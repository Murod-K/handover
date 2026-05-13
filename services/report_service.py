import logging
from datetime import datetime
from data.translations import t

logger = logging.getLogger(__name__)

_SHIFT_TYPE_LABELS = {
    "day":   {"ru": "День", "uz": "Kunduz", "en": "Day",   "tr": "Gündüz"},
    "night": {"ru": "Ночь", "uz": "Kecha",  "en": "Night", "tr": "Gece"},
}

_NATURA_LABELS = {
    "NATURA_GIVEN":       {"ru": "Дана",         "uz": "Berilgan",       "en": "Given",           "tr": "Verildi"},
    "NATURA_NOT_GIVEN":   {"ru": "Не дана",       "uz": "Berilmagan",     "en": "Not given",       "tr": "Verilmedi"},
    "NATURA_WILL_BE_NIGHT":{"ru":"Будет ночью",   "uz": "Kechasi bo'ladi","en": "At night",         "tr": "Gece olacak"},
}
_REBAR_LABELS = {
    "REBAR_DONE":    {"ru": "Сдана",    "uz": "Topshirilgan",     "en": "Done",    "tr": "Tamamlandı"},
    "REBAR_PARTIAL": {"ru": "Частично", "uz": "Qisman",           "en": "Partial", "tr": "Kısmen"},
    "REBAR_NOT_DONE":{"ru": "Не сдана", "uz": "Topshirilmagan",   "en": "Not done","tr": "Tamamlanmadı"},
}
_PUMP_LOG_LABELS = {
    "PUMP_MOUNT": {"ru":"Монтаж",       "uz":"Montaj",        "en":"Mount",       "tr":"Montaj"},
    "PUMP_MOVE":  {"ru":"Перестановка", "uz":"Ko'chirish",    "en":"Reposition",  "tr":"Yeniden konum"},
    "PUMP_BOTH":  {"ru":"Оба",          "uz":"Ikkalasi",      "en":"Both",        "tr":"İkisi de"},
    "PUMP_NONE":  {"ru":"Нет",          "uz":"Yo'q",          "en":"None",        "tr":"Yok"},
}

_COL_HEADERS = {
    "ru": ["№","Конструкция","Маркировка","Натура","Арматура","Дефекты","Бетон","Объём","Способ","Насос","Логистика","Примечание"],
    "uz": ["№","Konstruksiya","Belgilash","Natura","Armatura","Nuqsonlar","Beton","Hajm","Usul","Nasos","Logistika","Izoh"],
    "en": ["#","Structure","Marking","Formwork","Rebar","Defects","Concrete","Volume","Method","Pump","Logistics","Note"],
    "tr": ["#","Yapı","İşaret","Kalıp","Donatım","Kusurlar","Beton","Hacim","Yöntem","Pompa","Lojistik","Not"],
}

_TITLE = {
    "ru": "АКТ ПЕРЕДАЧИ СМЕНЫ",
    "uz": "SMENA TOPSHIRISH DALOLATNOMASI",
    "en": "SHIFT HANDOVER REPORT",
    "tr": "VARDİYA DEVİR RAPORU",
}
_OBJECT_LABEL = {"ru":"Объект","uz":"Ob'ekt","en":"Project","tr":"Proje"}
_BLOCK_LABEL =  {"ru":"Блок",  "uz":"Blok",  "en":"Block",  "tr":"Blok"}
_SHIFT_LABEL =  {"ru":"Смена", "uz":"Smena", "en":"Shift",  "tr":"Vardiya"}
_DATE_LABEL =   {"ru":"Дата",  "uz":"Sana",  "en":"Date",   "tr":"Tarih"}
_ENG_LABEL =    {"ru":"Инженер","uz":"Muhandis","en":"Engineer","tr":"Mühendis"}
_TOTAL_LABEL =  {
    "ru": "Итого: {structs} конструкций | {pours} заливок | {vol:.1f} м³ | {warns} предупреждений",
    "uz": "Jami: {structs} ta konstruksiya | {pours} ta quyish | {vol:.1f} m³ | {warns} ta ogohlantirish",
    "en": "Total: {structs} structures | {pours} pours | {vol:.1f} m³ | {warns} warnings",
    "tr": "Toplam: {structs} yapı | {pours} döküm | {vol:.1f} m³ | {warns} uyarı",
}
_WARN_HEADER = {"ru":"Предупреждения","uz":"Ogohlantirishlar","en":"Warnings","tr":"Uyarılar"}
_YES = {"ru":"Да","uz":"Ha","en":"Yes","tr":"Evet"}
_NO  = {"ru":"Нет","uz":"Yo'q","en":"No","tr":"Hayır"}


def _lbl(dct: dict, lang: str) -> str:
    return dct.get(lang, dct.get("ru", ""))


