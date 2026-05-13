import asyncio
import logging
import os
import sys
from datetime import datetime, timedelta
from typing import Any, Awaitable, Callable, Dict

from aiogram import Bot, Dispatcher, BaseMiddleware
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.fsm.context import FSMContext
from aiogram.types import TelegramObject

from config import BOT_TOKEN, FSM_TIMEOUT_MINUTES
from services.database import init_db
from handlers import auth, menu, shift, report, admin
from data.translations import t
from repositories.user_repo import get_user

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger(__name__)

# ─── Timeout tracker (own dict, no private API) ───────────────────────────────
# { (chat_id, user_id): last_activity_datetime }
_activity: dict[tuple, datetime] = {}


class ActivityMiddleware(BaseMiddleware):
    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any],
    ) -> Any:
        fsm_context: FSMContext | None = data.get("state")
        if fsm_context:
            try:
                state = await fsm_context.get_state()
                if state:
                    key = (fsm_context.key.chat_id, fsm_context.key.user_id)
                    _activity[key] = datetime.utcnow()
            except Exception:
                pass
        return await handler(event, data)


async def fsm_timeout_task(bot: Bot, dp: Dispatcher):
    """Every 60 s check for sessions idle longer than FSM_TIMEOUT_MINUTES."""
    while True:
        await asyncio.sleep(60)
        try:
            timeout = timedelta(minutes=FSM_TIMEOUT_MINUTES)
            now = datetime.utcnow()
            expired = [k for k, ts in list(_activity.items()) if now - ts > timeout]
            for chat_id, user_id in expired:
                _activity.pop((chat_id, user_id), None)
                try:
                    from aiogram.fsm.storage.base import StorageKey
                    key = StorageKey(bot_id=bot.id, chat_id=chat_id, user_id=user_id)
                    ctx = FSMContext(storage=dp.storage, key=key)
                    state = await ctx.get_state()
                    if state:
                        await ctx.clear()
                        user = await get_user(user_id)
                        lang = user["lang"] if user else "ru"
                        await bot.send_message(chat_id, t("fsm_timeout", lang))
                except Exception as e:
                    logger.debug(f"FSM timeout cleanup: {e}")
        except Exception as e:
            logger.warning(f"FSM timeout task error: {e}")


async def main():
    if not BOT_TOKEN:
        logger.error("BOT_TOKEN not set!")
        sys.exit(1)

    await init_db()
    logger.info("Database ready.")

    bot = Bot(token=BOT_TOKEN)
    storage = MemoryStorage()
    dp = Dispatcher(storage=storage)

    # Register routers
    dp.include_router(auth.router)
    dp.include_router(menu.router)
    dp.include_router(shift.router)
    dp.include_router(report.router)
    dp.include_router(admin.router)

    dp.update.middleware(ActivityMiddleware())

    logger.info("Bot starting...")
    # Run timeout task alongside polling
    await asyncio.gather(
        dp.start_polling(bot, allowed_updates=["message", "callback_query"]),
        fsm_timeout_task(bot, dp),
    )


if __name__ == "__main__":
    asyncio.run(main())
