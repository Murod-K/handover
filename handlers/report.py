from aiogram import Router, F
from aiogram.types import CallbackQuery
from aiogram.fsm.context import FSMContext

from data.translations import t
from repositories.user_repo import get_language
from repositories.shift_repo import get_active_shift, finish_shift, get_shift_entries
from services.report_service import generate_report
from states import EntryStates

router = Router()


@router.callback_query(F.data == "entry:finish_shift")
async def on_finish_shift(callback: CallbackQuery, state: FSMContext):
    lang = await get_language(callback.from_user.id)
    data = await state.get_data()
    shift_id = data.get("shift_id")

    if not shift_id:
        await callback.answer("No active shift", show_alert=True)
        return

    entries = await get_shift_entries(shift_id)
    if not entries:
        await callback.answer(t("no_entries", lang), show_alert=True)
        return

    await callback.message.edit_text(t("shift_finished", lang))

    shift = await get_active_shift(callback.from_user.id)
    if shift:
        await finish_shift(shift["id"])

        report = await generate_report(shift, lang)
        # Send report in chunks if needed
        if len(report) > 4000:
            chunks = [report[i:i+4000] for i in range(0, len(report), 4000)]
            for chunk in chunks:
                await callback.message.answer(chunk, parse_mode="Markdown")
        else:
            await callback.message.answer(report, parse_mode="Markdown")

    await state.clear()
    await callback.answer()
