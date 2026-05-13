import logging
from services.database import get_db

logger = logging.getLogger(__name__)

# In-memory cache
_cache: dict = {}


def invalidate_cache():
    _cache.clear()


# ─── Projects ────────────────────────────────────────────────────────────────

async def get_projects():
    if "projects" not in _cache:
        async with await get_db() as db:
            cur = await db.execute("SELECT * FROM projects WHERE is_active=1 ORDER BY name")
            _cache["projects"] = await cur.fetchall()
    return _cache["projects"]


async def add_project(name: str):
    async with await get_db() as db:
        await db.execute("INSERT INTO projects (name) VALUES (?)", (name,))
        await db.commit()
    invalidate_cache()


async def delete_project(project_id: int):
    async with await get_db() as db:
        await db.execute("UPDATE projects SET is_active=0 WHERE id=?", (project_id,))
        await db.commit()
    invalidate_cache()


# ─── Subprojects ─────────────────────────────────────────────────────────────

async def get_subprojects(project_id: int):
    key = f"subprojects_{project_id}"
    if key not in _cache:
        async with await get_db() as db:
            cur = await db.execute(
                "SELECT * FROM subprojects WHERE project_id=? AND is_active=1 ORDER BY name",
                (project_id,)
            )
            _cache[key] = await cur.fetchall()
    return _cache[key]


async def add_subproject(project_id: int, name: str):
    async with await get_db() as db:
        await db.execute("INSERT INTO subprojects (project_id, name) VALUES (?,?)", (project_id, name))
        await db.commit()
    invalidate_cache()


async def delete_subproject(sub_id: int):
    async with await get_db() as db:
        await db.execute("UPDATE subprojects SET is_active=0 WHERE id=?", (sub_id,))
        await db.commit()
    invalidate_cache()


# ─── Structure Types ──────────────────────────────────────────────────────────

async def get_structure_types():
    if "structure_types" not in _cache:
        async with await get_db() as db:
            cur = await db.execute("SELECT * FROM structure_types WHERE is_active=1 ORDER BY name_ru")
            _cache["structure_types"] = await cur.fetchall()
    return _cache["structure_types"]


async def add_structure_type(code: str, icon: str, name_ru: str, name_uz: str, name_en: str, name_tr: str):
    async with await get_db() as db:
        await db.execute("""
            INSERT INTO structure_types (code, icon, name_ru, name_uz, name_en, name_tr)
            VALUES (?,?,?,?,?,?)
        """, (code, icon, name_ru, name_uz, name_en, name_tr))
        await db.commit()
    invalidate_cache()


async def delete_structure_type(st_id: int):
    async with await get_db() as db:
        await db.execute("UPDATE structure_types SET is_active=0 WHERE id=?", (st_id,))
        await db.commit()
    invalidate_cache()


# ─── Defect Types ─────────────────────────────────────────────────────────────

async def get_defect_types():
    if "defect_types" not in _cache:
        async with await get_db() as db:
            cur = await db.execute("SELECT * FROM defect_types WHERE is_active=1 ORDER BY name_ru")
            _cache["defect_types"] = await cur.fetchall()
    return _cache["defect_types"]


async def add_defect_type(code: str, name_ru: str, name_uz: str, name_en: str, name_tr: str):
    async with await get_db() as db:
        await db.execute("""
            INSERT INTO defect_types (code, name_ru, name_uz, name_en, name_tr)
            VALUES (?,?,?,?,?)
        """, (code, name_ru, name_uz, name_en, name_tr))
        await db.commit()
    invalidate_cache()


async def delete_defect_type(d_id: int):
    async with await get_db() as db:
        await db.execute("UPDATE defect_types SET is_active=0 WHERE id=?", (d_id,))
        await db.commit()
    invalidate_cache()


# ─── Pour Methods ─────────────────────────────────────────────────────────────

async def get_pour_methods():
    if "pour_methods" not in _cache:
        async with await get_db() as db:
            cur = await db.execute("SELECT * FROM pour_methods WHERE is_active=1 ORDER BY name_ru")
            _cache["pour_methods"] = await cur.fetchall()
    return _cache["pour_methods"]


async def add_pour_method(code: str, icon: str, name_ru: str, name_uz: str, name_en: str, name_tr: str, requires_pump: int):
    async with await get_db() as db:
        await db.execute("""
            INSERT INTO pour_methods (code, icon, name_ru, name_uz, name_en, name_tr, requires_pump)
            VALUES (?,?,?,?,?,?,?)
        """, (code, icon, name_ru, name_uz, name_en, name_tr, requires_pump))
        await db.commit()
    invalidate_cache()


async def delete_pour_method(pm_id: int):
    async with await get_db() as db:
        await db.execute("UPDATE pour_methods SET is_active=0 WHERE id=?", (pm_id,))
        await db.commit()
    invalidate_cache()


# ─── Pump Types ───────────────────────────────────────────────────────────────

async def get_pump_types():
    if "pump_types" not in _cache:
        async with await get_db() as db:
            cur = await db.execute("SELECT * FROM pump_types WHERE is_active=1 ORDER BY name_ru")
            _cache["pump_types"] = await cur.fetchall()
    return _cache["pump_types"]


async def add_pump_type(code: str, name_ru: str, name_uz: str, name_en: str, name_tr: str):
    async with await get_db() as db:
        await db.execute("""
            INSERT INTO pump_types (code, name_ru, name_uz, name_en, name_tr)
            VALUES (?,?,?,?,?)
        """, (code, name_ru, name_uz, name_en, name_tr))
        await db.commit()
    invalidate_cache()


async def delete_pump_type(pt_id: int):
    async with await get_db() as db:
        await db.execute("UPDATE pump_types SET is_active=0 WHERE id=?", (pt_id,))
        await db.commit()
    invalidate_cache()


def get_name(row, lang: str) -> str:
    """Get localized name from a reference row."""
    col = f"name_{lang}"
    try:
        return row[col] or row["name_ru"]
    except (IndexError, KeyError):
        return row["name_ru"]
