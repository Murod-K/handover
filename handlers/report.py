import logging
import tempfile
import os
from aiogram import Router, F
from aiogram.types import CallbackQuery, Message, BufferedInputFile
from aiogram.fsm.context import FSMContext

from data.translations import t
from keyboards.builders import main_menu_keyboard, paginated_keyboard
from repositories.user_repo import get_user
from repositories.shift_repo import get_shift_with_entries, get_user_shifts, get_all_shifts
from services.report_service import generate_html
from services.access_service import is_admin, is_senior_or_above, check_access

logger = logging.getLogger(__name__)
router = Router()


async def generate_and_send_report(message: Message, user_id: int, shift_id: int, lang: str):
    shift, entries = await get_shift_with_entries(shift_id)
    if not shift:
        await message.answer(t("no_reports", lang))
        return

    html = generate_html(shift, entries, lang)
    filename = f"handover_{shift_id}_{lang}.html"
    data = html.encode("utf-8")
    file = BufferedInputFile(data, filename=filename)

    senior = await is_senior_or_above(user_id)
    admin = await is_admin(user_id)
    await message.answer_document(
        file,
        caption=t("report_ready", lang),
        reply_markup=main_menu_keyboard(lang, senior, admin)
    )


@router.callback_query(F.data == "reports:my")
async def my_reports(callback: CallbackQuery, state: FSMContext):
    allowed, _ = await check_access(callback.from_user.id)
    if not allowed:
        await callback.answer(t("no_access", "ru"), show_alert=True)
        return
    user = await get_user(callback.from_user.id)
    lang = user["lang"]
    shifts = await get_user_shifts(callback.from_user.id)
    if not shifts:
        await callback.message.edit_text(t("no_reports", lang))
        await callback.answer()
        return
    await _show_shift_list(callback, shifts, lang, "report_my")


@router.callback_query(F.data == "reports:all")
async def all_reports(callback: CallbackQuery, state: FSMContext):
    allowed, _ = await check_access(callback.from_user.id)
    if not allowed:
        await callback.answer(t("no_access", "ru"), show_alert=True)
        return
    senior = await is_senior_or_above(callback.from_user.id)
    admin = await is_admin(callback.from_user.id)
    if not (senior or admin):
        await callback.answer(t("no_access", "ru"), show_alert=True)
        return
    user = await get_user(callback.from_user.id)
    lang = user["lang"]
    shifts = await get_all_shifts()
    if not shifts:
        await callback.message.edit_text(t("no_reports", lang))
        await callback.answer()
        return
    await _show_shift_list(callback, shifts, lang, "report_all")


async def _show_shift_list(callback: CallbackQuery, shifts, lang: str, prefix: str):
    from aiogram.utils.keyboard import InlineKeyboardBuilder
    from aiogram.types import InlineKeyboardButton
    kb = InlineKeyboardBuilder()
    for s in shifts[:15]:
        date_str = str(s["started_at"])[:16] if s["started_at"] else ""
        eng = f" [{s['engineer_name']}]" if "engineer_name" in s.keys() else ""
        label = f"{date_str} | {s['project_name']} / {s['subproject_name']}{eng}"
        kb.button(text=label, callback_data=f"{prefix}:{s['id']}")
    kb.button(text=t("btn_back", lang), callback_data="menu:main")
    kb.adjust(1)
    await callback.message.edit_text(t("choose_report", lang), reply_markup=kb.as_markup())
    await callback.answer()


@router.callback_query(F.data.startswith("report_my:"))
async def open_my_report(callback: CallbackQuery):
    user = await get_user(callback.from_user.id)
    lang = user["lang"]
    shift_id = int(callback.data.split(":")[1])
    await callback.message.answer(t("generating_report", lang))
    await generate_and_send_report(callback.message, callback.from_user.id, shift_id, lang)
    await callback.answer()


@router.callback_query(F.data.startswith("report_all:"))
async def open_all_report(callback: CallbackQuery):
    user = await get_user(callback.from_user.id)
    lang = user["lang"]
    shift_id = int(callback.data.split(":")[1])
    await callback.message.answer(t("generating_report", lang))
    await generate_and_send_report(callback.message, callback.from_user.id, shift_id, lang)
    await callback.answer()
