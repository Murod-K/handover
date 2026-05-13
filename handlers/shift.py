import logging
from aiogram import Router, F
from aiogram.types import CallbackQuery, Message
from aiogram.fsm.context import FSMContext

from states import ShiftStates
from data.translations import t
from keyboards.builders import (
    paginated_keyboard, shift_type_keyboard, natura_keyboard, rebar_keyboard,
    defects_keyboard, yes_no_keyboard, pump_logistics_keyboard,
    entry_finish_keyboard, skip_keyboard, main_menu_keyboard
)
from repositories.user_repo import get_user
from repositories.ref_repo import (
    get_projects, get_subprojects, get_structure_types,
    get_defect_types, get_pour_methods, get_pump_types, get_name
)
from repositories.shift_repo import create_shift, finish_shift, add_entry, add_entry_defect, get_last_shift
from services.access_service import check_access, is_admin, is_senior_or_above
from services.gpt_service import translate_comment, normalize_defect
from enums import NaturaStatus, RebarStatus, ConcretePlan

logger = logging.getLogger(__name__)
router = Router()


# ─── Guards ──────────────────────────────────────────────────────────────────

async def get_lang(tg_id: int) -> str:
    user = await get_user(tg_id)
    return user["lang"] if user else "ru"


async def guard(callback: CallbackQuery) -> str | None:
    """Check access, return lang or None."""
    allowed, _ = await check_access(callback.from_user.id)
    if not allowed:
        await callback.answer(t("no_access", "ru"), show_alert=True)
        return None
    return await get_lang(callback.from_user.id)


# ─── Cancel ──────────────────────────────────────────────────────────────────

@router.callback_query(F.data == "shift:cancel")
async def cancel_shift(callback: CallbackQuery, state: FSMContext):
    lang = await get_lang(callback.from_user.id)
    await state.clear()
    senior = await is_senior_or_above(callback.from_user.id)
    admin = await is_admin(callback.from_user.id)
    await callback.message.edit_text(
        t("shift_cancelled", lang),
        reply_markup=main_menu_keyboard(lang, senior, admin)
    )
    await callback.answer()


# ─── Start shift ─────────────────────────────────────────────────────────────

@router.callback_query(F.data == "shift:start")
async def start_shift(callback: CallbackQuery, state: FSMContext):
    lang = await guard(callback)
    if not lang:
        return
    await state.clear()
    projects = await get_projects()
    if not projects:
        await callback.message.edit_text(t("no_projects", lang))
        await callback.answer()
        return
    await state.set_state(ShiftStates.choosing_project)
    await callback.message.edit_text(
        t("choose_project", lang),
        reply_markup=paginated_keyboard(projects, "project", lang, name_field="name")
    )
    await callback.answer()


@router.callback_query(F.data.startswith("page:project:"))
async def paginate_projects(callback: CallbackQuery, state: FSMContext):
    lang = await guard(callback)
    if not lang:
        return
    page = int(callback.data.split(":")[2])
    projects = await get_projects()
    await callback.message.edit_reply_markup(
        reply_markup=paginated_keyboard(projects, "project", lang, name_field="name", page=page)
    )
    await callback.answer()


@router.callback_query(ShiftStates.choosing_project, F.data.startswith("project:"))
async def choose_project(callback: CallbackQuery, state: FSMContext):
    lang = await guard(callback)
    if not lang:
        return
    project_id = int(callback.data.split(":")[1])
    projects = await get_projects()
    proj = next((p for p in projects if p["id"] == project_id), None)
    await state.update_data(project_id=project_id, project_name=proj["name"] if proj else "")

    subs = await get_subprojects(project_id)
    await state.set_state(ShiftStates.choosing_subproject)
    await callback.message.edit_text(
        t("choose_subproject", lang),
        reply_markup=paginated_keyboard(subs, "subproject", lang, name_field="name")
    )
    await callback.answer()


@router.callback_query(ShiftStates.choosing_subproject, F.data.startswith("subproject:"))
async def choose_subproject(callback: CallbackQuery, state: FSMContext):
    lang = await guard(callback)
    if not lang:
        return
    sub_id = int(callback.data.split(":")[1])
    data = await state.get_data()
    subs = await get_subprojects(data["project_id"])
    sub = next((s for s in subs if s["id"] == sub_id), None)
    await state.update_data(subproject_id=sub_id, subproject_name=sub["name"] if sub else "")

    await state.set_state(ShiftStates.choosing_shift_type)
    await callback.message.edit_text(
        t("choose_shift_type", lang),
        reply_markup=shift_type_keyboard(lang)
    )
    await callback.answer()


