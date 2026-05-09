import aiosqlite
import os
from datetime import datetime

DB_PATH = os.getenv("DB_PATH", "handover.db")


async def create_shift(tg_id, project_id, subproject_id, shift_type) -> int:
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            "UPDATE shifts SET is_active=0, finished_at=? WHERE telegram_id=? AND is_active=1",
            (datetime.now(), tg_id)
        )
        cur = await db.execute(
            "INSERT INTO shifts (telegram_id, project_id, subproject_id, shift_type) VALUES (?,?,?,?)",
            (tg_id, project_id, subproject_id, shift_type)
        )
        await db.commit()
        return cur.lastrowid


async def get_active_shift(tg_id: int) -> dict | None:
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        row = await (await db.execute(
            "SELECT * FROM shifts WHERE telegram_id=? AND is_active=1", (tg_id,)
        )).fetchone()
        return dict(row) if row else None


async def finish_shift(shift_id: int):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            "UPDATE shifts SET is_active=0, finished_at=? WHERE id=?",
            (datetime.now(), shift_id)
        )
        await db.commit()


async def create_entry(data: dict) -> int:
    async with aiosqlite.connect(DB_PATH) as db:
        cur = await db.execute("""
            INSERT INTO entries (
                shift_id, structure_type_id, structure_name,
                natura_status, rebar_status, concrete_plan,
                pour_method_id, pump_type_id, pump_logistics,
                concrete_volume, formwork_ready, waterproof_ready,
                rebar_ready_for_pour, comment,
                comment_ru, comment_uz, comment_en, comment_tr
            ) VALUES (
                :shift_id, :structure_type_id, :structure_name,
                :natura_status, :rebar_status, :concrete_plan,
                :pour_method_id, :pump_type_id, :pump_logistics,
                :concrete_volume, :formwork_ready, :waterproof_ready,
                :rebar_ready_for_pour, :comment,
                :comment_ru, :comment_uz, :comment_en, :comment_tr
            )
        """, data)
        await db.commit()
        return cur.lastrowid


async def add_defects(entry_id: int, defects: list[tuple]):
    """defects = list of (defect_id, custom_text)"""
    async with aiosqlite.connect(DB_PATH) as db:
        for d_id, custom in defects:
            await db.execute(
                "INSERT INTO entry_defects (entry_id, defect_id, custom_text) VALUES (?,?,?)",
                (entry_id, d_id, custom)
            )
        await db.commit()


async def delete_last_entry(shift_id: int) -> bool:
    async with aiosqlite.connect(DB_PATH) as db:
        row = await (await db.execute(
            "SELECT id FROM entries WHERE shift_id=? ORDER BY id DESC LIMIT 1", (shift_id,)
        )).fetchone()
        if not row:
            return False
        await db.execute("DELETE FROM entry_defects WHERE entry_id=?", (row[0],))
        await db.execute("DELETE FROM entries WHERE id=?", (row[0],))
        await db.commit()
        return True


async def get_entries(shift_id: int) -> list[dict]:
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        rows = await (await db.execute(
            "SELECT * FROM entries WHERE shift_id=? ORDER BY id", (shift_id,)
        )).fetchall()
        return [dict(r) for r in rows]


async def get_entry_defects(entry_id: int) -> list[dict]:
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        rows = await (await db.execute("""
            SELECT ed.custom_text,
                   dt.name_ru, dt.name_uz, dt.name_en, dt.name_tr, dt.code
            FROM entry_defects ed
            LEFT JOIN defect_types dt ON dt.id = ed.defect_id
            WHERE ed.entry_id=?
        """, (entry_id,)).fetchall() if False else
        (await db.execute("""
            SELECT ed.custom_text,
                   dt.name_ru, dt.name_uz, dt.name_en, dt.name_tr, dt.code
            FROM entry_defects ed
            LEFT JOIN defect_types dt ON dt.id = ed.defect_id
            WHERE ed.entry_id=?
        """, (entry_id,))).fetchall())
        return [dict(r) for r in rows]


async def get_shift_with_project(shift_id: int) -> dict | None:
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        row = await (await db.execute("""
            SELECT s.*, p.name AS project_name, sp.name AS subproject_name
            FROM shifts s
            LEFT JOIN projects p ON p.id = s.project_id
            LEFT JOIN subprojects sp ON sp.id = s.subproject_id
            WHERE s.id=?
        """, (shift_id,))).fetchone()
        return dict(row) if row else None


async def get_recent_shifts(tg_id: int, limit: int = 5) -> list[dict]:
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        rows = await (await db.execute("""
            SELECT s.*, p.name AS project_name, sp.name AS subproject_name
            FROM shifts s
            LEFT JOIN projects p ON p.id = s.project_id
            LEFT JOIN subprojects sp ON sp.id = s.subproject_id
            WHERE s.telegram_id=? AND s.is_active=0
            ORDER BY s.finished_at DESC LIMIT ?
        """, (tg_id, limit))).fetchall()
        return [dict(r) for r in rows]
