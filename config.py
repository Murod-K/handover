import os
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN: str = os.getenv("BOT_TOKEN", "")
OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
DB_PATH: str = os.getenv("DB_PATH", "/tmp/handover_v3.db")
ADMIN_TG_ID: int = int(os.getenv("ADMIN_TG_ID", "0"))

FSM_TIMEOUT_MINUTES: int = 30
SUPPORTED_LANGS = ["ru", "uz", "en", "tr"]