@router.callback_query(ShiftStates.choosing_shift_type, F.data.startswith("shift_type:"))
async def choose_shift_type(callback: CallbackQuery, state: FSMContext):
    lang = await guard(callback)
    if not lang:
        return
    shift_type = callback.data.split(":")[1]
    data = await state.get_data()

    shift_id = await create_shift(
        callback.from_user.id,
        data["project_id"],
        data["subproject_id"],
        shift_type
    )
    await state.update_data(shift_id=shift_id, shift_type=shift_type, entries=[])
    await _ask_structure_type(callback, state, lang)
    await callback.answer()


# ─── "Like yesterday" ────────────────────────────────────────────────────────

@router.callback_query(F.data == "shift:repeat")
async def repeat_last_shift(callback: CallbackQuery, state: FSMContext):
    lang = await guard(callback)
    if not lang:
        return
    _, entries = await get_last_shift(callback.from_user.id)
    if not entries:
        await callback.message.edit_text(t("last_shift_not_found", lang))
        await callback.answer()
        return

    # Store entries as template in state then send to project selection
    await state.update_data(repeat_entries=entries)
    await start_shift(callback, state)  # reuse normal flow
    await callback.answer()


# ─── Entry loop ──────────────────────────────────────────────────────────────

async def _ask_structure_type(callback: CallbackQuery, state: FSMContext, lang: str):
    types = await get_structure_types()
    await state.set_state(ShiftStates.choosing_structure_type)
    await callback.message.edit_text(
        t("choose_structure_type", lang),
        reply_markup=paginated_keyboard(types, "struct", lang)
    )


@router.callback_query(ShiftStates.choosing_structure_type, F.data.startswith("struct:"))
async def choose_structure_type(callback: CallbackQuery, state: FSMContext):
    lang = await guard(callback)
    if not lang:
        return
    st_id = int(callback.data.split(":")[1])
    await state.update_data(
        current_entry={"structure_type_id": st_id, "defect_ids": [], "custom_defects": []}
    )
    await state.set_state(ShiftStates.entering_structure_name)
    await callback.message.edit_text(t("enter_structure_name", lang))
    await callback.answer()


@router.message(ShiftStates.entering_structure_name)
async def enter_structure_name(message: Message, state: FSMContext):
    lang = await get_lang(message.from_user.id)
    data = await state.get_data()
    entry = data.get("current_entry", {})
    entry["structure_name"] = message.text.strip()
    await state.update_data(current_entry=entry)
    await state.set_state(ShiftStates.choosing_natura)
    await message.answer(t("choose_natura", lang), reply_markup=natura_keyboard(lang))


@router.callback_query(ShiftStates.choosing_natura, F.data.startswith("natura:"))
async def choose_natura(callback: CallbackQuery, state: FSMContext):
    lang = await guard(callback)
    if not lang:
        return
    status = callback.data.split(":")[1]
    data = await state.get_data()
    entry = data.get("current_entry", {})
    entry["natura_status"] = status
    await state.update_data(current_entry=entry)
    await state.set_state(ShiftStates.choosing_rebar)
    await callback.message.edit_text(t("choose_rebar", lang), reply_markup=rebar_keyboard(lang))
    await callback.answer()


@router.callback_query(ShiftStates.choosing_rebar, F.data.startswith("rebar:"))
async def choose_rebar(callback: CallbackQuery, state: FSMContext):
    lang = await guard(callback)
    if not lang:
        return
    status = callback.data.split(":")[1]
    data = await state.get_data()
    entry = data.get("current_entry", {})
    entry["rebar_status"] = status
    await state.update_data(current_entry=entry)

    if status == RebarStatus.NOT_DONE:
        # Show defect selection
        defects = await get_defect_types()
        await state.set_state(ShiftStates.choosing_defects)
        await callback.message.edit_text(
            t("choose_defects", lang),
            reply_markup=defects_keyboard(lang, defects, entry.get("defect_ids", []))
        )
    else:
        await _ask_concrete(callback, state, lang, entry)
    await callback.answer()


