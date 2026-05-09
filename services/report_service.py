"""
Report generator.
Produces a structured tabular report from stored codes.
No translation of stored data — all from dictionaries and DB labels.
"""

from datetime import datetime
from data.translations import t, lbl, SHIFT_LABELS, NATURA_LABELS, REBAR_LABELS, PUMP_LOGISTICS_LABELS
from repositories.shift_repo import get_entries, get_entry_defects, get_shift_with_project
from repositories.ref_repo import get_item


def _col(item: dict, lang: str, fallback_key: str = "name_ru") -> str:
    col = f"name_{lang}"
    return item.get(col) or item.get(fallback_key) or "—"


def _yn(val: str, lang: str) -> str:
    if val == "READY":
        return "✅"
    if val == "NOT_READY":
        return "❌"
    return "—"


async def generate_report(shift_id: int, lang: str) -> str:
    shift = await get_shift_with_project(shift_id)
    if not shift:
        return "❌ Смена не найдена"

    entries = await get_entries(shift_id)
    if not entries:
        return t("no_entries", lang)

    now = datetime.now().strftime("%d.%m.%Y %H:%M")
    shift_label = lbl(SHIFT_LABELS, shift["shift_type"], lang)
    started = (shift.get("started_at") or "")[:16].replace("T", " ")

    lines = []

    # ══════════════════════════════════════════
    # HEADER
    # ══════════════════════════════════════════
    lines.append("```")
    lines.append("╔══════════════════════════════════════════╗")
    lines.append("║     АКТ ПЕРЕДАЧИ СМЕНЫ / HANDOVER        ║")
    lines.append("╚══════════════════════════════════════════╝")
    lines.append(f"  Объект   : {shift.get('project_name', '—')}")
    lines.append(f"  Блок/зона: {shift.get('subproject_name', '—')}")
    lines.append(f"  Смена    : {shift_label}  |  {started}")
    lines.append(f"  Дата     : {now}")
    lines.append("──────────────────────────────────────────")
    lines.append("```")

    warnings = []
    total_volume = 0.0
    pour_count = 0

    # ══════════════════════════════════════════
    # ENTRIES — one card per structure
    # ══════════════════════════════════════════
    for i, entry in enumerate(entries, 1):
        struct_type = await get_item("structure_types", entry["structure_type_id"])
        st_name = _col(struct_type, lang) if struct_type else "—"
        st_icon = struct_type.get("icon", "🏗") if struct_type else "🏗"

        natura = lbl(NATURA_LABELS, entry["natura_status"], lang)
        rebar  = lbl(REBAR_LABELS, entry["rebar_status"], lang)

        # Defects
        defects = await get_entry_defects(entry["id"])
        defect_lines = []
        for d in defects:
            if d.get("code") == "CUSTOM" and d.get("custom_text"):
                defect_lines.append(f"• {d['custom_text']}")
            else:
                dname = d.get(f"name_{lang}") or d.get("name_ru") or "—"
                defect_lines.append(f"• {dname}")

        # Concrete block
        concrete_plan = entry["concrete_plan"]
        pour_method_name = "—"
        pump_name = "—"
        logistics_name = "—"
        volume_str = "—"
        readiness_str = "—"

        if concrete_plan == "WILL_POUR":
            pour_count += 1
            if entry.get("concrete_volume"):
                total_volume += entry["concrete_volume"]
                volume_str = f"{entry['concrete_volume']} м³"

            if entry.get("pour_method_id"):
                pm = await get_item("pour_methods", entry["pour_method_id"])
                if pm:
                    pour_method_name = f"{pm.get('icon','🚛')} {_col(pm, lang)}"

            if entry.get("pump_type_id"):
                pt = await get_item("pump_types", entry["pump_type_id"])
                if pt:
                    pump_name = _col(pt, lang)

            if entry.get("pump_logistics"):
                logistics_name = lbl(PUMP_LOGISTICS_LABELS, entry["pump_logistics"], lang)

            fw = _yn(entry.get("formwork_ready"), lang)
            wp = _yn(entry.get("waterproof_ready"), lang)
            rb = _yn(entry.get("rebar_ready_for_pour"), lang)
            readiness_str = f"Оп:{fw} Гидро:{wp} Арм:{rb}"

        # ── Collect warnings ──
        if entry["natura_status"] == "NATURA_NOT_GIVEN":
            warnings.append(f"‼️ {st_icon}{entry['structure_name']}: {t('warn_natura_not_given', lang)}")
        elif entry["natura_status"] == "NATURA_WILL_BE_NIGHT":
            warnings.append(f"⚠️ {st_icon}{entry['structure_name']}: {t('warn_natura_night', lang)}")

        if entry["rebar_status"] == "REBAR_NOT_ACCEPTED" and concrete_plan == "WILL_POUR":
            warnings.append(f"‼️ {st_icon}{entry['structure_name']}: {t('warn_rebar_blocks', lang)}")

        # ── Format card ──
        comment = ""
        if entry.get("comment"):
            c_key = f"comment_{lang}"
            comment = entry.get(c_key) or entry.get("comment") or ""

        lines.append("```")
        lines.append(f"┌─[{i}] {st_icon} {st_name}: {entry['structure_name']}")
        lines.append(f"│")
        lines.append(f"│  📋 Натура    : {natura}")
        lines.append(f"│  🔩 Арматура  : {rebar}")

        if defect_lines:
            lines.append(f"│  ⚠️  Дефекты   :")
            for dl in defect_lines:
                lines.append(f"│      {dl}")

        lines.append(f"│")

        if concrete_plan == "WILL_POUR":
            lines.append(f"│  🪣 Бетон     : ✅ ЗАЛИВКА")
            lines.append(f"│  📐 Объём     : {volume_str}")
            lines.append(f"│  🚛 Подача    : {pour_method_name}")
            if pump_name != "—":
                lines.append(f"│  ⚙️  Насос     : {pump_name}")
            if logistics_name != "—":
                lines.append(f"│  🔧 Логистика : {logistics_name}")
            lines.append(f"│  🔲 Готовность: {readiness_str}")
        else:
            lines.append(f"│  🪣 Бетон     : ❌ Заливки нет")

        if comment:
            lines.append(f"│")
            lines.append(f"│  💬 {comment}")

        lines.append(f"└{'─'*40}")
        lines.append("```")

    # ══════════════════════════════════════════
    # SUMMARY TABLE
    # ══════════════════════════════════════════
    lines.append("```")
    lines.append("┌──────────────── ИТОГ ────────────────────┐")
    lines.append(f"│  Конструкций всего : {len(entries):<20}│")
    lines.append(f"│  Запланировано заливок: {pour_count:<17}│")
    lines.append(f"│  Общий объём бетона: {f'{total_volume:.1f} м³':<20}│")
    lines.append("├──────────────────────────────────────────┤")

    # Status counts
    natura_ok  = sum(1 for e in entries if e["natura_status"] == "NATURA_GIVEN")
    natura_warn = len(entries) - natura_ok
    rebar_ok   = sum(1 for e in entries if e["rebar_status"] == "REBAR_ACCEPTED")
    rebar_warn = len(entries) - rebar_ok

    lines.append(f"│  Натура выдана    : {natura_ok}/{len(entries):<21}│")
    lines.append(f"│  Арматура сдана   : {rebar_ok}/{len(entries):<21}│")
    lines.append("└──────────────────────────────────────────┘")
    lines.append("```")

    # ══════════════════════════════════════════
    # WARNINGS BLOCK
    # ══════════════════════════════════════════
    if warnings:
        lines.append("⚠️ *ПРЕДУПРЕЖДЕНИЯ:*")
        for w in warnings:
            lines.append(w)
        lines.append("")

    lines.append(f"🕐 _Сформировано: {now}_")
    lines.append(f"#handover #{datetime.now().strftime('%Y%m%d')}")

    return "\n".join(lines)
