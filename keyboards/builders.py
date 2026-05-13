from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder
from data.translations import t

PAGE_SIZE = 8


def lang_keyboard() -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    kb.button(text="🇷🇺 Русский", callback_data="lang:ru")
    kb.button(text="🇺🇿 O'zbek", callback_data="lang:uz")
    kb.button(text="🇬🇧 English", callback_data="lang:en")
    kb.button(text="🇹🇷 Türkçe", callback_data="lang:tr")
    kb.adjust(2)
    return kb.as_markup()


def main_menu_keyboard(lang: str, is_senior: bool, is_admin: bool) -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    kb.button(text=t("btn_start_shift", lang), callback_data="shift:start")
    kb.button(text=t("btn_repeat_last", lang), callback_data="shift:repeat")
    kb.button(text=t("btn_my_reports", lang), callback_data="reports:my")
    if is_senior or is_admin:
        kb.button(text=t("btn_all_reports", lang), callback_data="reports:all")
    if is_admin:
        kb.button(text=t("btn_admin", lang), callback_data="admin:menu")
    kb.adjust(1)
    return kb.as_markup()


def paginated_keyboard(items: list, callback_prefix: str, lang: str,
                       name_field: str = None, page: int = 0,
                       extra_buttons: list = None) -> InlineKeyboardMarkup:
    """Generic paginated inline keyboard."""
    kb = InlineKeyboardBuilder()
    start = page * PAGE_SIZE
    chunk = items[start:start + PAGE_SIZE]
    total_pages = max(1, (len(items) + PAGE_SIZE - 1) // PAGE_SIZE)

    for item in chunk:
        if name_field:
            label = item[f"name_{lang}"] if f"name_{lang}" in item.keys() else item[name_field]
        else:
            label = item["name"]
        icon = item["icon"] + " " if "icon" in item.keys() and item["icon"] else ""
        kb.button(text=f"{icon}{label}", callback_data=f"{callback_prefix}:{item['id']}")

    kb.adjust(2)

    # Pagination row
    nav = []
    if page > 0:
        nav.append(InlineKeyboardButton(text=t("btn_prev", lang), callback_data=f"page:{callback_prefix}:{page-1}"))
    if (page + 1) < total_pages:
        nav.append(InlineKeyboardButton(text=t("btn_next", lang), callback_data=f"page:{callback_prefix}:{page+1}"))
    if nav:
        kb.row(*nav)

    if extra_buttons:
        for btn in extra_buttons:
            kb.row(InlineKeyboardButton(text=btn[0], callback_data=btn[1]))

    kb.row(InlineKeyboardButton(text=t("btn_cancel", lang), callback_data="shift:cancel"))
    return kb.as_markup()


def shift_type_keyboard(lang: str) -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    kb.button(text=f"☀️ {t('shift_day', lang)}", callback_data="shift_type:day")
    kb.button(text=f"🌙 {t('shift_night', lang)}", callback_data="shift_type:night")
    kb.button(text=t("btn_cancel", lang), callback_data="shift:cancel")
    kb.adjust(2, 1)
    return kb.as_markup()


def natura_keyboard(lang: str) -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    kb.button(text=t("natura_given", lang), callback_data="natura:NATURA_GIVEN")
    kb.button(text=t("natura_not_given", lang), callback_data="natura:NATURA_NOT_GIVEN")
    kb.button(text=t("natura_will_be_night", lang), callback_data="natura:NATURA_WILL_BE_NIGHT")
    kb.button(text=t("btn_cancel", lang), callback_data="shift:cancel")
    kb.adjust(1)
    return kb.as_markup()


def rebar_keyboard(lang: str) -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    kb.button(text=t("rebar_done", lang), callback_data="rebar:REBAR_DONE")
    kb.button(text=t("rebar_partial", lang), callback_data="rebar:REBAR_PARTIAL")
    kb.button(text=t("rebar_not_done", lang), callback_data="rebar:REBAR_NOT_DONE")
    kb.button(text=t("btn_cancel", lang), callback_data="shift:cancel")
    kb.adjust(1)
    return kb.as_markup()


def defects_keyboard(lang: str, defects: list, selected: list) -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    for d in defects:
        sel = "✅ " if d["id"] in selected else ""
        name = d[f"name_{lang}"] if f"name_{lang}" in d.keys() else d["name_ru"]
        kb.button(text=f"{sel}{name}", callback_data=f"defect:{d['id']}")
    kb.adjust(1)
    kb.row(InlineKeyboardButton(text=t("btn_add_custom_defect", lang), callback_data="defect:custom"))
    kb.row(InlineKeyboardButton(text=t("btn_done_defects", lang), callback_data="defect:done"))
    kb.row(InlineKeyboardButton(text=t("btn_cancel", lang), callback_data="shift:cancel"))
    return kb.as_markup()


def yes_no_keyboard(lang: str, yes_cb: str, no_cb: str) -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    kb.button(text=t("btn_yes", lang), callback_data=yes_cb)
    kb.button(text=t("btn_no", lang), callback_data=no_cb)
    kb.button(text=t("btn_cancel", lang), callback_data="shift:cancel")
    kb.adjust(2, 1)
    return kb.as_markup()


def pump_logistics_keyboard(lang: str) -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    kb.button(text=t("pump_mount", lang), callback_data="pump_log:PUMP_MOUNT")
    kb.button(text=t("pump_move", lang), callback_data="pump_log:PUMP_MOVE")
    kb.button(text=t("pump_both", lang), callback_data="pump_log:PUMP_BOTH")
    kb.button(text=t("pump_none", lang), callback_data="pump_log:PUMP_NONE")
    kb.button(text=t("btn_cancel", lang), callback_data="shift:cancel")
    kb.adjust(2, 2, 1)
    return kb.as_markup()


def entry_finish_keyboard(lang: str) -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    kb.button(text=t("btn_add_structure", lang), callback_data="entry:add_more")
    kb.button(text=t("btn_finish_shift", lang), callback_data="entry:finish")
    kb.adjust(1)
    return kb.as_markup()


def skip_keyboard(lang: str) -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    kb.button(text=t("btn_skip", lang), callback_data="comment:skip")
    kb.button(text=t("btn_cancel", lang), callback_data="shift:cancel")
    kb.adjust(1)
    return kb.as_markup()


def admin_menu_keyboard(lang: str) -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    kb.button(text=t("btn_manage_projects", lang), callback_data="admin:projects")
    kb.button(text=t("btn_manage_structures", lang), callback_data="admin:structures")
    kb.button(text=t("btn_manage_defects", lang), callback_data="admin:defects")
    kb.button(text=t("btn_manage_pour", lang), callback_data="admin:pour")
    kb.button(text=t("btn_manage_pumps", lang), callback_data="admin:pumps")
    kb.button(text=t("btn_manage_users", lang), callback_data="admin:users")
    kb.button(text=t("btn_gen_codes", lang), callback_data="admin:gencode")
    kb.button(text=t("btn_back", lang), callback_data="menu:main")
    kb.adjust(2, 2, 2, 1, 1)
    return kb.as_markup()


def ref_list_keyboard(lang: str, items: list, prefix: str, name_lang: str) -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    for item in items:
        try:
            name = item[f"name_{name_lang}"]
        except (KeyError, IndexError):
            name = item.get("name", str(item["id"]))
        kb.button(text=f"❌ {name}", callback_data=f"{prefix}:del:{item['id']}")
    kb.button(text=f"➕ Добавить / Add", callback_data=f"{prefix}:add")
    kb.button(text=t("btn_back", lang), callback_data="admin:menu")
    kb.adjust(1)
    return kb.as_markup()


def confirm_keyboard(lang: str, yes_cb: str, no_cb: str = "admin:menu") -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    kb.button(text=t("btn_yes", lang), callback_data=yes_cb)
    kb.button(text=t("btn_no", lang), callback_data=no_cb)
    kb.adjust(2)
    return kb.as_markup()
