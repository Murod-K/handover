import aiosqlite
from datetime import datetime
from config import Config

DB_PATH = Config().DB_PATH


async def create_shift(
    telegram_id: int,
    project_id: int,
    subproject_id: int,
    shift_type: str
) -> int:
    async with aiosqlite.connect(DB_PATH) as db:
        # Close any open shifts for this user
        await db.execute(
            "UPDATE shifts SET is_active = 0, finished_at = ? WHERE telegram_id = ? AND is_active = 1",
            (datetime.now(), telegram_id)
        )
        cursor = await db.execute(
            """INSERT INTO shifts (telegram_id, project_id, subproject_id, shift_type)
               VALUES (?, ?, ?, ?)""",
            (telegram_id, project_id, subproject_id, shift_type)
        )
        await db.commit()
        return cursor.lastrowid


async def get_active_shift(telegram_id: int) -> dict | None:
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute(
            "SELECT * FROM shifts WHERE telegram_id = ? AND is_active = 1",
            (telegram_id,)
        ) as cursor:
            row = await cursor.fetchone()
            return dict(row) if row else None


async def finish_shift(shift_id: int):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            "UPDATE shifts SET is_active = 0, finished_at = ? WHERE id = ?",
            (datetime.now(), shift_id)
        )
        await db.commit()


async def create_entry(entry_data: dict) -> int:
    async with aiosqlite.connect(DB_PATH) as db:
        cursor = await db.execute(
            """INSERT INTO entries (
                shift_id, structure_type, structure_name,
                natura_status, rebar_status, concrete_plan,
                concrete_available, formwork_ready, waterproof_ready,
                rebar_ready_for_pour, concrete_volume, pour_method,
                pump_type, pump_logistics, rebar_comment,
                rebar_comment_translated, entry_comment, entry_comment_translated
            ) VALUES (
                :shift_id, :structure_type, :structure_name,
                :natura_status, :rebar_status, :concrete_plan,
                :concrete_available, :formwork_ready, :waterproof_ready,
                :rebar_ready_for_pour, :concrete_volume, :pour_method,
                :pump_type, :pump_logistics, :rebar_comment,
                :rebar_comment_translated, :entry_comment, :entry_comment_translated
            )""",
            entry_data
        )
        await db.commit()
        return cursor.lastrowid


async def add_entry_defects(entry_id: int, defects: list[tuple[str, str | None]]):
    async with aiosqlite.connect(DB_PATH) as db:
        for defect_code, custom_text in defects:
            await db.execute(
                "INSERT INTO entry_defects (entry_id, defect_code, custom_text) VALUES (?, ?, ?)",
                (entry_id, defect_code, custom_text)
            )
        await db.commit()


async def get_shift_entries(shift_id: int) -> list[dict]:
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute(
            "SELECT * FROM entries WHERE shift_id = ? ORDER BY created_at",
            (shift_id,)
        ) as cursor:
            rows = await cursor.fetchall()
            return [dict(r) for r in rows]


async def get_entry_defects(entry_id: int) -> list[dict]:
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute(
            "SELECT * FROM entry_defects WHERE entry_id = ?", (entry_id,)
        ) as cursor:
            rows = await cursor.fetchall()
            return [dict(r) for r in rows]


async def get_last_shift_entries(telegram_id: int) -> list[dict]:
    """Get entries from the most recently completed shift (for 'same as yesterday')."""
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute(
            """SELECT e.* FROM entries e
               JOIN shifts s ON e.shift_id = s.id
               WHERE s.telegram_id = ? AND s.is_active = 0
               ORDER BY s.finished_at DESC, e.id DESC
               LIMIT 10""",
            (telegram_id,)
        ) as cursor:
            rows = await cursor.fetchall()
            return [dict(r) for r in rows]
