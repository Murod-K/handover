"""
Entry service.
Collects FSM state data, translates free-text comments via OpenAI,
and persists the entry with full defects list.
"""

import json
from aiogram.fsm.context import FSMContext

from repositories.shift_repo import create_entry, add_entry_defects
from repositories.user_repo import get_language
from services.translation_service import translate_comment
from enums import RebarDefect


async def save_entry(telegram_id: int, state: FSMContext) -> int:
    data = await state.get_data()
    lang = await get_language(telegram_id)

    # Translate rebar comment if present
    rebar_comment = data.get("rebar_comment")
    rebar_comment_translated = None
    if rebar_comment:
        translations = await translate_comment(rebar_comment, source_lang=lang)
        rebar_comment_translated = json.dumps(translations, ensure_ascii=False)

    # Translate entry comment if present
    entry_comment = data.get("entry_comment")
    entry_comment_translated = None
    if entry_comment:
        translations = await translate_comment(entry_comment, source_lang=lang)
        entry_comment_translated = json.dumps(translations, ensure_ascii=False)

    entry_data = {
        "shift_id": data["shift_id"],
        "structure_type": data.get("structure_type"),
        "structure_name": data.get("structure_name"),
        "natura_status": data.get("natura_status"),
        "rebar_status": data.get("rebar_status"),
        "concrete_plan": data.get("concrete_plan"),
        "concrete_available": data.get("concrete_available"),
        "formwork_ready": data.get("formwork_ready"),
        "waterproof_ready": data.get("waterproof_ready"),
        "rebar_ready_for_pour": data.get("rebar_ready_for_pour"),
        "concrete_volume": data.get("concrete_volume"),
        "pour_method": data.get("pour_method"),
        "pump_type": data.get("pump_type"),
        "pump_logistics": data.get("pump_logistics"),
        "rebar_comment": rebar_comment,
        "rebar_comment_translated": rebar_comment_translated,
        "entry_comment": entry_comment,
        "entry_comment_translated": entry_comment_translated,
    }

    entry_id = await create_entry(entry_data)

    # Save defects
    selected_defects = data.get("selected_defects", [])
    defect_pairs = []
    for defect_code in selected_defects:
        if defect_code == RebarDefect.CUSTOM:
            # Custom defect text from rebar comment as fallback
            defect_pairs.append((defect_code, rebar_comment))
        else:
            defect_pairs.append((defect_code, None))

    if defect_pairs:
        await add_entry_defects(entry_id, defect_pairs)

    return entry_id


def get_comment_for_lang(comment_translated_json: str | None, lang: str, fallback: str | None) -> str | None:
    """Extract the right language version from stored JSON translations."""
    if not comment_translated_json:
        return fallback
    try:
        translations = json.loads(comment_translated_json)
        return translations.get(lang, fallback)
    except Exception:
        return fallback
