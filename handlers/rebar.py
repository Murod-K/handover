from aiogram import Router, F
from aiogram.types import CallbackQuery, Message
from aiogram.fsm.context import FSMContext

from data.translations import t
from keyboards.builders import rebar_defects_keyboard, concrete_plan_keyboard
from repositories.user_repo import get_language
from enums import RebarStatus, RebarDefect
from states import EntryStates

router = Router()


@router.callback_query(F.data.startswith("rebar_status:"), EntryStates.choosing_rebar_status)
async def on_rebar_status_chosen(callback: CallbackQuery, state: FSMContext):
    rebar_status = callback.data.split(":")[1]
    lang = await get_language(callback.from_user.id)

    await state.update_data(rebar_status=rebar_status, selected_defects=[])

    if rebar_status != RebarStatus.ACCEPTED:
        # Show defect checklist
        await callback.message.edit_text(
            t("select_rebar_defects", lang),
            reply_markup=rebar_defects_keyboard(lang, selected=[])
        )
        await state.set_state(EntryStates.choosing_rebar_defects)
    else:
        # No defects needed — go to rebar comment
        await callback.message.edit_text(t("enter_rebar_comment", lang))
        await state.set_state(EntryStates.entering_rebar_comment)

    await callback.answer()


@router.callback_query(F.data.startswith("defect:"), EntryStates.choosing_rebar_defects)
async def on_defect_toggled(callback: CallbackQuery, state: FSMContext):
    defect_value = callback.data.split(":")[1]
    lang = await get_language(callback.from_user.id)
    data = await state.get_data()
    selected = data.get("selected_defects", [])

    if defect_value == "DONE":
        # Move to rebar comment
        await callback.message.edit_text(t("enter_rebar_comment", lang))
        await state.set_state(EntryStates.entering_rebar_comment)
        await callback.answer()
        return

    # Toggle selection
    if defect_value in selected:
        selected.remove(defect_value)
    else:
        selected.append(defect_value)

    await state.update_data(selected_defects=selected)

    await callback.message.edit_text(
        t("select_rebar_defects", lang),
        reply_markup=rebar_defects_keyboard(lang, selected=selected)
    )
    await callback.answer()


@router.message(EntryStates.choosing_rebar_defects, F.text == "/skip")
async def skip_defects(message: Message, state: FSMContext):
    lang = await get_language(message.from_user.id)
    await message.answer(t("enter_rebar_comment", lang))
    await state.set_state(EntryStates.entering_rebar_comment)


@router.message(EntryStates.entering_rebar_comment)
async def on_rebar_comment(message: Message, state: FSMContext):
    lang = await get_language(message.from_user.id)
    text = message.text.strip()

    if text == "/skip" or text.lower() == "skip":
        await state.update_data(rebar_comment=None)
    else:
        await state.update_data(rebar_comment=text)

    # Proceed to concrete section
    await message.answer(
        t("select_concrete_plan", lang),
        reply_markup=concrete_plan_keyboard(lang)
    )
    await state.set_state(EntryStates.choosing_concrete_plan)
