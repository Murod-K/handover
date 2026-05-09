from aiogram.types import InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder
from data.translations import t, SHIFT_LABELS, NATURA_LABELS, REBAR_LABELS, PUMP_LOGISTICS_LABELS


def lang_kb() -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    kb.button(text="🇷🇺 Русский",  callback_data="lang:ru")
    kb.button(text="🇺🇿 O'zbek",   callback_data="lang:uz")
    kb.button(text="🇬🇧 English",  callback_data="lang:en")
    kb.button(text="🇹🇷 Türkçe",   callback_data="lang:tr")
    kb.adjust(2)
    return kb.as_markup()


def main_menu_kb(lang: str, is_admin: bool = False) -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    kb.button(text=t("btn_new_shift", lang),  callback_data="menu:new_shift")
    kb.button(text=t("btn_my_reports", lang), callback_data="menu:reports")
    kb.button(text=t("btn_settings", lang),   callback_data="menu:settings")
    if is_admin:
        kb.button(text=t("btn_admin", lang),  callback_data="menu:admin")
    kb.adjust(1)
    return kb.as_markup()


def list_kb(items: list[dict], prefix: str, lang: str,
            back_cb: str = None, add_cb: str = None) -> InlineKeyboardMarkup:
    """Generic list keyboard from DB rows."""
    kb = InlineKeyboardBuilder()
    for item in items:
        name = item.get("name") or item.get("name_ru") or "—"
        kb.button(text=name, callback_data=f"{prefix}:{item['id']}")
    if add_cb:
        kb.button(text=t("btn_add_new", lang), callback_data=add_cb)
    if back_cb:
        kb.button(text=t("btn_back", lang), callback_data=back_cb)
    kb.adjust(1)
    return kb.as_markup()


def shift_type_kb(lang: str) -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    for code, lbls in SHIFT_LABELS.items():
        kb.button(text=lbls.get(lang, lbls["ru"]), callback_data=f"shift_type:{code}")
    kb.adjust(2)
    return kb.as_markup()


def natura_kb(lang: str) -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    for code, lbls in NATURA_LABELS.items():
        kb.button(text=lbls.get(lang, lbls["ru"]), callback_data=f"natura:{code}")
    kb.adjust(1)
    return kb.as_markup()


def rebar_kb(lang: str) -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    for code, lbls in REBAR_LABELS.items():
        kb.button(text=lbls.get(lang, lbls["ru"]), callback_data=f"rebar:{code}")
    kb.adjust(1)
    return kb.as_markup()


def defects_kb(defects: list[dict], selected: list[int], lang: str) -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    col = f"name_{lang}" if lang in ("uz", "en", "tr") else "name_ru"
    for d in defects:
        mark = "✅ " if d["id"] in selected else "☐ "
        name = d.get(col) or d.get("name_ru") or "—"
        kb.button(text=f"{mark}{name}", callback_data=f"defect:{d['id']}")
    kb.button(text=t("btn_done", lang), callback_data="defect:DONE")
    kb.adjust(1)
    return kb.as_markup()


def pour_methods_kb(methods: list[dict], lang: str) -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    col = f"name_{lang}" if lang in ("uz", "en", "tr") else "name_ru"
    for m in methods:
        icon = m.get("icon", "🚛")
        name = m.get(col) or m.get("name_ru") or "—"
        kb.button(text=f"{icon} {name}", callback_data=f"pour:{m['id']}")
    kb.adjust(1)
    return kb.as_markup()


def pump_types_kb(pumps: list[dict], lang: str) -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    col = f"name_{lang}" if lang in ("uz", "en", "tr") else "name_ru"
    for p in pumps:
        name = p.get(col) or p.get("name_ru") or "—"
        kb.button(text=name, callback_data=f"pump:{p['id']}")
    kb.adjust(1)
    return kb.as_markup()


def pump_logistics_kb(lang: str) -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    for code, lbls in PUMP_LOGISTICS_LABELS.items():
        kb.button(text=lbls.get(lang, lbls["ru"]), callback_data=f"logistics:{code}")
    kb.adjust(1)
    return kb.as_markup()


