from aiogram import Router, F
from aiogram.types import CallbackQuery
from aiogram.fsm.context import FSMContext

from data.translations import t
from keyboards.builders import pump_type_keyboard, pump_logistics_keyboard, after_entry_keyboard
from repositories.user_repo import get_language
from enums import PourMethod, PumpLogistics
from states import EntryStates
from services.entry_service import save_entry

router = Router()


@router.callback_query(F.data.startswith("pour_method:"), EntryStates.choosing_pour_method)
async def on_pour_method(callback: CallbackQuery, state: FSMContext):
    method = callback.data.split(":")[1]
    lang = await get_language(callback.from_user.id)

    await state.update_data(pour_method=method)

    if method in (PourMethod.STATIONARY_PUMP, PourMethod.MOBILE_PUMP):
        await callback.message.edit_text(
            t("select_pump_type", lang),
            reply_markup=pump_type_keyboard(lang)
        )
        await state.set_state(EntryStates.choosing_pump_type)
    else:
        # No pump — skip pump type, go to logistics (N/A)
        await state.update_data(pump_type=None)
        await callback.message.edit_text(
            t("select_pump_logistics", lang),
            reply_markup=pump_logistics_keyboard(lang)
        )
        await state.set_state(EntryStates.choosing_pump_logistics)

    await callback.answer()


@router.callback_query(F.data.startswith("pump_type:"), EntryStates.choosing_pump_type)
async def on_pump_type(callback: CallbackQuery, state: FSMContext):
    pump_type = callback.data.split(":")[1]
    lang = await get_language(callback.from_user.id)

    await state.update_data(pump_type=pump_type)
    await callback.message.edit_text(
        t("select_pump_logistics", lang),
        reply_markup=pump_logistics_keyboard(lang)
    )
    await state.set_state(EntryStates.choosing_pump_logistics)
    await callback.answer()


@router.callback_query(F.data.startswith("pump_logistics:"), EntryStates.choosing_pump_logistics)
async def on_pump_logistics(callback: CallbackQuery, state: FSMContext):
    logistics = callback.data.split(":")[1]
    lang = await get_language(callback.from_user.id)

    await state.update_data(pump_logistics=logistics)

    # Save entry
    await save_entry(callback.from_user.id, state)

    await callback.message.edit_text(
        t("entry_saved", lang),
        reply_markup=after_entry_keyboard(lang)
    )
    await state.set_state(EntryStates.entry_done)
    await callback.answer()
