from aiogram import Router, F
from aiogram.types import CallbackQuery, Message
from aiogram.fsm.context import FSMContext

from data.translations import t
from keyboards.builders import projects_keyboard, subprojects_keyboard, shift_type_keyboard
from repositories.project_repo import get_projects, get_subprojects
from repositories.user_repo import get_language
from states import ProjectStates, ShiftStates

router = Router()


async def show_projects(message: Message, lang: str):
    projects = await get_projects()
    if not projects:
        await message.answer(t("no_projects", lang))
        return
    await message.answer(
        t("select_project", lang),
        reply_markup=projects_keyboard(projects)
    )


@router.callback_query(F.data.startswith("project:"))
async def on_project_chosen(callback: CallbackQuery, state: FSMContext):
    project_id = int(callback.data.split(":")[1])
    lang = await get_language(callback.from_user.id)

    await state.update_data(project_id=project_id)

    subprojects = await get_subprojects(project_id)
    await callback.message.edit_text(
        t("select_subproject", lang),
        reply_markup=subprojects_keyboard(subprojects)
    )
    await state.set_state(ProjectStates.choosing_subproject)
    await callback.answer()


@router.callback_query(F.data.startswith("subproject:"))
async def on_subproject_chosen(callback: CallbackQuery, state: FSMContext):
    subproject_id = int(callback.data.split(":")[1])
    lang = await get_language(callback.from_user.id)

    await state.update_data(subproject_id=subproject_id)

    await callback.message.edit_text(
        t("select_shift", lang),
        reply_markup=shift_type_keyboard(lang)
    )
    await state.set_state(ShiftStates.choosing_shift_type)
    await callback.answer()
