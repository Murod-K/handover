import asyncio
import logging
import os
import sys
from datetime import datetime, timedelta

from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.fsm.context import FSMContext

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

LOCK_FILE = "/tmp/handover_v3.lock"


def acquire_lock():
    if os.path.exists(LOCK_FILE):
        try:
            with open(LOCK_FILE) as f:
                pid = int(f.read().strip())
            os.kill(pid, 0)
            logger.error(f"Another instance running (PID {pid}). Exiting.")
            sys.exit(1)
        except (ProcessLookupError, ValueError):
            pass
    with open(LOCK_FILE, "w") as f:
        f.write(str(os.getpid()))


def release_lock():
    try:
        os.remove(LOCK_FILE)
    except FileNotFoundError:
        pass


async def fsm_timeout_task(bot: Bot, storage: MemoryStorage):
    """Background task: clear FSM states idle for > FSM_TIMEOUT_MINUTES."""
    while True:
        await asyncio.sleep(60)
        try:
            timeout = timedelta(minutes=FSM_TIMEOUT_MINUTES)
            now = datetime.utcnow()
            # MemoryStorage doesn't expose idle times directly,
            # so we track via custom data key "fsm_last_activity"
            data_map = storage._storage  # internal dict {(chat_id, user_id): {state, data}}
            to_clear = []
            for key, val in list(data_map.items()):
                state_data = val.get("data", {})
                last = state_data.get("fsm_last_activity")
                if last and (now - datetime.fromisoformat(last)) > timeout:
                    to_clear.append(key)
            for key in to_clear:
                chat_id, user_id = key
                try:
                    user = await get_user(user_id)
                    lang = user["lang"] if user else "ru"
                    await bot.send_message(chat_id, t("fsm_timeout", lang))
                except Exception:
                    pass
                if key in storage._storage:
                    del storage._storage[key]
        except Exception as e:
            logger.warning(f"FSM timeout task error: {e}")


async def main():
    if not BOT_TOKEN:
        logger.error("BOT_TOKEN not set!")
        sys.exit(1)

    acquire_lock()
    try:
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

        # Middleware: update fsm_last_activity on every update
        from aiogram import BaseMiddleware
        from aiogram.types import Update

        class ActivityMiddleware(BaseMiddleware):
            async def __call__(self, handler, event, data):
                fsm_context: FSMContext = data.get("state")
                if fsm_context:
                    try:
                        state = await fsm_context.get_state()
                        if state:
                            sd = await fsm_context.get_data()
                            sd["fsm_last_activity"] = datetime.utcnow().isoformat()
                            await fsm_context.set_data(sd)
                    except Exception:
                        pass
                return await handler(event, data)

        dp.update.middleware(ActivityMiddleware())

        asyncio.create_task(fsm_timeout_task(bot, storage))

        logger.info("Bot starting...")
        await dp.start_polling(bot, allowed_updates=["message", "callback_query"])
    finally:
        release_lock()


if __name__ == "__main__":
    asyncio.run(main())
