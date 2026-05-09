from aiogram import Router, F
from aiogram.types import CallbackQuery, Message
from aiogram.fsm.context import FSMContext

from data.translations import t
from keyboards.builders import (
    admin_menu_kb, ref_list_admin_kb, confirm_del_kb,
    projects_admin_kb, project_detail_kb
)
from repositories.user_repo import get_language, get_role
from repositories.ref_repo import (
    get_all, get_item, delete_item,
    add_project, add_subproject, add_ref_item, get_all as ref_get_all
)
from states import AdminSG

router = Router()

REF_TABLES = {
    "structures":   ("structure_types", "Типы конструкций"),
    "defects":      ("defect_types",    "Дефекты"),
    "pour_methods": ("pour_methods",    "Способы подачи"),
    "pump_types":   ("pump_types",      "Типы насосов"),
}


async def _check_admin(callback: CallbackQuery) -> bool:
    role = await get_role(callback.from_user.id)
    if role != "admin":
        await callback.answer(t("access_denied", "ru"), show_alert=True)
        return False
    return True


@router.callback_query(F.data == "menu:admin")
async def on_admin(callback: CallbackQuery, state: FSMContext):
    if not await _check_admin(callback):
        return
    lang = await get_language(callback.from_user.id)
    await callback.message.edit_text(
        t("admin_menu", lang), reply_markup=admin_menu_kb(lang), parse_mode="Markdown"
    )
    await state.set_state(AdminSG.menu)
    await callback.answer()


# ── PROJECTS ──

@router.callback_query(F.data == "admin:projects")
async def on_admin_projects(callback: CallbackQuery, state: FSMContext):
    if not await _check_admin(callback):
        return
    lang = await get_language(callback.from_user.id)
    projects = await get_all("projects", lang)
    await callback.message.edit_text(
        "📁 *Объекты:*",
        reply_markup=projects_admin_kb(projects, lang),
        parse_mode="Markdown"
    )
    await state.set_state(AdminSG.projects_list)
    await callback.answer()


@router.callback_query(F.data.startswith("proj_detail:"))
async def on_proj_detail(callback: CallbackQuery, state: FSMContext):
    if not await _check_admin(callback):
        return
    pid = int(callback.data.split(":")[1])
    lang = await get_language(callback.from_user.id)
    proj = await get_item("projects", pid)
    subs = await get_all("subprojects", lang, project_id=pid)
    await state.update_data(current_project_id=pid)
    await callback.message.edit_text(
        f"📁 *{proj['name']}*\nПодобъекты:",
        reply_markup=project_detail_kb(pid, subs, lang),
        parse_mode="Markdown"
    )
    await state.set_state(AdminSG.project_detail)
    await callback.answer()


@router.callback_query(F.data == "add_project")
async def on_add_project(callback: CallbackQuery, state: FSMContext):
    if not await _check_admin(callback):
        return
    lang = await get_language(callback.from_user.id)
    await callback.message.edit_text("✏️ Введите название нового объекта:")
    await state.set_state(AdminSG.add_project)
    await callback.answer()


@router.message(AdminSG.add_project)
async def on_project_name(message: Message, state: FSMContext):
    lang = await get_language(message.from_user.id)
    await add_project(message.text.strip())
    await message.answer(t("item_added", lang))
    # Refresh list
    projects = await get_all("projects", lang)
    await message.answer("📁 *Объекты:*", reply_markup=projects_admin_kb(projects, lang), parse_mode="Markdown")
    await state.set_state(AdminSG.projects_list)


@router.callback_query(F.data.startswith("add_subproject:"))
async def on_add_subproject_start(callback: CallbackQuery, state: FSMContext):
    pid = int(callback.data.split(":")[1])
    await state.update_data(current_project_id=pid)
    await callback.message.edit_text("✏️ Введите название подобъекта / блока:")
    await state.set_state(AdminSG.add_subproject)
    await callback.answer()


@router.message(AdminSG.add_subproject)
async def on_subproject_name(message: Message, state: FSMContext):
    lang = await get_language(message.from_user.id)
    data = await state.get_data()
    pid = data["current_project_id"]
    await add_subproject(pid, message.text.strip())
    await message.answer(t("item_added", lang))
    proj = await get_item("projects", pid)
    subs = await get_all("subprojects", lang, project_id=pid)
    await message.answer(
        f"📁 *{proj['name']}*\nПодобъекты:",
        reply_markup=project_detail_kb(pid, subs, lang),
        parse_mode="Markdown"
    )
    await state.set_state(AdminSG.project_detail)


@router.callback_query(F.data.startswith("del_project:"))
async def on_del_project(callback: CallbackQuery, state: FSMContext):
    pid = int(callback.data.split(":")[1])
    lang = await get_language(callback.from_user.id)
    await state.update_data(del_table="projects", del_id=pid)
    proj = await get_item("projects", pid)
    await callback.message.edit_text(
        f"{t('confirm_delete', lang)}\n*{proj['name']}*",
        reply_markup=confirm_del_kb(lang, "confirm_del:yes"),
        parse_mode="Markdown"
    )
    await state.set_state(AdminSG.ref_confirm_del)
    await callback.answer()


