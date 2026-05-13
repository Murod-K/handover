import logging
from aiogram import Router, F
from aiogram.types import CallbackQuery, Message
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext

from data.translations import t
from keyboards.builders import main_menu_keyboard
from repositories.user_repo import get_user
from services.access_service import check_access, is_admin, is_senior_or_above

logger = logging.getLogger(__name__)
router = Router()


async def show_main_menu(event, lang: str, tg_id: int):
    senior = await is_senior_or_above(tg_id)
    admin = await is_admin(tg_id)
    text = t("main_menu", lang)
    kb = main_menu_keyboard(lang, senior, admin)
    if isinstance(event, CallbackQuery):
        await event.message.edit_text(text, reply_markup=kb)
        await event.answer()
    else:
        await event.answer(text, reply_markup=kb)


@router.callback_query(F.data == "menu:main")
async def back_to_menu(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    user = await get_user(callback.from_user.id)
    if not user:
        await callback.answer()
        return
    await show_main_menu(callback, user["lang"], callback.from_user.id)


@router.message(Command("menu"))
async def cmd_menu(message: Message, state: FSMContext):
    allowed, reason = await check_access(message.from_user.id)
    if not allowed:
        await message.answer(t("no_access", "ru"))
        return
    user = await get_user(message.from_user.id)
    await show_main_menu(message, user["lang"], message.from_user.id)