@router.callback_query(ShiftStates.choosing_defects, F.data.startswith("defect:"))
async def choose_defect(callback: CallbackQuery, state: FSMContext):
    lang = await guard(callback)
    if not lang:
        return
    val = callback.data.split(":")[1]
    data = await state.get_data()
    entry = data.get("current_entry", {})

    if val == "done":
        await state.update_data(current_entry=entry)
        await _ask_concrete(callback, state, lang, entry)
    elif val == "custom":
        await state.set_state(ShiftStates.entering_custom_defect)
        await callback.message.edit_text(t("enter_custom_defect", lang))
    else:
        defect_id = int(val)
        ids = entry.get("defect_ids", [])
        if defect_id in ids:
            ids.remove(defect_id)
        else:
            ids.append(defect_id)
        entry["defect_ids"] = ids
        await state.update_data(current_entry=entry)
        defects = await get_defect_types()
        await callback.message.edit_reply_markup(
            reply_markup=defects_keyboard(lang, defects, ids)
        )
    await callback.answer()


@router.message(ShiftStates.entering_custom_defect)
async def enter_custom_defect(message: Message, state: FSMContext):
    lang = await get_lang(message.from_user.id)
    raw = message.text.strip()
    # Normalize via GPT
    ru_normalized = await normalize_defect(raw, lang)
    translations = await translate_comment(ru_normalized)
    data = await state.get_data()
    entry = data.get("current_entry", {})
    custom_defects = entry.get("custom_defects", [])
    custom_defects.append({
        "ru": ru_normalized,
        "uz": translations.get("uz", raw),
        "en": translations.get("en", raw),
        "tr": translations.get("tr", raw),
    })
    entry["custom_defects"] = custom_defects
    await state.update_data(current_entry=entry)

    defects = await get_defect_types()
    await state.set_state(ShiftStates.choosing_defects)
    await message.answer(
        t("choose_defects", lang),
        reply_markup=defects_keyboard(lang, defects, entry.get("defect_ids", []))
    )


async def _ask_concrete(callback: CallbackQuery, state: FSMContext, lang: str, entry: dict):
    await state.update_data(current_entry=entry)
    await state.set_state(ShiftStates.choosing_concrete_plan)
    await callback.message.edit_text(
        t("choose_concrete_plan", lang),
        reply_markup=yes_no_keyboard(lang, "concrete:yes", "concrete:no")
    )


@router.callback_query(ShiftStates.choosing_concrete_plan, F.data.startswith("concrete:"))
async def choose_concrete(callback: CallbackQuery, state: FSMContext):
    lang = await guard(callback)
    if not lang:
        return
    val = callback.data.split(":")[1]
    data = await state.get_data()
    entry = data.get("current_entry", {})

    if val == "no":
        entry["concrete_plan"] = ConcretePlan.NO
        await state.update_data(current_entry=entry)
        await _ask_comment(callback, state, lang)
    else:
        entry["concrete_plan"] = ConcretePlan.YES
        await state.update_data(current_entry=entry)
        # Check warnings
        warnings = []
        if entry.get("natura_status") == NaturaStatus.NOT_GIVEN:
            warnings.append(t("warn_natura_concrete", lang))
        if entry.get("rebar_status") == RebarStatus.NOT_DONE:
            warnings.append(t("warn_rebar_concrete", lang))
        if warnings:
            warn_text = "\n".join(f"⚠️ {w}" for w in warnings)
            entry["warnings"] = warnings
            await state.update_data(current_entry=entry)
            await callback.message.answer(warn_text)

        await state.set_state(ShiftStates.choosing_concrete_available)
        await callback.message.edit_text(
            t("concrete_ordered", lang),
            reply_markup=yes_no_keyboard(lang, "concrete_avail:yes", "concrete_avail:no")
        )
    await callback.answer()


@router.callback_query(ShiftStates.choosing_concrete_available, F.data.startswith("concrete_avail:"))
async def choose_concrete_available(callback: CallbackQuery, state: FSMContext):
    lang = await guard(callback)
    if not lang:
        return
    val = callback.data.split(":")[1]
    data = await state.get_data()
    entry = data.get("current_entry", {})
    entry["concrete_available"] = (val == "yes")
    await state.update_data(current_entry=entry)

    pour_methods = await get_pour_methods()
    await state.set_state(ShiftStates.choosing_pour_method)
    await callback.message.edit_text(
        t("choose_pour_method", lang),
        reply_markup=paginated_keyboard(pour_methods, "pour", lang)
    )
    await callback.answer()