@router.callback_query(F.data.startswith("del_subproject:"))
async def on_del_subproject(callback: CallbackQuery, state: FSMContext):
    sid = int(callback.data.split(":")[1])
    lang = await get_language(callback.from_user.id)
    await state.update_data(del_table="subprojects", del_id=sid)
    item = await get_item("subprojects", sid)
    await callback.message.edit_text(
        f"{t('confirm_delete', lang)}\n*{item['name']}*",
        reply_markup=confirm_del_kb(lang, "confirm_del:yes"),
        parse_mode="Markdown"
    )
    await state.set_state(AdminSG.ref_confirm_del)
    await callback.answer()


# ── REFERENCE TABLES (structures, defects, pour_methods, pump_types) ──

@router.callback_query(F.data.startswith("admin:"), AdminSG.menu)
async def on_admin_ref(callback: CallbackQuery, state: FSMContext):
    if not await _check_admin(callback):
        return
    key = callback.data.split(":")[1]
    if key not in REF_TABLES:
        await callback.answer()
        return
    lang = await get_language(callback.from_user.id)
    table, title = REF_TABLES[key]
    items = await get_all(table, lang)
    await state.update_data(current_table=table, current_table_key=key)
    await callback.message.edit_text(
        f"*{title}:*",
        reply_markup=ref_list_admin_kb(items, table, lang, back_cb="admin:back"),
        parse_mode="Markdown"
    )
    await state.set_state(AdminSG.ref_list)
    await callback.answer()


@router.callback_query(F.data.startswith("del_") , AdminSG.ref_list)
async def on_del_ref_item(callback: CallbackQuery, state: FSMContext):
    parts = callback.data.split(":")
    table = parts[0].replace("del_", "")
    item_id = int(parts[1])
    lang = await get_language(callback.from_user.id)
    await state.update_data(del_table=table, del_id=item_id)
    item = await get_item(table, item_id)
    name = item.get(f"name_{lang}") or item.get("name_ru") or item.get("name") or "?"
    await callback.message.edit_text(
        f"{t('confirm_delete', lang)}\n*{name}*",
        reply_markup=confirm_del_kb(lang, "confirm_del:yes"),
        parse_mode="Markdown"
    )
    await state.set_state(AdminSG.ref_confirm_del)
    await callback.answer()


@router.callback_query(F.data == "confirm_del:yes", AdminSG.ref_confirm_del)
async def on_confirm_del(callback: CallbackQuery, state: FSMContext):
    lang = await get_language(callback.from_user.id)
    data = await state.get_data()
    await delete_item(data["del_table"], data["del_id"])
    await callback.answer(t("item_deleted", lang), show_alert=True)
    # Go back to admin menu
    await callback.message.edit_text(
        t("admin_menu", lang), reply_markup=admin_menu_kb(lang), parse_mode="Markdown"
    )
    await state.set_state(AdminSG.menu)


@router.callback_query(F.data.startswith("add_"), AdminSG.ref_list)
async def on_add_ref(callback: CallbackQuery, state: FSMContext):
    lang = await get_language(callback.from_user.id)
    await callback.message.edit_text(t("enter_name_ru", lang))
    await state.set_state(AdminSG.ref_add_ru)
    await callback.answer()


@router.message(AdminSG.ref_add_ru)
async def on_ref_name_ru(message: Message, state: FSMContext):
    await state.update_data(new_name_ru=message.text.strip())
    await message.answer("✏️ Ўзбекча номи (yoki /skip):")
    await state.set_state(AdminSG.ref_add_uz)


@router.message(AdminSG.ref_add_uz)
async def on_ref_name_uz(message: Message, state: FSMContext):
    val = None if message.text.strip().lower() in ("/skip", "skip") else message.text.strip()
    await state.update_data(new_name_uz=val)
    await message.answer("✏️ English name (or /skip):")
    await state.set_state(AdminSG.ref_add_en)


@router.message(AdminSG.ref_add_en)
async def on_ref_name_en(message: Message, state: FSMContext):
    val = None if message.text.strip().lower() in ("/skip", "skip") else message.text.strip()
    await state.update_data(new_name_en=val)
    await message.answer("✏️ Türkçe adı (veya /skip):")
    await state.set_state(AdminSG.ref_add_tr)


@router.message(AdminSG.ref_add_tr)
async def on_ref_name_tr(message: Message, state: FSMContext):
    lang = await get_language(message.from_user.id)
    val = None if message.text.strip().lower() in ("/skip", "skip") else message.text.strip()
    data = await state.get_data()
    table = data["current_table"]

    import re, time
    code = re.sub(r"[^A-Z0-9_]", "", data["new_name_ru"].upper().replace(" ", "_"))[:20]
    code = f"{code}_{int(time.time()) % 10000}"

    await add_ref_item(
        table, code,
        data["new_name_ru"], data.get("new_name_uz"),
        data.get("new_name_en"), val
    )
    await message.answer(t("item_added", lang))

    items = await get_all(table, lang)
    key = data["current_table_key"]
    _, title = REF_TABLES[key]
    await message.answer(
        f"*{title}:*",
        reply_markup=ref_list_admin_kb(items, table, lang, back_cb="admin:back"),
        parse_mode="Markdown"
    )
    await state.set_state(AdminSG.ref_list)


@router.callback_query(F.data == "admin:back")
async def on_admin_back(callback: CallbackQuery, state: FSMContext):
    lang = await get_language(callback.from_user.id)
    await callback.message.edit_text(
        t("admin_menu", lang), reply_markup=admin_menu_kb(lang), parse_mode="Markdown"
    )
    await state.set_state(AdminSG.menu)
    await callback.answer()
