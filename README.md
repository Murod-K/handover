# Handover Bot v3 — Система передачи смены

Telegram-бот для стандартизированной передачи смены на строительной площадке.

## Стек
- Python 3.11
- aiogram 3.x
- aiosqlite
- openai (GPT-4o-mini)
- python-dotenv

## Быстрый старт

### 1. Клонировать / распаковать проект
```bash
cd handover_v3
```

### 2. Создать виртуальное окружение
```bash
python3.11 -m venv venv
source venv/bin/activate   # Linux/Mac
venv\Scripts\activate      # Windows
```

### 3. Установить зависимости
```bash
pip install -r requirements.txt
```

### 4. Настроить переменные окружения
```bash
cp .env.example .env
# Отредактировать .env:
# BOT_TOKEN      — токен от @BotFather
# OPENAI_API_KEY — ключ OpenAI
# DB_PATH        — путь к БД (по умолчанию /tmp/handover_v3.db)
# ADMIN_TG_ID    — ваш Telegram ID (узнать у @userinfobot)
```

### 5. Запустить
```bash
python main.py
```

---

## Деплой на Render

1. Создать **Web Service** (или Background Worker) → Python
2. Build Command: `pip install -r requirements.txt`
3. Start Command: `python main.py`
4. Environment Variables — добавить все 4 переменные из `.env.example`
5. Disk: подключить Persistent Disk, смонтировать в `/data`, установить `DB_PATH=/data/handover_v3.db`

---

## Роли

| Роль | Возможности |
|------|-------------|
| `admin` | Всё + управление пользователями, справочниками, кодами |
| `senior` | Создание смен, просмотр всех отчётов |
| `engineer` | Создание смен, просмотр своих отчётов |

## Команды администратора

| Команда | Описание |
|---------|----------|
| `/gencode 5` | Сгенерировать 5 инвайт-кодов |
| `/users` | Список всех пользователей |
| `/block @username` | Заблокировать пользователя |
| `/role @username senior` | Изменить роль |

Также доступна кнопка **Администрирование** в главном меню.

---

## Структура проекта

```
handover_v3/
├── main.py                 — точка входа, polling, FSM-таймер
├── config.py               — переменные окружения
├── enums.py                — коды статусов
├── states.py               — FSM состояния
├── handlers/
│   ├── auth.py             — /start, инвайт-код, выбор языка
│   ├── menu.py             — главное меню
│   ├── shift.py            — ввод смены (полный FSM)
│   ├── report.py           — генерация и отправка HTML
│   └── admin.py            — управление справочниками и пользователями
├── services/
│   ├── database.py         — инициализация БД, миграции
│   ├── gpt_service.py      — переводы через GPT-4o-mini
│   ├── report_service.py   — генерация HTML-отчёта
│   └── access_service.py   — проверка ролей
├── repositories/
│   ├── user_repo.py        — CRUD пользователей и инвайт-кодов
│   ├── ref_repo.py         — CRUD справочников (с кэшем)
│   └── shift_repo.py       — CRUD смен и записей
├── keyboards/
│   └── builders.py         — все клавиатуры
├── data/
│   └── translations.py     — UI-строки на 4 языках
└── .env.example
```

---

## Языки интерфейса
- 🇷🇺 Русский
- 🇺🇿 O'zbek
- 🇬🇧 English
- 🇹🇷 Türkçe

Свободные комментарии автоматически переводятся на все 4 языка через GPT.
При недоступности GPT — комментарий сохраняется на языке ввода.
