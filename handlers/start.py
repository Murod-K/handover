from aiogram import Router, F
from aiogram.filters import CommandStart, Command
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext

from data.translations import t
from keyboards.builders import lang_kb, main_menu_kb
from repositories.user_repo import get_or_create, set_language, get_language, get_role
from states import LangSG, MenuSG

router = Router()


async def show_main_menu(obj, lang: str, tg_id: int, state: FSMContext):
    role = await get_role(tg_id)
    is_admin = (role == "admin")
    text = t("main_menu", lang)
    kb = main_menu_kb(lang, is_admin)
    if isinstance(obj, Message):
        await obj.answer(text, reply_markup=kb, parse_mode="Markdown")
    else:
        try:
            await obj.message.edit_text(text, reply_markup=kb, parse_mode="Markdown")
        except Exception:
            await obj.message.answer(text, reply_markup=kb, parse_mode="Markdown")
    await state.set_state(MenuSG.main)


@router.message(CommandStart())
async def cmd_start(message: Message, state: FSMContext):
    user = await get_or_create(
        message.from_user.id,
        message.from_user.username,
        message.from_user.full_name
    )
    lang = user.get("language", "ru")
    await show_main_menu(message, lang, message.from_user.id, state)


@router.callback_query(F.data == "menu:settings")
async def on_settings(callback: CallbackQuery, state: FSMContext):
    await callback.message.edit_text(
        t("welcome", "ru"),
        reply_markup=lang_kb(),
        parse_mode="Markdown"
    )
    await state.set_state(LangSG.choosing)
    await callback.answer()


@router.callback_query(F.data.startswith("lang:"))
async def on_lang(callback: CallbackQuery, state: FSMContext):
    lang = callback.data.split(":")[1]
    await set_language(callback.from_user.id, lang)
    await show_main_menu(callback, lang, callback.from_user.id, state)
    await callback.answer()


@router.callback_query(F.data == "menu:main")
async def on_main_menu(callback: CallbackQuery, state: FSMContext):
    lang = await get_language(callback.from_user.id)
    await show_main_menu(callback, lang, callback.from_user.id, state)
    await callback.answer()


@router.message(Command("lang"))
async def cmd_lang(message: Message, state: FSMContext):
    await message.answer(t("welcome", "ru"), reply_markup=lang_kb(), parse_mode="Markdown")
    await state.set_state(LangSG.choosing)


@router.message(Command("menu"))
async def cmd_menu(message: Message, state: FSMContext):
    lang = await get_language(message.from_user.id)
    await show_main_menu(message, lang, message.from_user.id, state)
