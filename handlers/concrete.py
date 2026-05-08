from aiogram import Router, F
from aiogram.types import CallbackQuery, Message
from aiogram.fsm.context import FSMContext

from data.translations import t
from keyboards.builders import (
    yes_no_keyboard, readiness_keyboard, pour_method_keyboard, after_entry_keyboard
)
from repositories.user_repo import get_language
from enums import (
    ConcretePlan, ConcreteAvailable, ReadinessStatus,
    RebarStatus, NaturaStatus, PourMethod
)
from states import EntryStates
from services.entry_service import save_entry

router = Router()


@router.callback_query(F.data.startswith("concrete_plan:"), EntryStates.choosing_concrete_plan)
async def on_concrete_plan(callback: CallbackQuery, state: FSMContext):
    plan = callback.data.split(":")[1]
    lang = await get_language(callback.from_user.id)
    data = await state.get_data()

    await state.update_data(concrete_plan=plan)

    if plan == ConcretePlan.NO_POUR:
        # Save entry directly
        entry_id = await save_entry(callback.from_user.id, state)
        await callback.message.edit_text(
            t("entry_saved", lang),
            reply_markup=after_entry_keyboard(lang)
        )
        await state.set_state(EntryStates.entry_done)
        await callback.answer()
        return

    # Check blocking conditions
    rebar_status = data.get("rebar_status")
    natura_status = data.get("natura_status")

    blocks = []
    if rebar_status == RebarStatus.NOT_ACCEPTED:
        blocks.append(t("error_rebar_blocks_pour", lang))
    if natura_status == NaturaStatus.NOT_GIVEN:
        blocks.append(t("warn_natura_not_given", lang))

    if blocks:
        warning_text = "\n".join(blocks)
        await callback.message.edit_text(
            f"{t('check_concrete_available', lang)}\n\n‼️ {warning_text}",
            reply_markup=yes_no_keyboard(
                lang,
                yes_cb=f"concrete_avail:{ConcreteAvailable.YES.value}",
                no_cb=f"concrete_avail:{ConcreteAvailable.NO.value}"
            )
        )
    else:
        await callback.message.edit_text(
            t("check_concrete_available", lang),
            reply_markup=yes_no_keyboard(
                lang,
                yes_cb=f"concrete_avail:{ConcreteAvailable.YES.value}",
                no_cb=f"concrete_avail:{ConcreteAvailable.NO.value}"
            )
        )
    await state.set_state(EntryStates.checking_concrete_available)
    await callback.answer()


@router.callback_query(F.data.startswith("concrete_avail:"), EntryStates.checking_concrete_available)
async def on_concrete_available(callback: CallbackQuery, state: FSMContext):
    available = callback.data.split(":")[1]
    lang = await get_language(callback.from_user.id)

    await state.update_data(concrete_available=available)

    if available == ConcreteAvailable.NO:
        # Critical warning — still let them fill rest but note it
        await callback.message.edit_text(
            f"{t('warn_no_concrete', lang)}\n\n{t('check_formwork', lang)}",
            reply_markup=readiness_keyboard(lang, "formwork")
        )
    else:
        await callback.message.edit_text(
            t("check_formwork", lang),
            reply_markup=readiness_keyboard(lang, "formwork")
        )
    await state.set_state(EntryStates.choosing_formwork_ready)
    await callback.answer()


@router.callback_query(F.data.startswith("formwork:"), EntryStates.choosing_formwork_ready)
async def on_formwork_ready(callback: CallbackQuery, state: FSMContext):
    status = callback.data.split(":")[1]
    lang = await get_language(callback.from_user.id)

    await state.update_data(formwork_ready=status)
    await callback.message.edit_text(
        t("check_waterproof", lang),
        reply_markup=readiness_keyboard(lang, "waterproof")
    )
    await state.set_state(EntryStates.choosing_waterproof_ready)
    await callback.answer()


@router.callback_query(F.data.startswith("waterproof:"), EntryStates.choosing_waterproof_ready)
async def on_waterproof_ready(callback: CallbackQuery, state: FSMContext):
    status = callback.data.split(":")[1]
    lang = await get_language(callback.from_user.id)

    await state.update_data(waterproof_ready=status)
    await callback.message.edit_text(
        t("check_rebar_for_pour", lang),
        reply_markup=readiness_keyboard(lang, "rebar_pour")
    )
    await state.set_state(EntryStates.choosing_rebar_ready_for_pour)
    await callback.answer()


@router.callback_query(F.data.startswith("rebar_pour:"), EntryStates.choosing_rebar_ready_for_pour)
async def on_rebar_pour_ready(callback: CallbackQuery, state: FSMContext):
    status = callback.data.split(":")[1]
    lang = await get_language(callback.from_user.id)

    await state.update_data(rebar_ready_for_pour=status)
    await callback.message.edit_text(t("enter_concrete_volume", lang))
    await state.set_state(EntryStates.entering_concrete_volume)
    await callback.answer()


@router.message(EntryStates.entering_concrete_volume)
async def on_concrete_volume(message: Message, state: FSMContext):
    lang = await get_language(message.from_user.id)
    text = message.text.strip().replace(",", ".")

    try:
        volume = float(text)
        if volume <= 0:
            raise ValueError
    except ValueError:
        await message.answer(t("invalid_volume", lang))
        return

    await state.update_data(concrete_volume=volume)
    await message.answer(
        t("select_pour_method", lang),
        reply_markup=pour_method_keyboard(lang)
    )
    await state.set_state(EntryStates.choosing_pour_method)
