import aiosqlite
import os

DB_PATH = os.getenv("DB_PATH", "handover.db")

# First telegram_id in DB becomes admin automatically
ADMIN_IDS: set[int] = set()


async def get_or_create(tg_id: int, username: str = None, full_name: str = None) -> dict:
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        row = await (await db.execute(
            "SELECT * FROM users WHERE telegram_id=?", (tg_id,)
        )).fetchone()
        if row:
            return dict(row)
        # First user = admin
        count = (await (await db.execute("SELECT COUNT(*) FROM users")).fetchone())[0]
        role = "admin" if count == 0 else "engineer"
        await db.execute(
            "INSERT INTO users (telegram_id, username, full_name, role) VALUES (?,?,?,?)",
            (tg_id, username, full_name, role)
        )
        await db.commit()
        row = await (await db.execute(
            "SELECT * FROM users WHERE telegram_id=?", (tg_id,)
        )).fetchone()
        return dict(row)


async def set_language(tg_id: int, lang: str):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("UPDATE users SET language=? WHERE telegram_id=?", (lang, tg_id))
        await db.commit()


async def get_language(tg_id: int) -> str:
    async with aiosqlite.connect(DB_PATH) as db:
        row = await (await db.execute(
            "SELECT language FROM users WHERE telegram_id=?", (tg_id,)
        )).fetchone()
        return row[0] if row else "ru"


async def get_role(tg_id: int) -> str:
    async with aiosqlite.connect(DB_PATH) as db:
        row = await (await db.execute(
            "SELECT role FROM users WHERE telegram_id=?", (tg_id,)
        )).fetchone()
        return row[0] if row else "engineer"
