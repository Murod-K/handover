import asyncio
import logging
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from config import Config
from services.database import init_db
from handlers import start, shift, entry, report, admin

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)


async def main():
    cfg = Config()
    await init_db()

    bot = Bot(token=cfg.BOT_TOKEN)
    dp = Dispatcher(storage=MemoryStorage())

    dp.include_router(start.router)
    dp.include_router(shift.router)
    dp.include_router(entry.router)
    dp.include_router(report.router)
    dp.include_router(admin.router)

    logging.info("🤖 Handover Bot v2 started")
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
