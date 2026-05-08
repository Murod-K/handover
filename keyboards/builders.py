"""
Keyboard builders. All labels come from translation dictionaries.
"""

from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder, ReplyKeyboardBuilder
from data.translations import (
    t, label,
    STRUCTURE_TYPE_LABELS, NATURA_LABELS, REBAR_STATUS_LABELS,
    DEFECT_LABELS, POUR_METHOD_LABELS, PUMP_TYPE_LABELS,
    PUMP_LOGISTICS_LABELS, SHIFT_TYPE_LABELS, READINESS_LABELS
)
from enums import (
    Language, ShiftType, StructureType, NaturaStatus,
    RebarStatus, RebarDefect, ConcretePlan, ConcreteAvailable,
    ReadinessStatus, PourMethod, PumpType, PumpLogistics
)


def language_keyboard() -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    kb.button(text="🇷🇺 Русский", callback_data="lang:ru")
    kb.button(text="🇺🇿 O'zbek", callback_data="lang:uz")
    kb.button(text="🇬🇧 English", callback_data="lang:en")
    kb.button(text="🇹🇷 Türkçe", callback_data="lang:tr")
    kb.adjust(2)
    return kb.as_markup()


def shift_type_keyboard(lang: str) -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    for st in ShiftType:
        kb.button(
            text=label(SHIFT_TYPE_LABELS, st, lang),
            callback_data=f"shift_type:{st.value}"
        )
    kb.adjust(2)
    return kb.as_markup()


def structure_type_keyboard(lang: str) -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    for st in StructureType:
        kb.button(
            text=label(STRUCTURE_TYPE_LABELS, st, lang),
            callback_data=f"struct:{st.value}"
        )
    kb.adjust(2)
    return kb.as_markup()


def natura_keyboard(lang: str) -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    for ns in NaturaStatus:
        kb.button(
            text=label(NATURA_LABELS, ns, lang),
            callback_data=f"natura:{ns.value}"
        )
    kb.adjust(1)
    return kb.as_markup()


def rebar_status_keyboard(lang: str) -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    for rs in RebarStatus:
        kb.button(
            text=label(REBAR_STATUS_LABELS, rs, lang),
            callback_data=f"rebar_status:{rs.value}"
        )
    kb.adjust(1)
    return kb.as_markup()


def rebar_defects_keyboard(lang: str, selected: list[str]) -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    for rd in RebarDefect:
        is_selected = rd.value in selected
        prefix = "✅ " if is_selected else "☐ "
        kb.button(
            text=f"{prefix}{label(DEFECT_LABELS, rd, lang)}",
            callback_data=f"defect:{rd.value}"
        )
    kb.button(
        text=t("btn_defects_done", lang),
        callback_data="defect:DONE"
    )
    kb.adjust(1)
    return kb.as_markup()


def yes_no_keyboard(lang: str, yes_cb: str, no_cb: str) -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    kb.button(text=t("btn_yes", lang), callback_data=yes_cb)
    kb.button(text=t("btn_no", lang), callback_data=no_cb)
    kb.adjust(2)
    return kb.as_markup()


def readiness_keyboard(lang: str, prefix: str) -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    for rs in ReadinessStatus:
        kb.button(
            text=label(READINESS_LABELS, rs, lang),
            callback_data=f"{prefix}:{rs.value}"
        )
    kb.adjust(2)
    return kb.as_markup()


def pour_method_keyboard(lang: str) -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    for pm in PourMethod:
        kb.button(
            text=label(POUR_METHOD_LABELS, pm, lang),
            callback_data=f"pour_method:{pm.value}"
        )
    kb.adjust(1)
    return kb.as_markup()


def pump_type_keyboard(lang: str) -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    for pt in PumpType:
        kb.button(
            text=label(PUMP_TYPE_LABELS, pt, lang),
            callback_data=f"pump_type:{pt.value}"
        )
    kb.adjust(1)
    return kb.as_markup()


def pump_logistics_keyboard(lang: str) -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    for pl in PumpLogistics:
        kb.button(
            text=label(PUMP_LOGISTICS_LABELS, pl, lang),
            callback_data=f"pump_logistics:{pl.value}"
        )
    kb.adjust(1)
    return kb.as_markup()


def projects_keyboard(projects: list[dict]) -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    for p in projects:
        kb.button(text=f"📁 {p['name']}", callback_data=f"project:{p['id']}")
    kb.adjust(1)
    return kb.as_markup()


def subprojects_keyboard(subprojects: list[dict]) -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    for sp in subprojects:
        kb.button(text=f"📂 {sp['name']}", callback_data=f"subproject:{sp['id']}")
    kb.adjust(1)
    return kb.as_markup()


def after_entry_keyboard(lang: str) -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    kb.button(text=t("btn_add_structure", lang), callback_data="entry:add_more")
    kb.button(text=t("btn_finish_shift", lang), callback_data="entry:finish_shift")
    kb.adjust(1)
    return kb.as_markup()


def concrete_plan_keyboard(lang: str) -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    kb.button(
        text="✅ " + ("Будет заливка" if lang == "ru" else "Quyish bo'ladi" if lang == "uz" else "Will pour" if lang == "en" else "Döküm yapılacak"),
        callback_data=f"concrete_plan:{ConcretePlan.WILL_POUR.value}"
    )
    kb.button(
        text="❌ " + ("Не будет" if lang == "ru" else "Bo'lmaydi" if lang == "uz" else "No pour" if lang == "en" else "Dökülmeyecek"),
        callback_data=f"concrete_plan:{ConcretePlan.NO_POUR.value}"
    )
    kb.adjust(1)
    return kb.as_markup()