@router.callback_query(ShiftStates.choosing_pour_method, F.data.startswith("pour:"))
async def choose_pour_method(callback: CallbackQuery, state: FSMContext):
    lang = await guard(callback)
    if not lang:
        return
    pm_id = int(callback.data.split(":")[1])
    pour_methods = await get_pour_methods()
    pm = next((p for p in pour_methods if p["id"] == pm_id), None)
    data = await state.get_data()
    entry = data.get("current_entry", {})
    entry["pour_method_id"] = pm_id
    await state.update_data(current_entry=entry)

    if pm and pm["requires_pump"]:
        pump_types = await get_pump_types()
        await state.set_state(ShiftStates.choosing_pump_type)
        await callback.message.edit_text(
            t("choose_pump_type", lang),
            reply_markup=paginated_keyboard(pump_types, "pump", lang)
        )
    else:
        await _ask_formwork(callback, state, lang, entry)
    await callback.answer()


@router.callback_query(ShiftStates.choosing_pump_type, F.data.startswith("pump:"))
async def choose_pump_type(callback: CallbackQuery, state: FSMContext):
    lang = await guard(callback)
    if not lang:
        return
    pt_id = int(callback.data.split(":")[1])
    data = await state.get_data()
    entry = data.get("current_entry", {})
    entry["pump_type_id"] = pt_id
    await state.update_data(current_entry=entry)
    await state.set_state(ShiftStates.choosing_pump_logistics)
    await callback.message.edit_text(
        t("choose_pump_logistics", lang),
        reply_markup=pump_logistics_keyboard(lang)
    )
    await callback.answer()


@router.callback_query(ShiftStates.choosing_pump_logistics, F.data.startswith("pump_log:"))
async def choose_pump_logistics(callback: CallbackQuery, state: FSMContext):
    lang = await guard(callback)
    if not lang:
        return
    logistics = callback.data.split(":")[1]
    data = await state.get_data()
    entry = data.get("current_entry", {})
    entry["pump_logistics"] = logistics
    await state.update_data(current_entry=entry)
    await state.set_state(ShiftStates.entering_concrete_volume)
    await callback.message.edit_text(t("enter_concrete_volume", lang))
    await callback.answer()


@router.message(ShiftStates.entering_concrete_volume)
async def enter_concrete_volume(message: Message, state: FSMContext):
    lang = await get_lang(message.from_user.id)
    try:
        vol = float(message.text.strip().replace(",", "."))
    except ValueError:
        await message.answer(t("volume_invalid", lang))
        return
    data = await state.get_data()
    entry = data.get("current_entry", {})
    entry["concrete_volume"] = vol
    await state.update_data(current_entry=entry)
    await state.set_state(ShiftStates.choosing_formwork_ready)
    # Reuse callback-style flow via message
    await message.answer(
        t("formwork_ready", lang),
        reply_markup=yes_no_keyboard(lang, "fw_ready:yes", "fw_ready:no")
    )


@router.callback_query(ShiftStates.choosing_formwork_ready, F.data.startswith("fw_ready:"))
async def choose_formwork_ready(callback: CallbackQuery, state: FSMContext):
    lang = await guard(callback)
    if not lang:
        return
    val = callback.data.split(":")[1]
    data = await state.get_data()
    entry = data.get("current_entry", {})
    entry["formwork_ready"] = (val == "yes")
    await state.update_data(current_entry=entry)
    await state.set_state(ShiftStates.choosing_waterproof_ready)
    await callback.message.edit_text(
        t("waterproof_ready", lang),
        reply_markup=yes_no_keyboard(lang, "wp_ready:yes", "wp_ready:no")
    )
    await callback.answer()


@router.callback_query(ShiftStates.choosing_waterproof_ready, F.data.startswith("wp_ready:"))
async def choose_waterproof_ready(callback: CallbackQuery, state: FSMContext):
    lang = await guard(callback)
    if not lang:
        return
    val = callback.data.split(":")[1]
    data = await state.get_data()
    entry = data.get("current_entry", {})
    entry["waterproof_ready"] = (val == "yes")
    await state.update_data(current_entry=entry)
    await state.set_state(ShiftStates.choosing_rebar_ready)
    await callback.message.edit_text(
        t("rebar_ready_for_pour", lang),
        reply_markup=yes_no_keyboard(lang, "rb_ready:yes", "rb_ready:no")
    )
    await callback.answer()


@router.callback_query(ShiftStates.choosing_rebar_ready, F.data.startswith("rb_ready:"))
async def choose_rebar_ready(callback: CallbackQuery, state: FSMContext):
    lang = await guard(callback)
    if not lang:
        return
    val = callback.data.split(":")[1]
    data = await state.get_data()
    entry = data.get("current_entry", {})
    entry["rebar_ready_for_pour"] = (val == "yes")
    await state.update_data(current_entry=entry)
    await _ask_comment(callback, state, lang)
    await callback.answer()


