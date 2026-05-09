from aiogram import Router, F
from aiogram.types import CallbackQuery
from aiogram.fsm.context import FSMContext

from data.translations import t
from keyboards.builders import list_kb, shift_type_kb, after_entry_kb
from repositories.user_repo import get_language
from repositories.ref_repo import get_all
from repositories.shift_repo import create_shift
from states import ShiftSG, EntrySG

router = Router()


@router.callback_query(F.data == "menu:new_shift")
async def on_new_shift(callback: CallbackQuery, state: FSMContext):
    lang = await get_language(callback.from_user.id)
    projects = await get_all("projects", lang)
    await callback.message.edit_text(
        t("select_project", lang),
        reply_markup=list_kb(projects, "proj", lang, back_cb="menu:main"),
        parse_mode="Markdown"
    )
    await state.set_state(ShiftSG.project)
    await callback.answer()


@router.callback_query(F.data.startswith("proj:"), ShiftSG.project)
async def on_project(callback: CallbackQuery, state: FSMContext):
    pid = int(callback.data.split(":")[1])
    lang = await get_language(callback.from_user.id)
    subprojects = await get_all("subprojects", lang, project_id=pid)
    await state.update_data(project_id=pid)
    await callback.message.edit_text(
        t("select_subproject", lang),
        reply_markup=list_kb(subprojects, "sub", lang, back_cb="menu:new_shift"),
        parse_mode="Markdown"
    )
    await state.set_state(ShiftSG.subproject)
    await callback.answer()


@router.callback_query(F.data.startswith("sub:"), ShiftSG.subproject)
async def on_subproject(callback: CallbackQuery, state: FSMContext):
    sid = int(callback.data.split(":")[1])
    lang = await get_language(callback.from_user.id)
    await state.update_data(subproject_id=sid)
    await callback.message.edit_text(
        t("select_shift_type", lang),
        reply_markup=shift_type_kb(lang),
        parse_mode="Markdown"
    )
    await state.set_state(ShiftSG.shift_type)
    await callback.answer()


@router.callback_query(F.data.startswith("shift_type:"), ShiftSG.shift_type)
async def on_shift_type(callback: CallbackQuery, state: FSMContext):
    shift_type = callback.data.split(":")[1]
    lang = await get_language(callback.from_user.id)
    data = await state.get_data()

    shift_id = await create_shift(
        callback.from_user.id,
        data["project_id"],
        data["subproject_id"],
        shift_type
    )
    await state.update_data(shift_id=shift_id)

    # Jump directly to structure type
    from repositories.ref_repo import get_all as ga
    structs = await ga("structure_types", lang)
    await callback.message.edit_text(
        t("shift_open", lang) + "\n\n" + t("select_structure_type", lang),
        reply_markup=list_kb(structs, "struct", lang),
        parse_mode="Markdown"
    )
    await state.set_state(EntrySG.structure_type)
    await callback.answer()
