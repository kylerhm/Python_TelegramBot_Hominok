"""
Форматтеры для отображения событий пользователю.
"""


def group_events_by_date(events):
    """Группирует список событий по дате. Возвращает dict {date_str: [events]}."""
    grouped = {}
    for e in events:
        date_str = str(e["date"])
        grouped.setdefault(date_str, []).append(e)
    return grouped


def format_events_text(grouped, title="📅 Календарь:"):
    """Форматирует сгруппированные события в текстовое сообщение."""
    if not grouped:
        return None
    lines = [title, ""]
    for date_str in sorted(grouped.keys()):
        lines.append(f"📌 {date_str}")
        for e in grouped[date_str]:
            lines.append(f"   ⏰ {e['time']} — {e['name']} (№{e['id']})")
        lines.append("")
    return "\n".join(lines)


def format_public_events_text(events):
    """Форматирует публичные события с именами авторов."""
    from utils.parsers import get_owner_name

    if not events:
        return None
    grouped = group_events_by_date(events)
    lines = ["🌍 Общие события:", ""]
    for date_str in sorted(grouped.keys()):
        lines.append(f"📌 {date_str}")
        for e in grouped[date_str]:
            owner_name = get_owner_name(e["owner_id"])
            lines.append(f"   ⏰ {e['time']} — {e['name']} (от {owner_name})")
        lines.append("")
    return "\n".join(lines)