async def _ask_formwork(callback: CallbackQuery, state: FSMContext, lang: str, entry: dict):
    await state.update_data(current_entry=entry)
    await state.set_state(ShiftStates.entering_concrete_volume)
    await callback.message.edit_text(t("enter_concrete_volume", lang))


async def _ask_comment(callback: CallbackQuery, state: FSMContext, lang: str):
    await state.set_state(ShiftStates.entering_comment)
    await callback.message.edit_text(
        t("enter_comment", lang),
        reply_markup=skip_keyboard(lang)
    )


@router.callback_query(ShiftStates.entering_comment, F.data == "comment:skip")
async def skip_comment(callback: CallbackQuery, state: FSMContext):
    lang = await guard(callback)
    if not lang:
        return
    await _save_entry(callback, state, lang, comment_ru=None)
    await callback.answer()


@router.message(ShiftStates.entering_comment)
async def enter_comment(message: Message, state: FSMContext):
    lang = await get_lang(message.from_user.id)
    raw = message.text.strip()
    await message.answer(t("translating", lang))
    translations = await translate_comment(raw)

    comment_data = {
        "comment_ru": raw if lang == "ru" else translations.get("ru", raw),
        "comment_uz": raw if lang == "uz" else translations.get("uz", raw),
        "comment_en": raw if lang == "en" else translations.get("en", raw),
        "comment_tr": raw if lang == "tr" else translations.get("tr", raw),
    }
    # Fallback: keep original in user's lang
    comment_data[f"comment_{lang}"] = raw

    data = await state.get_data()
    entry = data.get("current_entry", {})
    entry.update(comment_data)
    await state.update_data(current_entry=entry)
    await _save_entry_from_message(message, state, lang)


async def _save_entry(callback: CallbackQuery, state: FSMContext, lang: str, comment_ru=None):
    data = await state.get_data()
    shift_id = data["shift_id"]
    entry = data.get("current_entry", {})
    entries_list = data.get("entries", [])

    entry_id = await add_entry(shift_id, entry)

    # Save defects
    for did in entry.get("defect_ids", []):
        await add_entry_defect(entry_id, did)
    for cd in entry.get("custom_defects", []):
        await add_entry_defect(entry_id, None,
                               custom_ru=cd.get("ru"), custom_uz=cd.get("uz"),
                               custom_en=cd.get("en"), custom_tr=cd.get("tr"))

    entries_list.append(entry_id)
    await state.update_data(entries=entries_list, current_entry={})

    count = len(entries_list)
    await callback.message.edit_text(
        t("entry_added", lang) + "\n\n" + t("shift_summary", lang, count=count),
        reply_markup=entry_finish_keyboard(lang)
    )


async def _save_entry_from_message(message: Message, state: FSMContext, lang: str):
    data = await state.get_data()
    shift_id = data["shift_id"]
    entry = data.get("current_entry", {})
    entries_list = data.get("entries", [])

    entry_id = await add_entry(shift_id, entry)
    for did in entry.get("defect_ids", []):
        await add_entry_defect(entry_id, did)
    for cd in entry.get("custom_defects", []):
        await add_entry_defect(entry_id, None,
                               custom_ru=cd.get("ru"), custom_uz=cd.get("uz"),
                               custom_en=cd.get("en"), custom_tr=cd.get("tr"))

    entries_list.append(entry_id)
    await state.update_data(entries=entries_list, current_entry={})

    count = len(entries_list)
    await message.answer(
        t("entry_added", lang) + "\n\n" + t("shift_summary", lang, count=count),
        reply_markup=entry_finish_keyboard(lang)
    )


# ─── Add more / Finish ───────────────────────────────────────────────────────

@router.callback_query(F.data == "entry:add_more")
async def add_more_entry(callback: CallbackQuery, state: FSMContext):
    lang = await guard(callback)
    if not lang:
        return
    await _ask_structure_type(callback, state, lang)
    await callback.answer()


@router.callback_query(F.data == "entry:finish")
async def finish_shift_handler(callback: CallbackQuery, state: FSMContext):
    lang = await guard(callback)
    if not lang:
        return
    data = await state.get_data()
    shift_id = data.get("shift_id")
    if shift_id:
        await finish_shift(shift_id)

    await state.clear()
    await callback.message.edit_text(t("generating_report", lang))

    # Trigger report generation
    from handlers.report import generate_and_send_report
    await generate_and_send_report(callback.message, callback.from_user.id, shift_id, lang)
    await callback.answer()
