from aiogram import Router, F
from aiogram.types import CallbackQuery
from aiogram.fsm.context import FSMContext

from data.translations import t
from repositories.user_repo import get_language
from repositories.shift_repo import get_entries, finish_shift, get_active_shift
from services.report_service import generate_report
from handlers.start import show_main_menu

router = Router()


async def send_report(callback: CallbackQuery, state: FSMContext):
    lang = await get_language(callback.from_user.id)
    data = await state.get_data()
    shift_id = data.get("shift_id")

    entries = await get_entries(shift_id) if shift_id else []
    if not entries:
        await callback.answer(t("no_entries", lang), show_alert=True)
        return

    await callback.message.edit_text(t("generating_report", lang))
    await finish_shift(shift_id)

    report = await generate_report(shift_id, lang)

    # Send in chunks if needed
    if len(report) > 4096:
        chunks = [report[i:i+4096] for i in range(0, len(report), 4096)]
        await callback.message.delete()
        for chunk in chunks:
            await callback.message.answer(chunk, parse_mode="Markdown")
    else:
        await callback.message.edit_text(report, parse_mode="Markdown")

    await state.clear()
    # Return to main menu
    await show_main_menu(callback, lang, callback.from_user.id, state)
    await callback.answer()


@router.callback_query(F.data == "menu:reports")
async def on_my_reports(callback: CallbackQuery, state: FSMContext):
    from repositories.shift_repo import get_recent_shifts
    lang = await get_language(callback.from_user.id)
    shifts = await get_recent_shifts(callback.from_user.id, limit=5)

    if not shifts:
        await callback.answer("📭 Нет завершённых смен", show_alert=True)
        return

    from aiogram.utils.keyboard import InlineKeyboardBuilder
    kb = InlineKeyboardBuilder()
    for s in shifts:
        dt = (s.get("finished_at") or "")[:10]
        label = f"{s['shift_type']} | {s.get('project_name','?')} | {dt}"
        kb.button(text=label, callback_data=f"view_report:{s['id']}")
    from data.translations import t
    kb.button(text=t("btn_back", lang), callback_data="menu:main")
    kb.adjust(1)
    await callback.message.edit_text(
        "📊 *Последние смены:*",
        reply_markup=kb.as_markup(), parse_mode="Markdown"
    )
    await callback.answer()


@router.callback_query(F.data.startswith("view_report:"))
async def on_view_report(callback: CallbackQuery, state: FSMContext):
    shift_id = int(callback.data.split(":")[1])
    lang = await get_language(callback.from_user.id)
    report = await generate_report(shift_id, lang)
    if len(report) > 4096:
        chunks = [report[i:i+4096] for i in range(0, len(report), 4096)]
        await callback.message.delete()
        for chunk in chunks:
            await callback.message.answer(chunk, parse_mode="Markdown")
    else:
        await callback.message.edit_text(report, parse_mode="Markdown")
    await callback.answer()
