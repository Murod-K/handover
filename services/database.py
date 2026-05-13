import aiosqlite
import logging
from config import DB_PATH, ADMIN_TG_ID

logger = logging.getLogger(__name__)


async def get_db() -> aiosqlite.Connection:
    db = await aiosqlite.connect(DB_PATH)
    db.row_factory = aiosqlite.Row
    await db.execute("PRAGMA journal_mode=WAL")
    await db.execute("PRAGMA foreign_keys=ON")
    return db


async def init_db():
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        await db.execute("PRAGMA foreign_keys=ON")

        await db.executescript("""
        CREATE TABLE IF NOT EXISTS users (
            telegram_id INTEGER PRIMARY KEY,
            username TEXT,
            full_name TEXT,
            lang TEXT DEFAULT 'ru',
            role TEXT DEFAULT 'engineer',
            is_active INTEGER DEFAULT 1,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS invite_codes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            code TEXT UNIQUE NOT NULL,
            created_by INTEGER,
            used_by INTEGER,
            used_at TIMESTAMP,
            is_used INTEGER DEFAULT 0
        );

        CREATE TABLE IF NOT EXISTS projects (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            is_active INTEGER DEFAULT 1
        );

        CREATE TABLE IF NOT EXISTS subprojects (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            project_id INTEGER NOT NULL,
            name TEXT NOT NULL,
            is_active INTEGER DEFAULT 1,
            FOREIGN KEY (project_id) REFERENCES projects(id)
        );

        CREATE TABLE IF NOT EXISTS structure_types (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            code TEXT UNIQUE NOT NULL,
            icon TEXT DEFAULT '',
            name_ru TEXT NOT NULL,
            name_uz TEXT NOT NULL,
            name_en TEXT NOT NULL,
            name_tr TEXT NOT NULL,
            is_active INTEGER DEFAULT 1
        );

        CREATE TABLE IF NOT EXISTS defect_types (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            code TEXT UNIQUE NOT NULL,
            name_ru TEXT NOT NULL,
            name_uz TEXT NOT NULL,
            name_en TEXT NOT NULL,
            name_tr TEXT NOT NULL,
            is_active INTEGER DEFAULT 1
        );

        CREATE TABLE IF NOT EXISTS pour_methods (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            code TEXT UNIQUE NOT NULL,
            icon TEXT DEFAULT '',
            name_ru TEXT NOT NULL,
            name_uz TEXT NOT NULL,
            name_en TEXT NOT NULL,
            name_tr TEXT NOT NULL,
            requires_pump INTEGER DEFAULT 0,
            is_active INTEGER DEFAULT 1
        );

        CREATE TABLE IF NOT EXISTS pump_types (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            code TEXT UNIQUE NOT NULL,
            name_ru TEXT NOT NULL,
            name_uz TEXT NOT NULL,
            name_en TEXT NOT NULL,
            name_tr TEXT NOT NULL,
            is_active INTEGER DEFAULT 1
        );

        CREATE TABLE IF NOT EXISTS shifts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            project_id INTEGER NOT NULL,
            subproject_id INTEGER NOT NULL,
            shift_type TEXT NOT NULL,
            started_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            finished_at TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(telegram_id),
            FOREIGN KEY (project_id) REFERENCES projects(id),
            FOREIGN KEY (subproject_id) REFERENCES subprojects(id)
        );

        CREATE TABLE IF NOT EXISTS entries (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            shift_id INTEGER NOT NULL,
            structure_type_id INTEGER,
            structure_name TEXT NOT NULL,
            natura_status TEXT NOT NULL,
            rebar_status TEXT NOT NULL,
            concrete_plan TEXT NOT NULL,
            concrete_available INTEGER DEFAULT 0,
            pour_method_id INTEGER,
            pump_type_id INTEGER,
            pump_logistics TEXT,
            concrete_volume REAL,
            formwork_ready INTEGER DEFAULT 0,
            waterproof_ready INTEGER DEFAULT 0,
            rebar_ready_for_pour INTEGER DEFAULT 0,
            comment_ru TEXT,
            comment_uz TEXT,
            comment_en TEXT,
            comment_tr TEXT,
            FOREIGN KEY (shift_id) REFERENCES shifts(id),
            FOREIGN KEY (structure_type_id) REFERENCES structure_types(id),
            FOREIGN KEY (pour_method_id) REFERENCES pour_methods(id),
            FOREIGN KEY (pump_type_id) REFERENCES pump_types(id)
        );

        CREATE TABLE IF NOT EXISTS entry_defects (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            entry_id INTEGER NOT NULL,
            defect_id INTEGER,
            custom_text_ru TEXT,
            custom_text_uz TEXT,
            custom_text_en TEXT,
            custom_text_tr TEXT,
            FOREIGN KEY (entry_id) REFERENCES entries(id),
            FOREIGN KEY (defect_id) REFERENCES defect_types(id)
        );
        """)

        # Ensure admin user exists if configured
        if ADMIN_TG_ID:
            await db.execute("""
                INSERT OR IGNORE INTO users (telegram_id, username, full_name, lang, role, is_active)
                VALUES (?, 'admin', 'Administrator', 'ru', 'admin', 1)
            """, (ADMIN_TG_ID,))

        # Seed default data if empty
        count = await db.execute("SELECT COUNT(*) FROM structure_types")
        row = await count.fetchone()
        if row[0] == 0:
            await _seed_defaults(db)

        await db.commit()
        logger.info("Database initialized.")


