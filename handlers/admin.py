import logging
import re
from aiogram import Router, F
from aiogram.types import CallbackQuery, Message
from aiogram.fsm.context import FSMContext
from aiogram.filters import Command

from states import AdminStates
from data.translations import t
from keyboards.builders import (
    admin_menu_keyboard, ref_list_keyboard, confirm_keyboard,
    main_menu_keyboard, yes_no_keyboard
)
from repositories.user_repo import (
    get_user, get_all_users, find_user_by_username,
    set_user_active, update_user_role, generate_invite_codes
)
from repositories.ref_repo import (
    get_projects, add_project, delete_project,
    get_subprojects, add_subproject, delete_subproject,
    get_structure_types, add_structure_type, delete_structure_type,
    get_defect_types, add_defect_type, delete_defect_type,
    get_pour_methods, add_pour_method, delete_pour_method,
    get_pump_types, add_pump_type, delete_pump_type,
)
from services.access_service import is_admin
from services.gpt_service import translate_term

logger = logging.getLogger(__name__)
router = Router()

ROLES = ["engineer", "senior", "admin"]


async def _get_lang(tg_id: int) -> str:
    user = await get_user(tg_id)
    return user["lang"] if user else "ru"


async def _admin_guard(callback: CallbackQuery) -> str | None:
    if not await is_admin(callback.from_user.id):
        await callback.answer(t("no_access", "ru"), show_alert=True)
        return None
    return await _get_lang(callback.from_user.id)


# ─── Commands ─────────────────────────────────────────────────────────────────

@router.message(Command("users"))
async def cmd_users(message: Message):
    if not await is_admin(message.from_user.id):
        return
    lang = await _get_lang(message.from_user.id)
    users = await get_all_users()
    if not users:
        await message.answer(t("list_empty", lang))
        return
    lines = [t("user_list_header", lang)]
    for u in users:
        role_icon = {"admin": "🔴", "senior": "🟡", "engineer": "🟢"}.get(u["role"], "⚪")
        active = "✅" if u["is_active"] else "🚫"
        lines.append(f"{active} {role_icon} @{u['username'] or '—'} | {u['full_name']} | {u['role']}")
    await message.answer("\n".join(lines))


@router.message(Command("block"))
async def cmd_block(message: Message):
    if not await is_admin(message.from_user.id):
        return
    lang = await _get_lang(message.from_user.id)
    parts = message.text.split()
    if len(parts) < 2:
        await message.answer("/block @username")
        return
    user = await find_user_by_username(parts[1])
    if not user:
        await message.answer(t("user_not_found", lang))
        return
    await set_user_active(user["telegram_id"], False)
    await message.answer(t("user_blocked", lang))


@router.message(Command("role"))
async def cmd_role(message: Message):
    if not await is_admin(message.from_user.id):
        return
    lang = await _get_lang(message.from_user.id)
    parts = message.text.split()
    if len(parts) < 3 or parts[2] not in ROLES:
        await message.answer(f"/role @username {'|'.join(ROLES)}")
        return
    user = await find_user_by_username(parts[1])
    if not user:
        await message.answer(t("user_not_found", lang))
        return
    await update_user_role(user["telegram_id"], parts[2])
    await message.answer(t("role_updated", lang))


@router.message(Command("gencode"))
async def cmd_gencode(message: Message):
    if not await is_admin(message.from_user.id):
        return
    lang = await _get_lang(message.from_user.id)
    parts = message.text.split()
    try:
        n = int(parts[1]) if len(parts) > 1 else 1
        n = max(1, min(n, 50))
    except ValueError:
        n = 1
    codes = await generate_invite_codes(message.from_user.id, n)
    code_text = "\n".join(f"<code>{c}</code>" for c in codes)
    await message.answer(
        t("codes_generated", lang, n=n, codes=code_text),
        parse_mode="HTML"
    )


# ─── Admin menu ───────────────────────────────────────────────────────────────

@router.callback_query(F.data == "admin:menu")
async def admin_menu(callback: CallbackQuery, state: FSMContext):
    lang = await _admin_guard(callback)
    if not lang:
        return
    await state.clear()
    await callback.message.edit_text(
        t("admin_menu", lang),
        reply_markup=admin_menu_keyboard(lang)
    )
    await callback.answer()


# ─── Invite codes via button ──────────────────────────────────────────────────

