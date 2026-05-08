from aiogram import Router, F
from aiogram.types import CallbackQuery
from aiogram.fsm.context import FSMContext

from data.translations import t
from keyboards.builders import after_entry_keyboard, structure_type_keyboard
from repositories.user_repo import get_language
from repositories.shift_repo import create_shift
from states import ShiftStates, EntryStates

router = Router()


@router.callback_query(F.data.startswith("shift_type:"))
async def on_shift_type_chosen(callback: CallbackQuery, state: FSMContext):
    shift_type = callback.data.split(":")[1]
    lang = await get_language(callback.from_user.id)
    data = await state.get_data()

    shift_id = await create_shift(
        telegram_id=callback.from_user.id,
        project_id=data["project_id"],
        subproject_id=data["subproject_id"],
        shift_type=shift_type
    )
    await state.update_data(shift_id=shift_id, entries=[])

    await callback.message.edit_text(
        t("shift_started", lang),
        reply_markup=structure_type_keyboard(lang)
    )
    await state.set_state(EntryStates.choosing_structure_type)
    await callback.answer()


@router.callback_query(F.data == "entry:add_more")
async def on_add_more_structure(callback: CallbackQuery, state: FSMContext):
    lang = await get_language(callback.from_user.id)
    # Reset entry-specific data
    await state.update_data(
        structure_type=None, structure_name=None,
        natura_status=None, rebar_status=None,
        selected_defects=[], rebar_comment=None,
        concrete_plan=None, concrete_available=None,
        formwork_ready=None, waterproof_ready=None,
        rebar_ready_for_pour=None, concrete_volume=None,
        pour_method=None, pump_type=None, pump_logistics=None,
        entry_comment=None
    )
    await callback.message.edit_text(
        t("select_structure_type", lang),
        reply_markup=structure_type_keyboard(lang)
    )
    await state.set_state(EntryStates.choosing_structure_type)
    await callback.answer()
