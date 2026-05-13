import logging
from aiogram import Router, F
from aiogram.filters import CommandStart
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext

from states import AuthStates
from data.translations import t
from keyboards.builders import lang_keyboard, main_menu_keyboard
from repositories.user_repo import get_user, create_user, update_user_lang, use_invite_code
from services.access_service import is_admin, is_senior_or_above

logger = logging.getLogger(__name__)
router = Router()


@router.message(CommandStart())
async def cmd_start(message: Message, state: FSMContext):
    await state.clear()
    user = await get_user(message.from_user.id)

    if user:
        if not user["is_active"]:
            await message.answer(t("blocked", user["lang"]))
            return
        lang = user["lang"]
        senior = await is_senior_or_above(message.from_user.id)
        admin = await is_admin(message.from_user.id)
        await message.answer(
            t("main_menu", lang),
            reply_markup=main_menu_keyboard(lang, senior, admin)
        )
        return

    # New user — ask invite code
    await state.set_state(AuthStates.waiting_code)
    await message.answer(t("welcome", "ru"))


@router.message(AuthStates.waiting_code)
async def process_invite_code(message: Message, state: FSMContext):
    code = message.text.strip().upper()
    tg_id = message.from_user.id

    valid = await use_invite_code(code, tg_id)
    if not valid:
        await message.answer(t("invalid_code", "ru"))
        return

    # Code OK — create user skeleton, ask language
    await create_user(
        telegram_id=tg_id,
        username=message.from_user.username or "",
        full_name=message.from_user.full_name or "Unknown",
    )
    await state.set_state(AuthStates.choosing_lang)
    await message.answer(t("choose_lang", "ru"), reply_markup=lang_keyboard())


@router.callback_query(AuthStates.choosing_lang, F.data.startswith("lang:"))
async def process_lang_choice(callback: CallbackQuery, state: FSMContext):
    lang = callback.data.split(":")[1]
    await update_user_lang(callback.from_user.id, lang)
    await state.clear()
    await callback.message.edit_text(t("lang_set", lang))

    senior = await is_senior_or_above(callback.from_user.id)
    admin = await is_admin(callback.from_user.id)
    await callback.message.answer(
        t("main_menu", lang),
        reply_markup=main_menu_keyboard(lang, senior, admin)
    )
    await callback.answer()