def yes_no_kb(lang: str, yes_cb: str, no_cb: str) -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    kb.button(text=t("btn_yes", lang), callback_data=yes_cb)
    kb.button(text=t("btn_no", lang),  callback_data=no_cb)
    kb.adjust(2)
    return kb.as_markup()


def ready_kb(lang: str, prefix: str) -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    kb.button(text=t("btn_ready", lang),     callback_data=f"{prefix}:READY")
    kb.button(text=t("btn_not_ready", lang), callback_data=f"{prefix}:NOT_READY")
    kb.adjust(2)
    return kb.as_markup()


def concrete_kb(lang: str) -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    will = {"ru": "✅ Будет заливка", "uz": "✅ Quyish bo'ladi",
            "en": "✅ Will pour", "tr": "✅ Döküm yapılacak"}
    no   = {"ru": "❌ Не будет", "uz": "❌ Bo'lmaydi",
            "en": "❌ No pour", "tr": "❌ Dökülmeyecek"}
    kb.button(text=will.get(lang, will["ru"]), callback_data="concrete:WILL_POUR")
    kb.button(text=no.get(lang, no["ru"]),     callback_data="concrete:NO_POUR")
    kb.adjust(1)
    return kb.as_markup()


def after_entry_kb(lang: str) -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    kb.button(text=t("btn_add_structure", lang), callback_data="entry:add_more")
    kb.button(text=t("btn_finish_shift", lang),  callback_data="entry:finish")
    kb.button(text=t("btn_cancel_entry", lang),  callback_data="entry:cancel_last")
    kb.adjust(1)
    return kb.as_markup()


# ── ADMIN KEYBOARDS ──

def admin_menu_kb(lang: str) -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    kb.button(text=t("btn_manage_projects", lang),     callback_data="admin:projects")
    kb.button(text=t("btn_manage_structures", lang),   callback_data="admin:structures")
    kb.button(text=t("btn_manage_defects", lang),      callback_data="admin:defects")
    kb.button(text=t("btn_manage_pour_methods", lang), callback_data="admin:pour_methods")
    kb.button(text=t("btn_manage_pump_types", lang),   callback_data="admin:pump_types")
    kb.button(text=t("btn_back", lang),                callback_data="menu:main")
    kb.adjust(1)
    return kb.as_markup()


def ref_list_admin_kb(items: list[dict], table: str, lang: str, back_cb: str) -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    col = f"name_{lang}" if lang in ("uz", "en", "tr") else "name_ru"
    for item in items:
        name = item.get(col) or item.get("name") or item.get("name_ru") or "—"
        kb.button(text=f"🗑 {name}", callback_data=f"del_{table}:{item['id']}")
    kb.button(text=t("btn_add_new", lang), callback_data=f"add_{table}")
    kb.button(text=t("btn_back", lang),    callback_data=back_cb)
    kb.adjust(1)
    return kb.as_markup()


def confirm_del_kb(lang: str, confirm_cb: str) -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    kb.button(text=t("btn_confirm_yes", lang), callback_data=confirm_cb)
    kb.button(text=t("btn_cancel", lang),      callback_data="admin:back")
    kb.adjust(2)
    return kb.as_markup()


def projects_admin_kb(projects: list[dict], lang: str) -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    for p in projects:
        kb.button(text=f"📁 {p['name']}", callback_data=f"proj_detail:{p['id']}")
    kb.button(text=t("btn_add_new", lang), callback_data="add_project")
    kb.button(text=t("btn_back", lang),    callback_data="admin:back")
    kb.adjust(1)
    return kb.as_markup()


def project_detail_kb(project_id: int, subprojects: list[dict], lang: str) -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    for sp in subprojects:
        kb.button(text=f"🗑 {sp['name']}", callback_data=f"del_subproject:{sp['id']}")
    kb.button(text=t("btn_add_new", lang), callback_data=f"add_subproject:{project_id}")
    kb.button(text=f"🗑 Удалить объект",   callback_data=f"del_project:{project_id}")
    kb.button(text=t("btn_back", lang),    callback_data="admin:projects")
    kb.adjust(1)
    return kb.as_markup()