@router.callback_query(F.data == "admin:gencode")
async def admin_gencode(callback: CallbackQuery, state: FSMContext):
    lang = await _admin_guard(callback)
    if not lang:
        return
    await state.set_state(AdminStates.gencode_count)
    await callback.message.edit_text(t("gencode_how_many", lang))
    await callback.answer()


@router.message(AdminStates.gencode_count)
async def process_gencode_count(message: Message, state: FSMContext):
    lang = await _get_lang(message.from_user.id)
    try:
        n = max(1, min(int(message.text.strip()), 50))
    except ValueError:
        n = 1
    codes = await generate_invite_codes(message.from_user.id, n)
    code_text = "\n".join(f"<code>{c}</code>" for c in codes)
    await state.clear()
    await message.answer(
        t("codes_generated", lang, n=n, codes=code_text),
        parse_mode="HTML",
        reply_markup=admin_menu_keyboard(lang)
    )


# ─── Users management ─────────────────────────────────────────────────────────

@router.callback_query(F.data == "admin:users")
async def admin_users(callback: CallbackQuery, state: FSMContext):
    lang = await _admin_guard(callback)
    if not lang:
        return
    users = await get_all_users()
    if not users:
        await callback.message.edit_text(t("list_empty", lang))
        await callback.answer()
        return
    from aiogram.utils.keyboard import InlineKeyboardBuilder
    kb = InlineKeyboardBuilder()
    for u in users:
        role_icon = {"admin": "🔴", "senior": "🟡", "engineer": "🟢"}.get(u["role"], "⚪")
        active = "✅" if u["is_active"] else "🚫"
        label = f"{active}{role_icon} @{u['username'] or '—'} [{u['role']}]"
        kb.button(text=label, callback_data=f"admin_user:{u['telegram_id']}")
    kb.button(text=t("btn_back", lang), callback_data="admin:menu")
    kb.adjust(1)
    await callback.message.edit_text(t("user_list_header", lang), reply_markup=kb.as_markup())
    await callback.answer()


@router.callback_query(F.data.startswith("admin_user:"))
async def admin_user_detail(callback: CallbackQuery, state: FSMContext):
    lang = await _admin_guard(callback)
    if not lang:
        return
    uid = int(callback.data.split(":")[1])
    user = await get_user(uid)
    if not user:
        await callback.answer(t("user_not_found", lang), show_alert=True)
        return
    from aiogram.utils.keyboard import InlineKeyboardBuilder
    from aiogram.types import InlineKeyboardButton
    kb = InlineKeyboardBuilder()
    if user["is_active"]:
        kb.button(text="🚫 Блокировать / Block", callback_data=f"admin_block:{uid}")
    else:
        kb.button(text="✅ Разблокировать / Unblock", callback_data=f"admin_unblock:{uid}")
    for role in ROLES:
        if role != user["role"]:
            kb.button(text=f"→ {role}", callback_data=f"admin_setrole:{uid}:{role}")
    kb.button(text=t("btn_back", lang), callback_data="admin:users")
    kb.adjust(1)
    info = f"@{user['username'] or '—'}\n{user['full_name']}\nRole: {user['role']}\nActive: {bool(user['is_active'])}"
    await callback.message.edit_text(info, reply_markup=kb.as_markup())
    await callback.answer()


@router.callback_query(F.data.startswith("admin_block:"))
async def admin_block_user(callback: CallbackQuery):
    lang = await _admin_guard(callback)
    if not lang:
        return
    uid = int(callback.data.split(":")[1])
    await set_user_active(uid, False)
    await callback.answer(t("user_blocked", lang), show_alert=True)
    await admin_users(callback, None)


@router.callback_query(F.data.startswith("admin_unblock:"))
async def admin_unblock_user(callback: CallbackQuery):
    lang = await _admin_guard(callback)
    if not lang:
        return
    uid = int(callback.data.split(":")[1])
    await set_user_active(uid, True)
    await callback.answer(t("user_unblocked", lang), show_alert=True)
    await admin_users(callback, None)


@router.callback_query(F.data.startswith("admin_setrole:"))
async def admin_set_role(callback: CallbackQuery):
    lang = await _admin_guard(callback)
    if not lang:
        return
    parts = callback.data.split(":")
    uid, role = int(parts[1]), parts[2]
    await update_user_role(uid, role)
    await callback.answer(t("role_updated", lang), show_alert=True)
    await admin_users(callback, None)


# ─── Generic ref CRUD helpers ─────────────────────────────────────────────────

