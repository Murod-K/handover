import secrets
import string
import logging
from services.database import get_db

logger = logging.getLogger(__name__)


async def get_user(telegram_id: int):
    async with await get_db() as db:
        cur = await db.execute("SELECT * FROM users WHERE telegram_id = ?", (telegram_id,))
        return await cur.fetchone()


async def create_user(telegram_id: int, username: str, full_name: str, lang: str = "ru", role: str = "engineer"):
    async with await get_db() as db:
        await db.execute("""
            INSERT OR IGNORE INTO users (telegram_id, username, full_name, lang, role)
            VALUES (?, ?, ?, ?, ?)
        """, (telegram_id, username, full_name, lang, role))
        await db.commit()


async def update_user_lang(telegram_id: int, lang: str):
    async with await get_db() as db:
        await db.execute("UPDATE users SET lang = ? WHERE telegram_id = ?", (lang, telegram_id))
        await db.commit()


async def update_user_role(telegram_id: int, role: str):
    async with await get_db() as db:
        await db.execute("UPDATE users SET role = ? WHERE telegram_id = ?", (role, telegram_id))
        await db.commit()


async def set_user_active(telegram_id: int, is_active: bool):
    async with await get_db() as db:
        await db.execute("UPDATE users SET is_active = ? WHERE telegram_id = ?", (int(is_active), telegram_id))
        await db.commit()


async def get_all_users():
    async with await get_db() as db:
        cur = await db.execute("SELECT * FROM users ORDER BY created_at DESC")
        return await cur.fetchall()


async def find_user_by_username(username: str):
    uname = username.lstrip("@")
    async with await get_db() as db:
        cur = await db.execute("SELECT * FROM users WHERE username = ?", (uname,))
        return await cur.fetchone()


async def use_invite_code(code: str, telegram_id: int) -> bool:
    """Returns True if code is valid and was consumed."""
    async with await get_db() as db:
        cur = await db.execute(
            "SELECT * FROM invite_codes WHERE code = ? AND is_used = 0", (code,)
        )
        row = await cur.fetchone()
        if not row:
            return False
        await db.execute("""
            UPDATE invite_codes SET is_used = 1, used_by = ?, used_at = CURRENT_TIMESTAMP
            WHERE id = ?
        """, (telegram_id, row["id"]))
        await db.commit()
        return True


async def generate_invite_codes(created_by: int, count: int) -> list[str]:
    chars = string.ascii_uppercase + string.digits
    codes = ["".join(secrets.choice(chars) for _ in range(8)) for _ in range(count)]
    async with await get_db() as db:
        await db.executemany(
            "INSERT INTO invite_codes (code, created_by) VALUES (?, ?)",
            [(c, created_by) for c in codes]
        )
        await db.commit()
    return codes
