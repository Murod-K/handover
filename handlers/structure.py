from aiogram import Router, F
from aiogram.types import CallbackQuery, Message
from aiogram.fsm.context import FSMContext

from data.translations import t
from keyboards.builders import natura_keyboard, rebar_status_keyboard
from repositories.user_repo import get_language
from enums import NaturaStatus
from states import EntryStates

router = Router()


@router.callback_query(F.data.startswith("struct:"), EntryStates.choosing_structure_type)
async def on_structure_type_chosen(callback: CallbackQuery, state: FSMContext):
    structure_type = callback.data.split(":")[1]
    lang = await get_language(callback.from_user.id)

    await state.update_data(structure_type=structure_type)
    await callback.message.edit_text(t("enter_structure_name", lang))
    await state.set_state(EntryStates.entering_structure_name)
    await callback.answer()


@router.message(EntryStates.entering_structure_name)
async def on_structure_name_entered(message: Message, state: FSMContext):
    lang = await get_language(message.from_user.id)
    name = message.text.strip()

    await state.update_data(structure_name=name)
    await message.answer(
        t("select_natura", lang),
        reply_markup=natura_keyboard(lang)
    )
    await state.set_state(EntryStates.choosing_natura)


@router.callback_query(F.data.startswith("natura:"), EntryStates.choosing_natura)
async def on_natura_chosen(callback: CallbackQuery, state: FSMContext):
    natura = callback.data.split(":")[1]
    lang = await get_language(callback.from_user.id)

    await state.update_data(natura_status=natura)

    # Show warning but continue
    warning = ""
    if natura == NaturaStatus.NOT_GIVEN:
        warning = f"\n\n{t('warn_natura_not_given', lang)}"
    elif natura == NaturaStatus.WILL_BE_NIGHT:
        warning = f"\n\n{t('warn_natura_night', lang)}"

    await callback.message.edit_text(
        t("select_rebar_status", lang) + warning,
        reply_markup=rebar_status_keyboard(lang)
    )
    await state.set_state(EntryStates.choosing_rebar_status)
    await callback.answer()