async def _show_ref_list(callback: CallbackQuery, lang: str, items, prefix: str, title_key: str):
    from aiogram.utils.keyboard import InlineKeyboardBuilder
    kb = InlineKeyboardBuilder()
    for item in items:
        try:
            name = item[f"name_{lang}"] or item["name_ru"]
        except (KeyError, IndexError):
            name = item.get("name", str(item["id"]))
        kb.button(text=f"❌ {name}", callback_data=f"{prefix}:del:{item['id']}")
    kb.button(text="➕ Добавить / Add", callback_data=f"{prefix}:add")
    kb.button(text=t("btn_back", lang), callback_data="admin:menu")
    kb.adjust(1)
    await callback.message.edit_text(t(title_key, lang), reply_markup=kb.as_markup())


async def _auto_translate_and_save(message: Message, state: FSMContext,
                                   save_fn, extra_state_key: str = None):
    lang = await _get_lang(message.from_user.id)
    name_ru = message.text.strip()
    await message.answer(t("translating_auto", lang))
    trans = await translate_term(name_ru)
    data = await state.get_data()

    confirm_text = t("confirm_translation", lang,
                     uz=trans.get("uz", name_ru),
                     en=trans.get("en", name_ru),
                     tr=trans.get("tr", name_ru))

    await state.update_data(
        pending_ru=name_ru,
        pending_uz=trans.get("uz", name_ru),
        pending_en=trans.get("en", name_ru),
        pending_tr=trans.get("tr", name_ru),
    )
    return name_ru, trans


# ─── Projects ─────────────────────────────────────────────────────────────────

@router.callback_query(F.data == "admin:projects")
async def admin_projects(callback: CallbackQuery, state: FSMContext):
    lang = await _admin_guard(callback)
    if not lang:
        return
    await state.clear()
    items = await get_projects()
    await _show_ref_list(callback, lang, items, "aproject", "btn_manage_projects")
    await callback.answer()


@router.callback_query(F.data == "aproject:add")
async def admin_add_project(callback: CallbackQuery, state: FSMContext):
    lang = await _admin_guard(callback)
    if not lang:
        return
    await state.set_state(AdminStates.adding_project)
    await callback.message.edit_text(t("enter_project_name", lang))
    await callback.answer()


@router.message(AdminStates.adding_project)
async def process_add_project(message: Message, state: FSMContext):
    lang = await _get_lang(message.from_user.id)
    await add_project(message.text.strip())
    await state.clear()
    await message.answer(t("project_added", lang), reply_markup=admin_menu_keyboard(lang))


@router.callback_query(F.data.startswith("aproject:del:"))
async def admin_del_project(callback: CallbackQuery, state: FSMContext):
    lang = await _admin_guard(callback)
    if not lang:
        return
    pid = int(callback.data.split(":")[2])
    await delete_project(pid)
    await callback.answer(t("deleted", lang), show_alert=True)
    items = await get_projects()
    await _show_ref_list(callback, lang, items, "aproject", "btn_manage_projects")


# ─── Subprojects ──────────────────────────────────────────────────────────────

@router.callback_query(F.data == "asubproject:add")
async def admin_add_subproject_choose_project(callback: CallbackQuery, state: FSMContext):
    lang = await _admin_guard(callback)
    if not lang:
        return
    projects = await get_projects()
    if not projects:
        await callback.message.edit_text(t("no_projects", lang))
        await callback.answer()
        return
    from aiogram.utils.keyboard import InlineKeyboardBuilder
    kb = InlineKeyboardBuilder()
    for p in projects:
        kb.button(text=p["name"], callback_data=f"asubproject:proj:{p['id']}")
    kb.button(text=t("btn_back", lang), callback_data="admin:menu")
    kb.adjust(1)
    await state.set_state(AdminStates.adding_subproject_project)
    await callback.message.edit_text(t("select_project_for_subproject", lang), reply_markup=kb.as_markup())
    await callback.answer()


@router.callback_query(AdminStates.adding_subproject_project, F.data.startswith("asubproject:proj:"))
async def admin_add_subproject_name(callback: CallbackQuery, state: FSMContext):
    lang = await _admin_guard(callback)
    if not lang:
        return
    pid = int(callback.data.split(":")[2])
    await state.update_data(sub_project_id=pid)
    await state.set_state(AdminStates.adding_subproject_name)
    await callback.message.edit_text(t("enter_subproject_name", lang))
    await callback.answer()


