import logging
from enums import UserRole
from repositories.user_repo import get_user

logger = logging.getLogger(__name__)


async def get_user_lang(telegram_id: int) -> str:
    user = await get_user(telegram_id)
    return user["lang"] if user else "ru"


async def check_access(telegram_id: int) -> tuple[bool, str | None]:
    """Returns (allowed, reason). reason is None if allowed."""
    user = await get_user(telegram_id)
    if not user:
        return False, "not_registered"
    if not user["is_active"]:
        return False, "blocked"
    return True, None


async def is_admin(telegram_id: int) -> bool:
    user = await get_user(telegram_id)
    return bool(user and user["role"] == UserRole.ADMIN)


async def is_senior_or_above(telegram_id: int) -> bool:
    user = await get_user(telegram_id)
    return bool(user and user["role"] in (UserRole.ADMIN, UserRole.SENIOR))
