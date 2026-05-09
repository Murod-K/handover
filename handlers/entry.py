from aiogram import Router, F
from aiogram.types import CallbackQuery, Message
from aiogram.fsm.context import FSMContext

from data.translations import t
from keyboards.builders import (
    natura_kb, rebar_kb, defects_kb, concrete_kb,
    pour_methods_kb, pump_types_kb, pump_logistics_kb,
    ready_kb, after_entry_kb, list_kb
)
from repositories.user_repo import get_language
from repositories.ref_repo import get_all, get_item
from repositories.shift_repo import create_entry, add_defects, delete_last_entry
from services.translation_service import translate_comment
from states import EntrySG

router = Router()


def _reset_entry(data: dict) -> dict:
    keys = [
        "structure_type_id", "structure_name", "natura_status",
        "rebar_status", "selected_defects", "concrete_plan",
        "pour_method_id", "pump_type_id", "pump_logistics",
        "concrete_volume", "formwork_ready", "waterproof_ready",
        "rebar_ready_for_pour", "comment"
    ]
    for k in keys:
        data[k] = None
    data["selected_defects"] = []
    return data


# ── STRUCTURE TYPE ──

@router.callback_query(F.data.startswith("struct:"), EntrySG.structure_type)
async def on_struct_type(callback: CallbackQuery, state: FSMContext):
    sid = int(callback.data.split(":")[1])
    lang = await get_language(callback.from_user.id)
    await state.update_data(structure_type_id=sid)
    await callback.message.edit_text(t("enter_structure_name", lang), parse_mode="Markdown")
    await state.set_state(EntrySG.structure_name)
    await callback.answer()


@router.message(EntrySG.structure_name)
async def on_struct_name(message: Message, state: FSMContext):
    lang = await get_language(message.from_user.id)
    await state.update_data(structure_name=message.text.strip())
    await message.answer(t("select_natura", lang), reply_markup=natura_kb(lang), parse_mode="Markdown")
    await state.set_state(EntrySG.natura)


# ── NATURA ──

@router.callback_query(F.data.startswith("natura:"), EntrySG.natura)
async def on_natura(callback: CallbackQuery, state: FSMContext):
    natura = callback.data.split(":")[1]
    lang = await get_language(callback.from_user.id)
    await state.update_data(natura_status=natura)

    warn = ""
    if natura == "NATURA_NOT_GIVEN":
        warn = f"\n\n{t('warn_natura_not_given', lang)}"
    elif natura == "NATURA_WILL_BE_NIGHT":
        warn = f"\n\n{t('warn_natura_night', lang)}"

    await callback.message.edit_text(
        t("select_rebar", lang) + warn,
        reply_markup=rebar_kb(lang), parse_mode="Markdown"
    )
    await state.set_state(EntrySG.rebar)
    await callback.answer()


# ── REBAR ──

@router.callback_query(F.data.startswith("rebar:"), EntrySG.rebar)
async def on_rebar(callback: CallbackQuery, state: FSMContext):
    rebar = callback.data.split(":")[1]
    lang = await get_language(callback.from_user.id)
    await state.update_data(rebar_status=rebar, selected_defects=[])

    if rebar != "REBAR_ACCEPTED":
        defects = await get_all("defect_types", lang)
        await callback.message.edit_text(
            t("select_defects", lang),
            reply_markup=defects_kb(defects, [], lang),
            parse_mode="Markdown"
        )
        await state.set_state(EntrySG.defects)
    else:
        # Skip defects → go to concrete
        await callback.message.edit_text(
            t("select_concrete", lang),
            reply_markup=concrete_kb(lang), parse_mode="Markdown"
        )
        await state.set_state(EntrySG.concrete)
    await callback.answer()


# ── DEFECTS ──

