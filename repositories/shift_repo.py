import logging
from services.database import get_db

logger = logging.getLogger(__name__)


async def create_shift(user_id: int, project_id: int, subproject_id: int, shift_type: str) -> int:
    async with await get_db() as db:
        cur = await db.execute("""
            INSERT INTO shifts (user_id, project_id, subproject_id, shift_type)
            VALUES (?,?,?,?)
        """, (user_id, project_id, subproject_id, shift_type))
        await db.commit()
        return cur.lastrowid


async def finish_shift(shift_id: int):
    async with await get_db() as db:
        await db.execute("""
            UPDATE shifts SET finished_at = CURRENT_TIMESTAMP WHERE id = ?
        """, (shift_id,))
        await db.commit()


async def add_entry(shift_id: int, data: dict) -> int:
    async with await get_db() as db:
        cur = await db.execute("""
            INSERT INTO entries (
                shift_id, structure_type_id, structure_name,
                natura_status, rebar_status, concrete_plan,
                concrete_available, pour_method_id, pump_type_id,
                pump_logistics, concrete_volume,
                formwork_ready, waterproof_ready, rebar_ready_for_pour,
                comment_ru, comment_uz, comment_en, comment_tr
            ) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)
        """, (
            shift_id,
            data.get("structure_type_id"),
            data.get("structure_name", ""),
            data.get("natura_status", ""),
            data.get("rebar_status", ""),
            data.get("concrete_plan", ""),
            int(data.get("concrete_available", False)),
            data.get("pour_method_id"),
            data.get("pump_type_id"),
            data.get("pump_logistics"),
            data.get("concrete_volume"),
            int(data.get("formwork_ready", False)),
            int(data.get("waterproof_ready", False)),
            int(data.get("rebar_ready_for_pour", False)),
            data.get("comment_ru"),
            data.get("comment_uz"),
            data.get("comment_en"),
            data.get("comment_tr"),
        ))
        await db.commit()
        return cur.lastrowid


async def add_entry_defect(entry_id: int, defect_id: int | None,
                           custom_ru: str | None = None, custom_uz: str | None = None,
                           custom_en: str | None = None, custom_tr: str | None = None):
    async with await get_db() as db:
        await db.execute("""
            INSERT INTO entry_defects (entry_id, defect_id, custom_text_ru, custom_text_uz, custom_text_en, custom_text_tr)
            VALUES (?,?,?,?,?,?)
        """, (entry_id, defect_id, custom_ru, custom_uz, custom_en, custom_tr))
        await db.commit()


async def get_shift_with_entries(shift_id: int):
    async with await get_db() as db:
        cur = await db.execute("""
            SELECT s.*, p.name as project_name, sp.name as subproject_name,
                   u.full_name as engineer_name, u.username as engineer_username
            FROM shifts s
            JOIN projects p ON s.project_id = p.id
            JOIN subprojects sp ON s.subproject_id = sp.id
            JOIN users u ON s.user_id = u.telegram_id
            WHERE s.id = ?
        """, (shift_id,))
        shift = await cur.fetchone()
        if not shift:
            return None, []

        ecur = await db.execute("""
            SELECT e.*, st.name_ru as st_name_ru, st.name_uz as st_name_uz,
                   st.name_en as st_name_en, st.name_tr as st_name_tr, st.icon as st_icon,
                   pm.name_ru as pm_name_ru, pm.name_uz as pm_name_uz,
                   pm.name_en as pm_name_en, pm.name_tr as pm_name_tr,
                   pt.name_ru as pump_name_ru, pt.name_uz as pump_name_uz,
                   pt.name_en as pump_name_en, pt.name_tr as pump_name_tr
            FROM entries e
            LEFT JOIN structure_types st ON e.structure_type_id = st.id
            LEFT JOIN pour_methods pm ON e.pour_method_id = pm.id
            LEFT JOIN pump_types pt ON e.pump_type_id = pt.id
            WHERE e.shift_id = ?
            ORDER BY e.id
        """, (shift_id,))
        entries = await ecur.fetchall()

        # Load defects for each entry
        result_entries = []
        for entry in entries:
            entry_dict = dict(entry)
            dcur = await db.execute("""
                SELECT ed.*, dt.name_ru, dt.name_uz, dt.name_en, dt.name_tr
                FROM entry_defects ed
                LEFT JOIN defect_types dt ON ed.defect_id = dt.id
                WHERE ed.entry_id = ?
            """, (entry["id"],))
            entry_dict["defects"] = await dcur.fetchall()
            result_entries.append(entry_dict)

        return dict(shift), result_entries


async def get_user_shifts(user_id: int, limit: int = 20):
    async with await get_db() as db:
        cur = await db.execute("""
            SELECT s.id, s.shift_type, s.started_at, s.finished_at,
                   p.name as project_name, sp.name as subproject_name
            FROM shifts s
            JOIN projects p ON s.project_id = p.id
            JOIN subprojects sp ON s.subproject_id = sp.id
            WHERE s.user_id = ? AND s.finished_at IS NOT NULL
            ORDER BY s.started_at DESC
            LIMIT ?
        """, (user_id, limit))
        return await cur.fetchall()


async def get_all_shifts(limit: int = 50):
    async with await get_db() as db:
        cur = await db.execute("""
            SELECT s.id, s.shift_type, s.started_at, s.finished_at,
                   p.name as project_name, sp.name as subproject_name,
                   u.full_name as engineer_name
            FROM shifts s
            JOIN projects p ON s.project_id = p.id
            JOIN subprojects sp ON s.subproject_id = sp.id
            JOIN users u ON s.user_id = u.telegram_id
            WHERE s.finished_at IS NOT NULL
            ORDER BY s.started_at DESC
            LIMIT ?
        """, (limit,))
        return await cur.fetchall()


async def get_last_shift(user_id: int):
    """Get the last completed shift with its entries for 'like yesterday' feature."""
    async with await get_db() as db:
        cur = await db.execute("""
            SELECT id FROM shifts
            WHERE user_id = ? AND finished_at IS NOT NULL
            ORDER BY started_at DESC LIMIT 1
        """, (user_id,))
        row = await cur.fetchone()
        if not row:
            return None, []
        return await get_shift_with_entries(row["id"])
