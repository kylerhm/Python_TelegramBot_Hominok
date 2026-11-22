"""
Обработчики callback-кнопок Telegram-бота.
"""
import re
import html
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from events.models import Meeting
from utils import (
    require_registration, handle_errors, parse_event_id,
    get_owner_name, group_events_by_date, format_events_text,
    format_public_events_text,
)
from services import (
    get_user, get_menu_keyboard,
    meeting_context, create_context, edit_context, read_context, delete_context,
    STATUS_EMOJI,
)

# calendar устанавливается динамически в main.py
import services as _services


# --- Callback-обработчики ---

def menu_callback_handler(update, context):
    """Обработчик кнопок меню."""
    query = update.callback_query
    try:
        query.answer()
    except Exception:
        pass  # Кнопка истекла или невалидна

    action = query.data

    def safe_edit(text, markup):
        """Безопасное редактирование сообщения с обработкой ошибок."""
        try:
            query.edit_message_text(text, reply_markup=markup)
        except Exception:
            pass  # Сообщение уже обновлено или не изменено

    if action == "menu_calendar":
        events = _services.calendar.get_all_events(query.from_user.id)
        if events:
            text = format_events_text(group_events_by_date(events), "📅 Ваш календарь:")
        else:
            text = "📅 Ваш календарь пуст. Создайте событие: /create_event <название> <дата> <время>"
        safe_edit(text, get_menu_keyboard())

    elif action == "menu_stats":
        try:
            tg_user = get_user(query.from_user.id)
            if tg_user:
                text = (
                    f"📊 Ваша статистика:\n\n"
                    f"Событий создано: {tg_user.events_created}\n"
                    f"Событий отредактировано: {tg_user.events_edited}\n"
                    f"Событий удалено: {tg_user.events_cancelled}"
                )
            else:
                text = "Сначала зарегистрируйтесь: /register"
        except Exception:
            text = "Сначала зарегистрируйтесь: /register"
        safe_edit(text, get_menu_keyboard())

    elif action == "menu_create":
        create_context[query.from_user.id] = {"step": "create"}
        safe_edit(
            "➕ Создание нового события\n\n"
            "Введите название, дату и время через пробел:\n"
            "Пример: Встреча 2026-11-15 15:30\n\n"
            "Или используйте команду: /create_event <название> <дата> <время>",
            get_menu_keyboard()
        )

    elif action == "menu_all":
        events = _services.calendar.get_all_events(query.from_user.id)
        if events:
            lines = [f"№{e['id']}: {html.escape(str(e['name']))} — {html.escape(str(e['date']))} {html.escape(str(e['time']))}" for e in events]
            text = "Ваши события:\n" + "\n".join(lines)
        else:
            # Обновляем счётчик событий, если они были удалены
            tg_user = get_user(query.from_user.id)
            if tg_user:
                tg_user.events_created = 0
                tg_user.save()
            text = "У вас пока нет событий."
        safe_edit(text, get_menu_keyboard())

    elif action == "menu_meetings":
        meetings = Meeting.objects.filter(
            participant_id=query.from_user.id,
            status__in=['pending', 'confirmed']
        ).order_by('date', 'time')
        if not meetings:
            text = "У вас нет запланированных встреч."
        else:
            lines = ["Ваши встречи:\n"]
            for m in meetings:
                emoji = STATUS_EMOJI.get(m.status, "•")
                lines.append(
                    f"{emoji} {html.escape(m.title)}\n"
                    f"   Дата: {html.escape(str(m.date))}  Время: {html.escape(str(m.time))}\n"
                    f"   Организатор: {html.escape(m.organizer_name)}\n"
                    f"   Статус: {html.escape(m.get_status_display())}\n"
                )
            text = "\n".join(lines)
        safe_edit(text, get_menu_keyboard())

    elif action == "menu_public":
        events = _services.calendar.get_public_events(query.from_user.id)
        if not events:
            text = "Пока нет публичных событий от других пользователей."
        else:
            lines = []
            for ev in events:
                owner_name = get_owner_name(ev["owner_id"])
                lines.append(
                    f"№{ev['id']} — {html.escape(str(ev['name']))}\n"
                    f"  Дата: {html.escape(str(ev['date']))}  Время: {html.escape(str(ev['time']))}\n"
                    f"  Автор: {html.escape(owner_name)}"
                )
            text = "🌍 Публичные события других пользователей:\n\n" + "\n\n".join(lines)
        safe_edit(text, get_menu_keyboard())

    elif action == "menu_register":
        safe_edit(
            "👤 Для регистрации используйте команду:\n"
            "/register\n\n"
            "После регистрации вам станут доступны все функции бота.",
            get_menu_keyboard()
        )

    elif action == "menu_read":
        read_context[query.from_user.id] = {"step": "read"}
        safe_edit(
            "📖 Просмотр события\n\n"
            "Введите ID события:\n"
            "Пример: 1",
            get_menu_keyboard()
        )

    elif action == "menu_edit":
        edit_context[query.from_user.id] = {"step": "edit"}
        safe_edit(
            "✏️ Редактирование события\n\n"
            "Введите ID, дату, время и новое название через пробел:\n"
            "Пример: 1 2026-12-01 10:00 Новое название\n\n"
            "Или используйте команду: /edit_event <id> <дата> <время> <название>",
            get_menu_keyboard()
        )

    elif action == "menu_delete":
        delete_context[query.from_user.id] = {"step": "delete"}
        safe_edit(
            "🗑️ Удаление события\n\n"
            "Введите ID события:\n"
            "Пример: 1",
            get_menu_keyboard()
        )


def public_callback_handler(update, context):
    """Обработчик кнопок публичности события."""
    query = update.callback_query
    try:
        query.answer()
    except Exception:
        pass  # Кнопка истекла или невалидна

    _, event_id = query.data.split("_")
    event_id = int(event_id)

    user = query.from_user
    new_status = _services.calendar.toggle_public(user.id, event_id)
    if new_status is None:
        query.edit_message_text("Событие не найдено или не принадлежит вам.")
        return

    button_text = "Сделать приватным" if new_status else "Сделать публичным"
    keyboard = [[InlineKeyboardButton(button_text, callback_data=f"public_{event_id}")]]
    old_text = query.message.text
    public_str = "да" if new_status else "нет"
    new_text = re.sub(r"Публичное: .+", f"Публичное: {public_str}", old_text)
    query.edit_message_text(new_text, reply_markup=InlineKeyboardMarkup(keyboard))
