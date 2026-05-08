import aiosqlite
import json
from datetime import datetime
from config import Config

DB_PATH = Config().DB_PATH


async def init_db():
    async with aiosqlite.connect(DB_PATH) as db:
        await db.executescript("""
        CREATE TABLE IF NOT EXISTS users (
            telegram_id INTEGER PRIMARY KEY,
            username TEXT,
            language TEXT DEFAULT 'ru',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS projects (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            is_active BOOLEAN DEFAULT 1
        );

        CREATE TABLE IF NOT EXISTS subprojects (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            project_id INTEGER REFERENCES projects(id),
            name TEXT NOT NULL
        );

        CREATE TABLE IF NOT EXISTS shifts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            telegram_id INTEGER REFERENCES users(telegram_id),
            project_id INTEGER REFERENCES projects(id),
            subproject_id INTEGER REFERENCES subprojects(id),
            shift_type TEXT NOT NULL,
            started_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            finished_at TIMESTAMP,
            is_active BOOLEAN DEFAULT 1
        );

        CREATE TABLE IF NOT EXISTS entries (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            shift_id INTEGER REFERENCES shifts(id),
            structure_type TEXT NOT NULL,
            structure_name TEXT NOT NULL,
            natura_status TEXT NOT NULL,
            rebar_status TEXT NOT NULL,
            concrete_plan TEXT NOT NULL,
            concrete_available TEXT,
            formwork_ready TEXT,
            waterproof_ready TEXT,
            rebar_ready_for_pour TEXT,
            concrete_volume REAL,
            pour_method TEXT,
            pump_type TEXT,
            pump_logistics TEXT,
            rebar_comment TEXT,
            rebar_comment_translated TEXT,
            entry_comment TEXT,
            entry_comment_translated TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS entry_defects (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            entry_id INTEGER REFERENCES entries(id),
            defect_code TEXT NOT NULL,
            custom_text TEXT
        );

        CREATE TABLE IF NOT EXISTS translations_cache (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            original_text TEXT NOT NULL,
            source_lang TEXT,
            translated_texts TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );

        -- Seed projects if empty
        INSERT OR IGNORE INTO projects (id, name) VALUES (1, 'Объект A — Башня 1');
        INSERT OR IGNORE INTO projects (id, name) VALUES (2, 'Объект B — Жилой комплекс');
        INSERT OR IGNORE INTO projects (id, name) VALUES (3, 'Объект C — Офисный центр');

        INSERT OR IGNORE INTO subprojects (id, project_id, name) VALUES (1, 1, 'Блок А / Секция 1');
        INSERT OR IGNORE INTO subprojects (id, project_id, name) VALUES (2, 1, 'Блок Б / Секция 2');
        INSERT OR IGNORE INTO subprojects (id, project_id, name) VALUES (3, 1, 'Подвал');
        INSERT OR IGNORE INTO subprojects (id, project_id, name) VALUES (4, 2, 'Корпус 1');
        INSERT OR IGNORE INTO subprojects (id, project_id, name) VALUES (5, 2, 'Корпус 2');
        INSERT OR IGNORE INTO subprojects (id, project_id, name) VALUES (6, 3, 'Офисная зона');
        INSERT OR IGNORE INTO subprojects (id, project_id, name) VALUES (7, 3, 'Паркинг');
        """)
        await db.commit()


async def get_db():
    return aiosqlite.connect(DB_PATH)
