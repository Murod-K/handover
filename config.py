import os

class Config:
    BOT_TOKEN:      str = os.getenv("BOT_TOKEN", "")
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
    DB_PATH:        str = os.getenv("DB_PATH", "handover.db")