@router.message(AdminStates.adding_subproject_name)
async def process_add_subproject(message: Message, state: FSMContext):
    lang = await _get_lang(message.from_user.id)
    data = await state.get_data()
    await add_subproject(data["sub_project_id"], message.text.strip())
    await state.clear()
    await message.answer(t("subproject_added", lang), reply_markup=admin_menu_keyboard(lang))


# ─── Structure Types ──────────────────────────────────────────────────────────

@router.callback_query(F.data == "admin:structures")
async def admin_structures(callback: CallbackQuery, state: FSMContext):
    lang = await _admin_guard(callback)
    if not lang:
        return
    await state.clear()
    items = await get_structure_types()
    await _show_ref_list(callback, lang, items, "astruct", "btn_manage_structures")
    await callback.answer()


@router.callback_query(F.data == "astruct:add")
async def admin_add_structure(callback: CallbackQuery, state: FSMContext):
    lang = await _admin_guard(callback)
    if not lang:
        return
    await state.set_state(AdminStates.adding_structure_ru)
    await callback.message.edit_text(t("enter_name_ru", lang))
    await callback.answer()


@router.message(AdminStates.adding_structure_ru)
async def process_structure_ru(message: Message, state: FSMContext):
    lang = await _get_lang(message.from_user.id)
    name_ru = message.text.strip()
    await message.answer(t("translating_auto", lang))
    trans = await translate_term(name_ru)
    await state.update_data(pending_ru=name_ru,
                            pending_uz=trans.get("uz", name_ru),
                            pending_en=trans.get("en", name_ru),
                            pending_tr=trans.get("tr", name_ru))
    await state.set_state(AdminStates.adding_structure_icon)
    await message.answer(
        t("confirm_translation", lang,
          uz=trans.get("uz", name_ru), en=trans.get("en", name_ru), tr=trans.get("tr", name_ru)) +
        f"\n\n{t('enter_icon', lang)}"
    )


@router.message(AdminStates.adding_structure_icon)
async def process_structure_icon(message: Message, state: FSMContext):
    lang = await _get_lang(message.from_user.id)
    icon = message.text.strip()
    data = await state.get_data()
    import time; code = f"ST_{int(time.time())}"
    await add_structure_type(code, icon, data["pending_ru"], data["pending_uz"],
                             data["pending_en"], data["pending_tr"])
    await state.clear()
    await message.answer(t("saved", lang), reply_markup=admin_menu_keyboard(lang))


@router.callback_query(F.data.startswith("astruct:del:"))
async def admin_del_structure(callback: CallbackQuery):
    lang = await _admin_guard(callback)
    if not lang:
        return
    sid = int(callback.data.split(":")[2])
    await delete_structure_type(sid)
    await callback.answer(t("deleted", lang), show_alert=True)
    items = await get_structure_types()
    await _show_ref_list(callback, lang, items, "astruct", "btn_manage_structures")


# ─── Defect Types ──────────────────────────────────────────────────────────────

@router.callback_query(F.data == "admin:defects")
async def admin_defects(callback: CallbackQuery, state: FSMContext):
    lang = await _admin_guard(callback)
    if not lang:
        return
    await state.clear()
    items = await get_defect_types()
    await _show_ref_list(callback, lang, items, "adefect", "btn_manage_defects")
    await callback.answer()


@router.callback_query(F.data == "adefect:add")
async def admin_add_defect(callback: CallbackQuery, state: FSMContext):
    lang = await _admin_guard(callback)
    if not lang:
        return
    await state.set_state(AdminStates.adding_defect_ru)
    await callback.message.edit_text(t("enter_name_ru", lang))
    await callback.answer()


@router.message(AdminStates.adding_defect_ru)
async def process_defect_ru(message: Message, state: FSMContext):
    lang = await _get_lang(message.from_user.id)
    name_ru = message.text.strip()
    await message.answer(t("translating_auto", lang))
    trans = await translate_term(name_ru)
    import time; code = f"DEF_{int(time.time())}"
    await add_defect_type(code, name_ru, trans.get("uz", name_ru),
                          trans.get("en", name_ru), trans.get("tr", name_ru))
    await state.clear()
    await message.answer(t("saved", lang), reply_markup=admin_menu_keyboard(lang))


@router.callback_query(F.data.startswith("adefect:del:"))
async def admin_del_defect(callback: CallbackQuery):
    lang = await _admin_guard(callback)
    if not lang:
        return
    did = int(callback.data.split(":")[2])
    await delete_defect_type(did)
    await callback.answer(t("deleted", lang), show_alert=True)
    items = await get_defect_types()
    await _show_ref_list(callback, lang, items, "adefect", "btn_manage_defects")