@router.callback_query(F.data.startswith("defect:"), EntrySG.defects)
async def on_defect(callback: CallbackQuery, state: FSMContext):
    val = callback.data.split(":")[1]
    lang = await get_language(callback.from_user.id)

    if val == "DONE":
        # Check if CUSTOM selected — ask for text
        data = await state.get_data()
        selected = data.get("selected_defects", [])
        defects = await get_all("defect_types", lang)
        custom_item = next((d for d in defects if d.get("name_ru","").startswith("✏️")), None)
        # Find CUSTOM id
        all_defects_full = await get_all("defect_types", "ru")
        custom_id = next((d["id"] for d in all_defects_full
                          if "CUSTOM" in str(d.get("id","")) or d.get("name_ru","").startswith("✏️")), None)

        if custom_id and custom_id in selected:
            await callback.message.edit_text(
                t("enter_defect_custom", lang), parse_mode="Markdown"
            )
            await state.set_state(EntrySG.defect_custom)
        else:
            await callback.message.edit_text(
                t("select_concrete", lang),
                reply_markup=concrete_kb(lang), parse_mode="Markdown"
            )
            await state.set_state(EntrySG.concrete)
        await callback.answer()
        return

    # Toggle
    defect_id = int(val)
    data = await state.get_data()
    selected = list(data.get("selected_defects", []))
    if defect_id in selected:
        selected.remove(defect_id)
    else:
        selected.append(defect_id)
    await state.update_data(selected_defects=selected)

    defects = await get_all("defect_types", lang)
    await callback.message.edit_reply_markup(
        reply_markup=defects_kb(defects, selected, lang)
    )
    await callback.answer()


@router.message(EntrySG.defect_custom)
async def on_defect_custom(message: Message, state: FSMContext):
    lang = await get_language(message.from_user.id)
    await state.update_data(defect_custom_text=message.text.strip())
    await message.answer(
        t("select_concrete", lang),
        reply_markup=concrete_kb(lang), parse_mode="Markdown"
    )
    await state.set_state(EntrySG.concrete)


# ── CONCRETE ──

@router.callback_query(F.data.startswith("concrete:"), EntrySG.concrete)
async def on_concrete(callback: CallbackQuery, state: FSMContext):
    plan = callback.data.split(":")[1]
    lang = await get_language(callback.from_user.id)
    data = await state.get_data()
    await state.update_data(concrete_plan=plan)

    if plan == "NO_POUR":
        await _save_and_show_menu(callback, state, lang)
        return

    # Check blockers
    warns = []
    if data.get("natura_status") == "NATURA_NOT_GIVEN":
        warns.append(t("warn_natura_not_given", lang))
    if data.get("rebar_status") == "REBAR_NOT_ACCEPTED":
        warns.append(t("warn_rebar_blocks", lang))

    warn_text = ("\n\n" + "\n".join(warns)) if warns else ""

    methods = await get_all("pour_methods", lang)
    await callback.message.edit_text(
        t("select_pour_method", lang) + warn_text,
        reply_markup=pour_methods_kb(methods, lang), parse_mode="Markdown"
    )
    await state.set_state(EntrySG.pour_method)
    await callback.answer()


# ── POUR METHOD ──

@router.callback_query(F.data.startswith("pour:"), EntrySG.pour_method)
async def on_pour_method(callback: CallbackQuery, state: FSMContext):
    pm_id = int(callback.data.split(":")[1])
    lang = await get_language(callback.from_user.id)
    pm = await get_item("pour_methods", pm_id)
    await state.update_data(pour_method_id=pm_id)

    if pm and pm.get("requires_pump"):
        pumps = await get_all("pump_types", lang)
        await callback.message.edit_text(
            t("select_pump_type", lang),
            reply_markup=pump_types_kb(pumps, lang), parse_mode="Markdown"
        )
        await state.set_state(EntrySG.pump_type)
    else:
        await state.update_data(pump_type_id=None, pump_logistics=None)
        await callback.message.edit_text(
            t("enter_volume", lang), parse_mode="Markdown"
        )
        await state.set_state(EntrySG.volume)
    await callback.answer()


# ── PUMP TYPE ──

@router.callback_query(F.data.startswith("pump:"), EntrySG.pump_type)
async def on_pump_type(callback: CallbackQuery, state: FSMContext):
    pt_id = int(callback.data.split(":")[1])
    lang = await get_language(callback.from_user.id)
    await state.update_data(pump_type_id=pt_id)
    await callback.message.edit_text(
        t("select_pump_logistics", lang),
        reply_markup=pump_logistics_kb(lang), parse_mode="Markdown"
    )
    await state.set_state(EntrySG.pump_logistics)
    await callback.answer()


# ── PUMP LOGISTICS ──

@router.callback_query(F.data.startswith("logistics:"), EntrySG.pump_logistics)
async def on_logistics(callback: CallbackQuery, state: FSMContext):
    logistics = callback.data.split(":")[1]
    lang = await get_language(callback.from_user.id)
    await state.update_data(pump_logistics=logistics)
    await callback.message.edit_text(
        t("enter_volume", lang), parse_mode="Markdown"
    )
    await state.set_state(EntrySG.volume)
    await callback.answer()


