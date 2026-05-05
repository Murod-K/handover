import os
from dataclasses import dataclass


@dataclass
class Config:
    BOT_TOKEN: str = os.getenv("BOT_TOKEN", "8752565922:AAHlg4rk_BNba5qZtSPWLod_m3XY1nRKU6Y")
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "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")
    DB_PATH: str = os.getenv("DB_PATH", "handover.db")
    DEFAULT_LANGUAGE: str = "ru"