def _loc(row_or_dict, key: str, lang: str) -> str:
    """Get localized value from dict or aiosqlite.Row."""
    col = f"{key}_{lang}"
    try:
        v = row_or_dict[col]
        if v:
            return v
    except (KeyError, IndexError):
        pass
    try:
        return row_or_dict[f"{key}_ru"] or ""
    except (KeyError, IndexError):
        return ""


def _yn(val, lang: str) -> str:
    return _lbl(_YES, lang) if val else _lbl(_NO, lang)


def generate_html(shift: dict, entries: list, lang: str) -> str:
    headers = _COL_HEADERS.get(lang, _COL_HEADERS["ru"])
    shift_type_label = _lbl(_SHIFT_TYPE_LABELS.get(shift.get("shift_type", "day"), _SHIFT_TYPE_LABELS["day"]), lang)
    date_str = ""
    try:
        started = shift.get("started_at", "")
        if started:
            dt = datetime.fromisoformat(str(started).replace("Z",""))
            date_str = dt.strftime("%d.%m.%Y %H:%M")
    except Exception:
        date_str = str(shift.get("started_at",""))

    total_pours = 0
    total_vol = 0.0
    warnings_list = []
    rows_html = ""

    for i, entry in enumerate(entries, 1):
        st_name = _loc(entry, "st_name", lang) or entry.get("structure_name", "")
        marking = entry.get("structure_name", "")
        natura  = _lbl(_NATURA_LABELS.get(entry.get("natura_status",""), {}), lang)
        rebar   = _lbl(_REBAR_LABELS.get(entry.get("rebar_status",""), {}), lang)

        # Defects
        defect_parts = []
        for d in entry.get("defects", []):
            if d.get("defect_id"):
                col = f"name_{lang}"
                try:
                    dname = d[col] or d["name_ru"]
                except (KeyError, IndexError):
                    dname = ""
                if dname:
                    defect_parts.append(dname)
            else:
                custom = d.get(f"custom_text_{lang}") or d.get("custom_text_ru") or ""
                if custom:
                    defect_parts.append(custom)
        defects_text = "; ".join(defect_parts) if defect_parts else "—"

        concrete_plan = entry.get("concrete_plan", "CONCRETE_NO")
        has_concrete = (concrete_plan == "CONCRETE_YES")
        concrete_cell = _lbl(_YES, lang) if has_concrete else _lbl(_NO, lang)

        vol = entry.get("concrete_volume")
        vol_str = f"{vol:.1f}" if vol else "—"
        pm_name = _loc(entry, "pm_name", lang) if has_concrete else "—"
        pump_name = _loc(entry, "pump_name", lang) if entry.get("pump_type_id") else "—"
        pump_log = _lbl(_PUMP_LOG_LABELS.get(entry.get("pump_logistics",""), {}), lang) if has_concrete else "—"
        comment = entry.get(f"comment_{lang}") or entry.get("comment_ru") or "—"

        if has_concrete:
            total_pours += 1
            total_vol += vol or 0.0

        # Warnings
        entry_warnings = []
        if has_concrete and entry.get("natura_status") == "NATURA_NOT_GIVEN":
            entry_warnings.append(f"{marking}: {t('warn_natura_concrete', lang)}")
        if has_concrete and entry.get("rebar_status") == "REBAR_NOT_DONE":
            entry_warnings.append(f"{marking}: {t('warn_rebar_concrete', lang)}")
        if has_concrete and not entry.get("concrete_available"):
            entry_warnings.append(f"{marking}: {t('warn_concrete_not_ordered', lang)}")
        warnings_list.extend(entry_warnings)

        warn_class = ' class="warn-row"' if entry_warnings else ""
        concrete_class = ' class="cell-yes"' if has_concrete else ""
        rebar_class = ' class="cell-bad"' if entry.get("rebar_status") == "REBAR_NOT_DONE" else (' class="cell-partial"' if entry.get("rebar_status") == "REBAR_PARTIAL" else ' class="cell-ok"')
        natura_class = ' class="cell-bad"' if entry.get("natura_status") == "NATURA_NOT_GIVEN" else ' class="cell-ok"'

        rows_html += f"""
        <tr{warn_class}>
            <td>{i}</td>
            <td>{st_name}</td>
            <td><strong>{marking}</strong></td>
            <td{natura_class}>{natura}</td>
            <td{rebar_class}>{rebar}</td>
            <td class="defects-cell">{defects_text}</td>
            <td{concrete_class}>{concrete_cell}</td>
            <td>{vol_str}</td>
            <td>{pm_name}</td>
            <td>{pump_name}</td>
            <td>{pump_log}</td>
            <td class="comment-cell">{comment}</td>
        </tr>"""

    # Warnings block
    warn_html = ""
    if warnings_list:
        items = "".join(f"<li>⚠ {w}</li>" for w in warnings_list)
        warn_html = f"""
        <div class="warnings-block">
            <h3>{_lbl(_WARN_HEADER, lang)}</h3>
            <ul>{items}</ul>
        </div>"""

    total_line = _TOTAL_LABEL.get(lang, _TOTAL_LABEL["ru"]).format(
        structs=len(entries), pours=total_pours, vol=total_vol, warns=len(warnings_list)
    )

    header_row = "".join(f"<th>{h}</th>" for h in headers)

    html = f"""<!DOCTYPE html>
<html lang="{lang}">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{_lbl(_TITLE, lang)}</title>
<style>
  * {{ box-sizing: border-box; margin: 0; padding: 0; }}
  body {{
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
    font-size: 13px;
    background: #f5f7fa;
    color: #1a1a2e;
    padding: 16px;
  }}
  .page {{ background: #fff; border-radius: 10px; box-shadow: 0 2px 12px rgba(0,0,0,0.10); overflow: hidden; max-width: 1200px; margin: 0 auto; }}
  .header {{
    background: #1a2a4a;
    color: #fff;
    padding: 20px 24px 16px;
  }}
  .header h1 {{ font-size: 18px; font-weight: 700; letter-spacing: 1px; margin-bottom: 10px; }}
  .meta-grid {{ display: flex; flex-wrap: wrap; gap: 8px 24px; font-size: 13px; opacity: 0.9; }}
  .meta-item span {{ font-weight: 600; }}
  .table-wrap {{ overflow-x: auto; padding: 0; }}
  table {{ width: 100%; border-collapse: collapse; font-size: 12px; }}
  th {{
    background: #1a2a4a;
    color: #fff;
    padding: 9px 8px;
    text-align: left;
    font-weight: 600;
    white-space: nowrap;
    position: sticky;
    top: 0;
  }}
  td {{ padding: 8px 8px; border-bottom: 1px solid #e8ecf0; vertical-align: top; }}
  tr:hover td {{ background: #f0f4ff; }}
  tr.warn-row td {{ background: #fff5f5; }}
  .cell-ok  {{ color: #1a7a40; font-weight: 600; }}
  .cell-bad {{ color: #c0392b; font-weight: 600; }}
  .cell-partial {{ color: #e67e22; font-weight: 600; }}
  .cell-yes {{ color: #1a6ab5; font-weight: 600; }}
  .defects-cell {{ max-width: 160px; font-size: 11px; color: #c0392b; }}
  .comment-cell {{ max-width: 180px; font-size: 11px; color: #555; font-style: italic; }}
  .totals-row td {{
    background: #1a2a4a;
    color: #fff;
    font-weight: 700;
    font-size: 12px;
    padding: 10px 8px;
  }}
  .warnings-block {{
    margin: 16px 24px;
    background: #fff0f0;
    border-left: 4px solid #c0392b;
    border-radius: 6px;
    padding: 12px 16px;
  }}
  .warnings-block h3 {{ color: #c0392b; font-size: 13px; margin-bottom: 6px; }}
  .warnings-block ul {{ padding-left: 16px; font-size: 12px; color: #7a1010; line-height: 1.7; }}
  .footer {{ text-align: center; font-size: 11px; color: #aaa; padding: 12px; border-top: 1px solid #e8ecf0; }}
  @media (max-width: 600px) {{
    body {{ padding: 6px; font-size: 12px; }}
    .header h1 {{ font-size: 15px; }}
    th, td {{ padding: 6px 5px; font-size: 11px; }}
  }}
</style>
</head>
<body>
<div class="page">
  <div class="header">
    <h1>{_lbl(_TITLE, lang)}</h1>
    <div class="meta-grid">
      <div class="meta-item">{_lbl(_OBJECT_LABEL, lang)}: <span>{shift.get('project_name','')}</span></div>
      <div class="meta-item">{_lbl(_BLOCK_LABEL, lang)}: <span>{shift.get('subproject_name','')}</span></div>
      <div class="meta-item">{_lbl(_SHIFT_LABEL, lang)}: <span>{shift_type_label}</span></div>
      <div class="meta-item">{_lbl(_DATE_LABEL, lang)}: <span>{date_str}</span></div>
      <div class="meta-item">{_lbl(_ENG_LABEL, lang)}: <span>{shift.get('engineer_name','')}</span></div>
    </div>
  </div>
  <div class="table-wrap">
    <table>
      <thead><tr>{header_row}</tr></thead>
      <tbody>{rows_html}</tbody>
      <tfoot>
        <tr class="totals-row"><td colspan="{len(headers)}">{total_line}</td></tr>
      </tfoot>
    </table>
  </div>
  {warn_html}
  <div class="footer">Handover Bot v3 &bull; {date_str}</div>
</div>
</body>
</html>"""
    return html
