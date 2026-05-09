import aiosqlite
import os

DB_PATH = os.getenv("DB_PATH", "handover.db")


def _lang_col(lang: str) -> str:
    return f"name_{lang}" if lang in ("ru", "uz", "en", "tr") else "name_ru"


async def get_all(table: str, lang: str = "ru", project_id: int = None) -> list[dict]:
    col = _lang_col(lang)
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        if table == "subprojects" and project_id:
            q = f"""SELECT id, {col} AS name, is_active FROM {table}
                    WHERE project_id=? AND is_active=1 ORDER BY sort_order, id"""
            rows = await (await db.execute(q, (project_id,))).fetchall()
        elif table == "projects":
            q = f"SELECT id, name, is_active FROM {table} WHERE is_active=1 ORDER BY sort_order, id"
            rows = await (await db.execute(q)).fetchall()
        else:
            q = f"""SELECT id, {col} AS name, is_active
                    FROM {table} WHERE is_active=1 ORDER BY sort_order, id"""
            rows = await (await db.execute(q)).fetchall()
        return [dict(r) for r in rows]


async def get_item(table: str, item_id: int) -> dict | None:
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        row = await (await db.execute(
            f"SELECT * FROM {table} WHERE id=?", (item_id,)
        )).fetchone()
        return dict(row) if row else None


async def get_item_by_code(table: str, code: str) -> dict | None:
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        row = await (await db.execute(
            f"SELECT * FROM {table} WHERE code=?", (code,)
        )).fetchone()
        return dict(row) if row else None


async def add_project(name: str) -> int:
    async with aiosqlite.connect(DB_PATH) as db:
        cur = await db.execute("INSERT INTO projects (name) VALUES (?)", (name,))
        await db.commit()
        return cur.lastrowid


async def add_subproject(project_id: int, name: str) -> int:
    async with aiosqlite.connect(DB_PATH) as db:
        cur = await db.execute(
            "INSERT INTO subprojects (project_id, name) VALUES (?,?)", (project_id, name)
        )
        await db.commit()
        return cur.lastrowid


async def add_ref_item(table: str, code: str, name_ru: str,
                        name_uz: str = None, name_en: str = None,
                        name_tr: str = None, extra: dict = None) -> int:
    cols = "code, name_ru, name_uz, name_en, name_tr"
    vals = "?,?,?,?,?"
    params = [code, name_ru, name_uz or name_ru, name_en or name_ru, name_tr or name_ru]
    if extra:
        for k, v in extra.items():
            cols += f", {k}"
            vals += ", ?"
            params.append(v)
    async with aiosqlite.connect(DB_PATH) as db:
        cur = await db.execute(
            f"INSERT INTO {table} ({cols}) VALUES ({vals})", params
        )
        await db.commit()
        return cur.lastrowid


async def delete_item(table: str, item_id: int):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(f"UPDATE {table} SET is_active=0 WHERE id=?", (item_id,))
        await db.commit()


async def get_pour_method(pm_id: int) -> dict | None:
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        row = await (await db.execute(
            "SELECT * FROM pour_methods WHERE id=?", (pm_id,)
        )).fetchone()
        return dict(row) if row else None