# ── VOLUME ──

@router.message(EntrySG.volume)
async def on_volume(message: Message, state: FSMContext):
    lang = await get_language(message.from_user.id)
    text = message.text.strip().replace(",", ".")
    try:
        vol = float(text)
        if vol <= 0:
            raise ValueError
    except ValueError:
        await message.answer(t("invalid_volume", lang))
        return

    await state.update_data(concrete_volume=vol)
    await message.answer(
        t("enter_comment", lang), parse_mode="Markdown"
    )
    await state.set_state(EntrySG.comment)


# ── COMMENT ──

@router.message(EntrySG.comment)
async def on_comment(message: Message, state: FSMContext):
    lang = await get_language(message.from_user.id)
    text = message.text.strip()
    if text.lower() in ("/skip", "skip"):
        await state.update_data(comment=None)
    else:
        await state.update_data(comment=text)
    await _save_and_show_menu(message, state, lang)


# ── SAVE & MENU ──

async def _save_and_show_menu(obj, state: FSMContext, lang: str):
    data = await state.get_data()

    # Translate comment
    comment_translations = {"ru": None, "uz": None, "en": None, "tr": None}
    raw_comment = data.get("comment")
    if raw_comment:
        comment_translations = await translate_comment(raw_comment, lang)

    entry_data = {
        "shift_id":             data["shift_id"],
        "structure_type_id":    data.get("structure_type_id"),
        "structure_name":       data.get("structure_name"),
        "natura_status":        data.get("natura_status"),
        "rebar_status":         data.get("rebar_status"),
        "concrete_plan":        data.get("concrete_plan"),
        "pour_method_id":       data.get("pour_method_id"),
        "pump_type_id":         data.get("pump_type_id"),
        "pump_logistics":       data.get("pump_logistics"),
        "concrete_volume":      data.get("concrete_volume"),
        "formwork_ready":       data.get("formwork_ready"),
        "waterproof_ready":     data.get("waterproof_ready"),
        "rebar_ready_for_pour": data.get("rebar_ready_for_pour"),
        "comment":              raw_comment,
        "comment_ru":           comment_translations.get("ru"),
        "comment_uz":           comment_translations.get("uz"),
        "comment_en":           comment_translations.get("en"),
        "comment_tr":           comment_translations.get("tr"),
    }
    entry_id = await create_entry(entry_data)

    # Save defects
    selected = data.get("selected_defects", [])
    if selected:
        custom_text = data.get("defect_custom_text")
        defect_pairs = [
            (d_id, custom_text if d_id == selected[-1] and custom_text else None)
            for d_id in selected
        ]
        await add_defects(entry_id, defect_pairs)

    # Reset entry state, keep shift_id
    shift_id = data["shift_id"]
    await state.update_data(**_reset_entry({}), shift_id=shift_id)

    text = t("entry_saved", lang) + "\n\n" + t("entry_menu", lang)
    kb = after_entry_kb(lang)
    if isinstance(obj, CallbackQuery):
        try:
            await obj.message.edit_text(text, reply_markup=kb, parse_mode="Markdown")
        except Exception:
            await obj.message.answer(text, reply_markup=kb, parse_mode="Markdown")
        await obj.answer()
    else:
        await obj.answer(text, reply_markup=kb, parse_mode="Markdown")

    await state.set_state(EntrySG.entry_done)


# ── AFTER ENTRY ACTIONS ──

@router.callback_query(F.data == "entry:add_more")
async def on_add_more(callback: CallbackQuery, state: FSMContext):
    lang = await get_language(callback.from_user.id)
    structs = await get_all("structure_types", lang)
    await callback.message.edit_text(
        t("select_structure_type", lang),
        reply_markup=list_kb(structs, "struct", lang),
        parse_mode="Markdown"
    )
    await state.set_state(EntrySG.structure_type)
    await callback.answer()


@router.callback_query(F.data == "entry:cancel_last")
async def on_cancel_last(callback: CallbackQuery, state: FSMContext):
    lang = await get_language(callback.from_user.id)
    data = await state.get_data()
    deleted = await delete_last_entry(data["shift_id"])
    msg = "✅ Последняя конструкция удалена." if deleted else "⚠️ Нечего удалять."
    await callback.answer(msg, show_alert=True)


@router.callback_query(F.data == "entry:finish")
async def on_finish(callback: CallbackQuery, state: FSMContext):
    from handlers.report import send_report
    await send_report(callback, state)