async def _seed_defaults(db: aiosqlite.Connection):
    await db.executemany("""
        INSERT OR IGNORE INTO structure_types (code, icon, name_ru, name_uz, name_en, name_tr)
        VALUES (?,?,?,?,?,?)
    """, [
        ("COLUMN", "🏛", "Колонна", "Ustun", "Column", "Kolon"),
        ("WALL", "🧱", "Стена", "Devor", "Wall", "Duvar"),
        ("SLAB", "⬛", "Плита", "Plita", "Slab", "Döşeme"),
        ("BEAM", "━", "Балка", "Rig", "Beam", "Kiriş"),
        ("FOUNDATION", "🏗", "Фундамент", "Poydevor", "Foundation", "Temel"),
        ("STAIRCASE", "🪜", "Лестница", "Zinapoya", "Staircase", "Merdiven"),
    ])

    await db.executemany("""
        INSERT OR IGNORE INTO defect_types (code, name_ru, name_uz, name_en, name_tr)
        VALUES (?,?,?,?,?)
    """, [
        ("SPACING", "Шаг арматуры не соответствует", "Armatura qadami mos emas", "Rebar spacing non-compliant", "Donatım aralığı uygun değil"),
        ("COVER", "Защитный слой нарушен", "Himoya qatlami buzilgan", "Cover layer violation", "Örtü katmanı ihlali"),
        ("SPLICE", "Стыковка не выполнена", "Birlashtirish bajarilmagan", "Splice not done", "Ek yapılmadı"),
        ("MISSING", "Арматура отсутствует", "Armatura yo'q", "Rebar missing", "Donatım eksik"),
        ("DIAMETER", "Диаметр не соответствует", "Diametr mos emas", "Diameter non-compliant", "Çap uygun değil"),
        ("ANCHOR", "Анкеровка нарушена", "Ankerlash buzilgan", "Anchorage violation", "Ankraj ihlali"),
    ])

    await db.executemany("""
        INSERT OR IGNORE INTO pour_methods (code, icon, name_ru, name_uz, name_en, name_tr, requires_pump)
        VALUES (?,?,?,?,?,?,?)
    """, [
        ("PUMP", "🚛", "Насос", "Nasos", "Pump", "Pompa", 1),
        ("CRANE_BUCKET", "🏗", "Кран + ковш", "Kran + chelak", "Crane + bucket", "Vinç + kova", 0),
        ("MANUAL", "👷", "Вручную", "Qo'lda", "Manual", "Elle", 0),
        ("CHUTE", "📐", "Лоток", "Novcha", "Chute", "Oluk", 0),
    ])

    await db.executemany("""
        INSERT OR IGNORE INTO pump_types (code, name_ru, name_uz, name_en, name_tr)
        VALUES (?,?,?,?,?)
    """, [
        ("STATIONARY", "Стационарный", "Statsionar", "Stationary", "Sabit"),
        ("TRUCK_MOUNTED", "Автобетононасос", "Avtobetonnasos", "Truck-mounted", "Kamyon tipi"),
        ("TRAILER", "Прицепной", "Tirma", "Trailer", "Treyler tipi"),
    ])

    await db.executemany("""
        INSERT OR IGNORE INTO projects (name) VALUES (?)
    """, [("Объект 1",), ("Объект 2",)])

    row = await (await db.execute("SELECT id FROM projects LIMIT 1")).fetchone()
    if row:
        await db.execute("""
            INSERT OR IGNORE INTO subprojects (project_id, name) VALUES (?, ?)
        """, (row["id"], "Блок А"))
        await db.execute("""
            INSERT OR IGNORE INTO subprojects (project_id, name) VALUES (?, ?)
        """, (row["id"], "Блок Б"))
