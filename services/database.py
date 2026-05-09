import aiosqlite
import os

DB_PATH = os.getenv("DB_PATH", "handover.db")


async def init_db():
    async with aiosqlite.connect(DB_PATH) as db:
        await db.executescript("""
        PRAGMA foreign_keys = ON;

        -- ── USERS ──
        CREATE TABLE IF NOT EXISTS users (
            telegram_id INTEGER PRIMARY KEY,
            username    TEXT,
            full_name   TEXT,
            language    TEXT DEFAULT 'ru',
            role        TEXT DEFAULT 'engineer',
            created_at  TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );

        -- ── FLEXIBLE REFERENCE TABLES ──

        CREATE TABLE IF NOT EXISTS projects (
            id         INTEGER PRIMARY KEY AUTOINCREMENT,
            name       TEXT NOT NULL,
            is_active  INTEGER DEFAULT 1,
            sort_order INTEGER DEFAULT 0
        );

        CREATE TABLE IF NOT EXISTS subprojects (
            id         INTEGER PRIMARY KEY AUTOINCREMENT,
            project_id INTEGER REFERENCES projects(id) ON DELETE CASCADE,
            name       TEXT NOT NULL,
            is_active  INTEGER DEFAULT 1,
            sort_order INTEGER DEFAULT 0
        );

        CREATE TABLE IF NOT EXISTS structure_types (
            id         INTEGER PRIMARY KEY AUTOINCREMENT,
            code       TEXT NOT NULL UNIQUE,
            icon       TEXT DEFAULT '🏗',
            name_ru    TEXT NOT NULL,
            name_uz    TEXT,
            name_en    TEXT,
            name_tr    TEXT,
            is_active  INTEGER DEFAULT 1,
            sort_order INTEGER DEFAULT 0
        );

        CREATE TABLE IF NOT EXISTS defect_types (
            id         INTEGER PRIMARY KEY AUTOINCREMENT,
            code       TEXT NOT NULL UNIQUE,
            name_ru    TEXT NOT NULL,
            name_uz    TEXT,
            name_en    TEXT,
            name_tr    TEXT,
            is_active  INTEGER DEFAULT 1,
            sort_order INTEGER DEFAULT 0
        );

        CREATE TABLE IF NOT EXISTS pour_methods (
            id              INTEGER PRIMARY KEY AUTOINCREMENT,
            code            TEXT NOT NULL UNIQUE,
            icon            TEXT DEFAULT '🚛',
            name_ru         TEXT NOT NULL,
            name_uz         TEXT,
            name_en         TEXT,
            name_tr         TEXT,
            requires_pump   INTEGER DEFAULT 0,
            is_active       INTEGER DEFAULT 1,
            sort_order      INTEGER DEFAULT 0
        );

        CREATE TABLE IF NOT EXISTS pump_types (
            id         INTEGER PRIMARY KEY AUTOINCREMENT,
            code       TEXT NOT NULL UNIQUE,
            name_ru    TEXT NOT NULL,
            name_uz    TEXT,
            name_en    TEXT,
            name_tr    TEXT,
            is_active  INTEGER DEFAULT 1,
            sort_order INTEGER DEFAULT 0
        );

        -- ── SHIFTS & ENTRIES ──

        CREATE TABLE IF NOT EXISTS shifts (
            id             INTEGER PRIMARY KEY AUTOINCREMENT,
            telegram_id    INTEGER REFERENCES users(telegram_id),
            project_id     INTEGER REFERENCES projects(id),
            subproject_id  INTEGER REFERENCES subprojects(id),
            shift_type     TEXT NOT NULL,
            started_at     TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            finished_at    TIMESTAMP,
            is_active      INTEGER DEFAULT 1
        );

        CREATE TABLE IF NOT EXISTS entries (
            id                      INTEGER PRIMARY KEY AUTOINCREMENT,
            shift_id                INTEGER REFERENCES shifts(id),
            structure_type_id       INTEGER REFERENCES structure_types(id),
            structure_name          TEXT NOT NULL,
            natura_status           TEXT NOT NULL,
            rebar_status            TEXT NOT NULL,
            concrete_plan           TEXT NOT NULL,
            pour_method_id          INTEGER REFERENCES pour_methods(id),
            pump_type_id            INTEGER REFERENCES pump_types(id),
            pump_logistics          TEXT,
            concrete_volume         REAL,
            formwork_ready          TEXT,
            waterproof_ready        TEXT,
            rebar_ready_for_pour    TEXT,
            comment                 TEXT,
            comment_ru              TEXT,
            comment_uz              TEXT,
            comment_en              TEXT,
            comment_tr              TEXT,
            created_at              TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS entry_defects (
            id           INTEGER PRIMARY KEY AUTOINCREMENT,
            entry_id     INTEGER REFERENCES entries(id) ON DELETE CASCADE,
            defect_id    INTEGER REFERENCES defect_types(id),
            custom_text  TEXT
        );

        -- ── SEED REFERENCE DATA ──

        INSERT OR IGNORE INTO projects (id, name) VALUES
            (1, 'Объект A — Башня 1'),
            (2, 'Объект B — Жилой комплекс'),
            (3, 'Объект C — Офисный центр');

        INSERT OR IGNORE INTO subprojects (id, project_id, name) VALUES
            (1, 1, 'Секция 1 / Блок А'),
            (2, 1, 'Секция 2 / Блок Б'),
            (3, 1, 'Подвал / Паркинг'),
            (4, 2, 'Корпус 1'),
            (5, 2, 'Корпус 2'),
            (6, 3, 'Офисная зона'),
            (7, 3, 'Паркинг');

        INSERT OR IGNORE INTO structure_types (code, icon, name_ru, name_uz, name_en, name_tr) VALUES
            ('COLUMN',     '🏛', 'Колонна',     'Ustun',       'Column',     'Kolon'),
            ('WALL',       '🧱', 'Стена',       'Devor',       'Wall',       'Duvar'),
            ('SLAB',       '⬛', 'Перекрытие',  'Tom yopma',   'Slab',       'Döşeme'),
            ('BEAM',       '📐', 'Балка',       'Balka',       'Beam',       'Kiriş'),
            ('FOUNDATION', '🪨', 'Фундамент',   'Poydevor',    'Foundation', 'Temel'),
            ('STAIRCASE',  '🪜', 'Лестница',    'Zinapoya',    'Staircase',  'Merdiven'),
            ('MONOLITH',   '🔷', 'Монолит',     'Monolit',     'Monolith',   'Monolit');

        INSERT OR IGNORE INTO defect_types (code, name_ru, name_uz, name_en, name_tr) VALUES
            ('NO_COVER',          'Нет защитного слоя',     'Himoya qatlami yo''q',      'No concrete cover',      'Pas payı yok'),
            ('MISSING_TIES',      'Нехватка хомутов',       'Xomutlar yetishmaydi',      'Missing stirrups',       'Etriye eksik'),
            ('MISSING_BOLTS',     'Нехватка шпилек',        'Shpilkalar yetishmaydi',    'Missing bolts/studs',    'Civata eksik'),
            ('WRONG_SPACING',     'Нарушение шага',         'Qadam buzilgan',            'Wrong bar spacing',      'Aralık hatası'),
            ('FRAME_SHIFT',       'Смещение каркаса',       'Karkasning siljishi',       'Frame displacement',     'Kafes kayması'),
            ('BINDING_INCOMPLETE','Не завершена вязка',     'Bog''lash tugallanmagan',   'Binding incomplete',     'Bağlama eksik'),
            ('GEODESY_NOT_READY', 'Геодезия не готова',     'Geodeziya tayyor emas',     'Geodesy not ready',      'Jeodezi hazır değil'),
            ('NO_CLEANING',       'Нет очистки (оттирки)',  'Tozalash yo''q',            'No cleaning done',       'Temizleme yok'),
            ('FORMWORK_DEFECT',   'Дефект опалубки',        'Qolip nuqsoni',             'Formwork defect',        'Kalıp kusuru'),
            ('WATERPROOF_ISSUE',  'Проблема гидроизоляции', 'Gidroizolyatsiya muammosi', 'Waterproofing issue',    'Su yalıtımı sorunu'),
            ('CUSTOM',            '✏️ Свой дефект',          '✏️ Boshqa nuqson',          '✏️ Custom defect',       '✏️ Özel kusur');

        INSERT OR IGNORE INTO pour_methods (code, icon, name_ru, name_uz, name_en, name_tr, requires_pump) VALUES
            ('STATIONARY_PUMP', '🏗', 'Стационарный насос',  'Statsionar nasos',  'Stationary pump', 'Sabit pompa',  1),
            ('MOBILE_PUMP',     '🚛', 'Мобильный насос',     'Mobil nasos',       'Mobile pump',     'Mobil pompa',  1),
            ('CRANE_BUCKET',    '🏗', 'Кран + бадья',        'Kran + bak',        'Crane + bucket',  'Vinç + kova',  0),
            ('MANUAL',          '👷', 'Вручную',             'Qo''lda',           'Manual',          'Elle',         0),
            ('CONVEYOR',        '⚙️', 'Ленточный конвейер',  'Lenta konveyer',    'Belt conveyor',   'Bant konveyör',0);

        INSERT OR IGNORE INTO pump_types (code, name_ru, name_uz, name_en, name_tr) VALUES
            ('SPIDER_32_4', 'Spider 32+4',  'Spider 32+4',  'Spider 32+4',  'Spider 32+4'),
            ('PUMP_20_4',   'Насос 20+4',   'Nasos 20+4',   'Pump 20+4',    'Pompa 20+4'),
            ('PUMP_36_4',   'Насос 36+4',   'Nasos 36+4',   'Pump 36+4',    'Pompa 36+4'),
            ('BOOM_42',     'Стрела 42м',   'Strel 42m',    'Boom 42m',     'Bom 42m'),
            ('OTHER',       'Другой',       'Boshqa',       'Other',        'Diğer');
        """)
        await db.commit()


async def get_db():
    return aiosqlite.connect(DB_PATH)
