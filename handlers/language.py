from aiogram import Router, F
from aiogram.types import CallbackQuery, Message
from aiogram.fsm.context import FSMContext

from data.translations import t
from keyboards.builders import language_keyboard
from repositories.user_repo import set_language, get_language
from states import LanguageStates

router = Router()


@router.callback_query(F.data.startswith("lang:"))
async def on_language_chosen(callback: CallbackQuery, state: FSMContext):
    lang = callback.data.split(":")[1]
    await set_language(callback.from_user.id, lang)

    await callback.message.edit_text(
        t("lang_saved", lang)
    )
    await state.clear()

    from handlers.project import show_projects
    await show_projects(callback.message, lang)
    await callback.answer()


@router.message(F.text.startswith("/lang"))
async def cmd_change_language(message: Message, state: FSMContext):
    await message.answer(
        t("welcome", "ru"),
        reply_markup=language_keyboard()
    )
    await state.set_state(LanguageStates.choosing)