# ─── Pour Methods ──────────────────────────────────────────────────────────────

@router.callback_query(F.data == "admin:pour")
async def admin_pour(callback: CallbackQuery, state: FSMContext):
    lang = await _admin_guard(callback)
    if not lang:
        return
    await state.clear()
    items = await get_pour_methods()
    await _show_ref_list(callback, lang, items, "apour", "btn_manage_pour")
    await callback.answer()


@router.callback_query(F.data == "apour:add")
async def admin_add_pour(callback: CallbackQuery, state: FSMContext):
    lang = await _admin_guard(callback)
    if not lang:
        return
    await state.set_state(AdminStates.adding_pour_ru)
    await callback.message.edit_text(t("enter_name_ru", lang))
    await callback.answer()


@router.message(AdminStates.adding_pour_ru)
async def process_pour_ru(message: Message, state: FSMContext):
    lang = await _get_lang(message.from_user.id)
    name_ru = message.text.strip()
    await message.answer(t("translating_auto", lang))
    trans = await translate_term(name_ru)
    await state.update_data(pending_ru=name_ru,
                            pending_uz=trans.get("uz", name_ru),
                            pending_en=trans.get("en", name_ru),
                            pending_tr=trans.get("tr", name_ru))
    await state.set_state(AdminStates.adding_pour_pump_flag)
    kb = yes_no_keyboard(lang, "pour_pump:yes", "pour_pump:no")
    await message.answer(t("requires_pump_yes", lang) + "?", reply_markup=kb)


@router.callback_query(AdminStates.adding_pour_pump_flag, F.data.startswith("pour_pump:"))
async def process_pour_pump_flag(callback: CallbackQuery, state: FSMContext):
    lang = await _admin_guard(callback)
    if not lang:
        return
    requires_pump = 1 if callback.data.endswith("yes") else 0
    data = await state.get_data()
    import time; code = f"PM_{int(time.time())}"
    await add_pour_method(code, "", data["pending_ru"], data["pending_uz"],
                          data["pending_en"], data["pending_tr"], requires_pump)
    await state.clear()
    await callback.message.edit_text(t("saved", lang), reply_markup=admin_menu_keyboard(lang))
    await callback.answer()


@router.callback_query(F.data.startswith("apour:del:"))
async def admin_del_pour(callback: CallbackQuery):
    lang = await _admin_guard(callback)
    if not lang:
        return
    pid = int(callback.data.split(":")[2])
    await delete_pour_method(pid)
    await callback.answer(t("deleted", lang), show_alert=True)
    items = await get_pour_methods()
    await _show_ref_list(callback, lang, items, "apour", "btn_manage_pour")


# ─── Pump Types ───────────────────────────────────────────────────────────────

@router.callback_query(F.data == "admin:pumps")
async def admin_pumps(callback: CallbackQuery, state: FSMContext):
    lang = await _admin_guard(callback)
    if not lang:
        return
    await state.clear()
    items = await get_pump_types()
    await _show_ref_list(callback, lang, items, "apump", "btn_manage_pumps")
    await callback.answer()


@router.callback_query(F.data == "apump:add")
async def admin_add_pump(callback: CallbackQuery, state: FSMContext):
    lang = await _admin_guard(callback)
    if not lang:
        return
    await state.set_state(AdminStates.adding_pump_ru)
    await callback.message.edit_text(t("enter_name_ru", lang))
    await callback.answer()


@router.message(AdminStates.adding_pump_ru)
async def process_pump_ru(message: Message, state: FSMContext):
    lang = await _get_lang(message.from_user.id)
    name_ru = message.text.strip()
    await message.answer(t("translating_auto", lang))
    trans = await translate_term(name_ru)
    import time; code = f"PT_{int(time.time())}"
    await add_pump_type(code, name_ru, trans.get("uz", name_ru),
                        trans.get("en", name_ru), trans.get("tr", name_ru))
    await state.clear()
    await message.answer(t("saved", lang), reply_markup=admin_menu_keyboard(lang))


@router.callback_query(F.data.startswith("apump:del:"))
async def admin_del_pump(callback: CallbackQuery):
    lang = await _admin_guard(callback)
    if not lang:
        return
    pid = int(callback.data.split(":")[2])
    await delete_pump_type(pid)
    await callback.answer(t("deleted", lang), show_alert=True)
    items = await get_pump_types()
    await _show_ref_list(callback, lang, items, "apump", "btn_manage_pumps")
