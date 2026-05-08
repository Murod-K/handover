import aiosqlite
from config import Config

DB_PATH = Config().DB_PATH


async def get_or_create_user(telegram_id: int, username: str = None) -> dict:
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute(
            "SELECT * FROM users WHERE telegram_id = ?", (telegram_id,)
        ) as cursor:
            row = await cursor.fetchone()
            if row:
                return dict(row)
        await db.execute(
            "INSERT INTO users (telegram_id, username, language) VALUES (?, ?, 'ru')",
            (telegram_id, username)
        )
        await db.commit()
        async with db.execute(
            "SELECT * FROM users WHERE telegram_id = ?", (telegram_id,)
        ) as cursor:
            return dict(await cursor.fetchone())


async def set_language(telegram_id: int, lang: str):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            "UPDATE users SET language = ? WHERE telegram_id = ?", (lang, telegram_id)
        )
        await db.commit()


async def get_language(telegram_id: int) -> str:
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute(
            "SELECT language FROM users WHERE telegram_id = ?", (telegram_id,)
        ) as cursor:
            row = await cursor.fetchone()
            return row[0] if row else "ru"
