"""
Report generator.
Generates report PURELY from stored codes using label dictionaries.
NO text is translated — all data was stored as codes.
"""

from datetime import datetime
from data.translations import (
    t, label,
    STRUCTURE_TYPE_LABELS, NATURA_LABELS, REBAR_STATUS_LABELS,
    DEFECT_LABELS, POUR_METHOD_LABELS, PUMP_TYPE_LABELS,
    PUMP_LOGISTICS_LABELS, SHIFT_TYPE_LABELS
)
from enums import NaturaStatus, RebarStatus, ConcretePlan, ConcreteAvailable, PourMethod
from repositories.shift_repo import get_shift_entries, get_entry_defects
from repositories.project_repo import get_project, get_subproject


async def generate_report(shift: dict, lang: str) -> str:
    """Generate full shift handover report in user's language."""
    entries = await get_shift_entries(shift["id"])
    project = await get_project(shift["project_id"])
    subproject = await get_subproject(shift["subproject_id"])

    lines = []

    # Header
    lines.append(f"{'═' * 35}")
    lines.append(f"📋 *{t('report_header', lang)}*")
    lines.append(f"{'═' * 35}")
    lines.append(f"")

    # Shift info
    shift_type_label = label(SHIFT_TYPE_LABELS, shift["shift_type"], lang)
    project_name = project["name"] if project else "—"
    subproject_name = subproject["name"] if subproject else "—"

    started = shift.get("started_at", "—")
    if isinstance(started, str) and "." in started:
        started = started[:16]

    lines.append(f"🏗 *{project_name}*")
    lines.append(f"📂 {subproject_name}")
    lines.append(f"⏱ {shift_type_label}  |  {started}")
    lines.append("")

    if not entries:
        lines.append(t("report_no_entries", lang))
        return "\n".join(lines)

    for i, entry in enumerate(entries, 1):
        lines.append(f"{'─' * 30}")
        struct_type = label(STRUCTURE_TYPE_LABELS, entry["structure_type"], lang)
        lines.append(f"*{i}. {struct_type}: {entry['structure_name']}*")
        lines.append("")

        # NATURA
        natura = label(NATURA_LABELS, entry["natura_status"], lang)
        lines.append(f"📋 Натура / Permit: {natura}")
        if entry["natura_status"] == NaturaStatus.NOT_GIVEN:
            lines.append(f"   ‼️ {t('warn_natura_not_given', lang)}")
        elif entry["natura_status"] == NaturaStatus.WILL_BE_NIGHT:
            lines.append(f"   ⚠️ {t('warn_natura_night', lang)}")

        # REBAR
        rebar = label(REBAR_STATUS_LABELS, entry["rebar_status"], lang)
        lines.append(f"🔩 Арматура / Rebar: {rebar}")

        defects = await get_entry_defects(entry["id"])
        if defects:
            lines.append("   Дефекты:")
            for d in defects:
                if d["defect_code"] == "DEFECT_CUSTOM" and d["custom_text"]:
                    lines.append(f"   • {d['custom_text']}")
                else:
                    defect_label = label(DEFECT_LABELS, d["defect_code"], lang)
                    lines.append(f"   • {defect_label}")

        if entry.get("rebar_comment"):
            comment_key = "rebar_comment_translated"
            comment = entry.get(comment_key) or entry.get("rebar_comment", "")
            if comment:
                lines.append(f"   💬 {comment}")

        # CONCRETE
        concrete_plan = entry["concrete_plan"]
        if concrete_plan == ConcretePlan.NO_POUR:
            lines.append(f"🪣 Бетон / Concrete: ❌ Нет заливки")
        else:
            lines.append(f"🪣 Бетон / Concrete: ✅ Заливка запланирована")

            if entry.get("concrete_available") == ConcreteAvailable.NO:
                lines.append(f"   🔴 Бетон отсутствует!")
            elif entry.get("concrete_available") == ConcreteAvailable.YES:
                lines.append(f"   ✅ Бетон есть")

            readiness_parts = []
            fw_map = {"READY": "✅", "NOT_READY": "❌"}
            if entry.get("formwork_ready"):
                readiness_parts.append(f"Опалубка: {fw_map.get(entry['formwork_ready'], '—')}")
            if entry.get("waterproof_ready"):
                readiness_parts.append(f"Гидроизол.: {fw_map.get(entry['waterproof_ready'], '—')}")
            if entry.get("rebar_ready_for_pour"):
                readiness_parts.append(f"Арм.: {fw_map.get(entry['rebar_ready_for_pour'], '—')}")
            if readiness_parts:
                lines.append(f"   {' | '.join(readiness_parts)}")

            if entry.get("concrete_volume"):
                lines.append(f"   📐 Объём: *{entry['concrete_volume']} м³*")

            if entry.get("pour_method"):
                pm = label(POUR_METHOD_LABELS, entry["pour_method"], lang)
                lines.append(f"   🏗 Метод: {pm}")

            if entry.get("pump_type"):
                pt = label(PUMP_TYPE_LABELS, entry["pump_type"], lang)
                lines.append(f"   ⚙️ Насос: {pt}")

            if entry.get("pump_logistics") and entry["pump_logistics"] != "LOGISTICS_NONE":
                pl = label(PUMP_LOGISTICS_LABELS, entry["pump_logistics"], lang)
                lines.append(f"   🔧 Логистика: {pl}")

        if entry.get("entry_comment"):
            lines.append(f"💬 {entry.get('entry_comment_translated') or entry['entry_comment']}")

        lines.append("")

    # Summary block
    lines.append(f"{'═' * 35}")
    total = len(entries)
    pour_count = sum(
        1 for e in entries if e["concrete_plan"] == ConcretePlan.WILL_POUR
    )
    total_vol = sum(
        e["concrete_volume"] or 0 for e in entries
        if e["concrete_plan"] == ConcretePlan.WILL_POUR and e.get("concrete_volume")
    )
    warning_count = sum(
        1 for e in entries
        if e["natura_status"] in (NaturaStatus.NOT_GIVEN, NaturaStatus.WILL_BE_NIGHT)
        or e["rebar_status"] == RebarStatus.NOT_ACCEPTED
    )

    lines.append(f"📊 Конструкций: *{total}* | Заливок: *{pour_count}* | Объём: *{total_vol:.1f} м³*")
    if warning_count:
        lines.append(f"⚠️ Предупреждений: *{warning_count}*")
    lines.append(f"{'═' * 35}")
    lines.append(f"#handover #{datetime.now().strftime('%Y%m%d')}")

    return "\n".join(lines)
