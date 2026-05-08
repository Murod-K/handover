from aiogram import Router
from aiogram.filters import CommandStart
from aiogram.types import Message
from aiogram.fsm.context import FSMContext

from data.translations import t
from keyboards.builders import language_keyboard
from repositories.user_repo import get_or_create_user
from states import LanguageStates

router = Router()


@router.message(CommandStart())
async def cmd_start(message: Message, state: FSMContext):
    user = await get_or_create_user(
        telegram_id=message.from_user.id,
        username=message.from_user.username
    )
    lang = user.get("language", "ru")

    if not user.get("language") or lang == "ru":
        # Prompt language choice on first launch
        await message.answer(
            t("welcome", "ru"),
            reply_markup=language_keyboard()
        )
        await state.set_state(LanguageStates.choosing)
    else:
        from handlers.project import show_projects
        await show_projects(message, lang)
