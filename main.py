import asyncio
import logging
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage

from config import Config
from handlers import (
    start, language, project, shift, structure,
    rebar, concrete, pump, report
)
from middlewares.db_middleware import DbMiddleware
from services.database import init_db

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


async def main():
    config = Config()
    await init_db()

    bot = Bot(token=config.BOT_TOKEN)
    storage = MemoryStorage()
    dp = Dispatcher(storage=storage)

    dp.update.middleware(DbMiddleware())

    # Register routers
    dp.include_router(start.router)
    dp.include_router(language.router)
    dp.include_router(project.router)
    dp.include_router(shift.router)
    dp.include_router(structure.router)
    dp.include_router(rebar.router)
    dp.include_router(concrete.router)
    dp.include_router(pump.router)
    dp.include_router(report.router)

    logger.info("Bot started")
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
