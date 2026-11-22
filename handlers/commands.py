"""
Обработчики команд Telegram-бота.
"""
import re
import html
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from events.models import TelegramUser, Meeting
from utils import (
    require_registration, handle_errors, parse_event_id,
    get_owner_name, group_events_by_date, format_events_text,
    format_public_events_text,
)
from services import (
    get_user, get_menu_keyboard, COMMANDS_HELP,
    meeting_context, create_context, edit_context, read_context, delete_context,
    STATUS_EMOJI,
)
from config import EXPORT_API_URL

# calendar устанавливается динамически в main.py
import services as _services


# --- Обработчики команд ---

def start_handler(update, context):
    """Обработчик команды /start."""
    user = update.effective_user
    if TelegramUser.objects.filter(telegram_id=user.id).exists():
        update.message.reply_text(
            f"Привет, {user.first_name}! Вы уже зарегистрированы.\n\n" + COMMANDS_HELP,
            reply_markup=get_menu_keyboard()
        )
    else:
        update.message.reply_text(
            f"Привет, {user.first_name}! Вы ещё не зарегистрированы.\n"
            f"Используйте /register для регистрации.",
            reply_markup=get_menu_keyboard()
        )


def register_handler(update, context):
    """Обработчик команды /register."""
    from services import register_user
    user = update.effective_user
    username = user.username or user.first_name or str(user.id)
    register_user(user.id, username, user.first_name or "")
    update.message.reply_text(
        f"Вы успешно зарегистрированы, {username}!\n\n"
        f"Теперь вам доступны:\n"
        f"/calendar — ваш календарь\n"
        f"/create_event <название> <дата> <время> — создать событие\n"
        f"/my_stats — ваша статистика",
        reply_markup=get_menu_keyboard()
    )


def login_handler(update, context):
    """Обработчик команды /login."""
    user = update.effective_user
    tg_user = get_user(user.id)
    if not tg_user:
        update.message.reply_text("Вы ещё не зарегистрированы. Используйте /register.")
        return

    update.message.reply_text(
        f"Вы вошли в личный кабинет.\n"
        f"ID: {tg_user.telegram_id}\n"
        f"Имя: {tg_user.username or tg_user.first_name}\n"
        f"Событий создано: {tg_user.events_created}\n"
        f"Событий отредактировано: {tg_user.events_edited}\n"
        f"Событий удалено: {tg_user.events_cancelled}\n\n"
        f"Команды:\n/calendar — мой календарь\n/my_stats — моя статистика"
    )


def calendar_handler(update, context):
    """Обработчик команды /_services.calendar."""
    user = update.effective_user

    if not TelegramUser.objects.filter(telegram_id=user.id).exists():
        update.message.reply_text("Сначала зарегистрируйтесь: /register")
        return

    events = _services.calendar.get_all_events(user.id)
    text = format_events_text(group_events_by_date(events), "📅 Ваш календарь:")
    if not text:
        text = "📅 Ваш календарь пуст. Создайте событие: /create_event <название> <дата> <время>\n\n"

    public_events = _services.calendar.get_public_events(user.id)
    public_text = format_public_events_text(public_events)
    if public_text:
        text += public_text

    update.message.reply_text(text)


@require_registration
@handle_errors
def my_stats_handler(update, context):
    """Обработчик команды /my_stats."""
    tg_user = get_user(update.effective_user.id)
    update.message.reply_text(
        f"📊 Ваша статистика:\n\n"
        f"Событий создано: {tg_user.events_created}\n"
        f"Событий отредактировано: {tg_user.events_edited}\n"
        f"Событий удалено: {tg_user.events_cancelled}\n"
    )


@require_registration
@handle_errors
def event_create_handler(update, context):
    """Обработчик команды /create_event."""
    print(f"[DEBUG] event_create_handler START, args={context.args}")
    if not context.args:
        update.message.reply_text("Укажите название, дату и время: /create_event <название> <дата> <время>\nПример: /create_event Встреча 2026-11-15 15:30")
        print("[DEBUG] No args")
        return

    event_name = " ".join(context.args).strip()
    print(f"[DEBUG] event_name='{event_name}'")
    if not event_name:
        update.message.reply_text("Название не может быть пустым.")
        return

    try:
        print(f"[DEBUG] Calling calendar.create_event...")
        event_id = _services.calendar.create_event(
            update.effective_user.id, event_name, "2026-10-06", "14:00", "Описание события"
        )
        print(f"[DEBUG] event_id={event_id}")
        tg_user = get_user(update.effective_user.id)
        if tg_user:
            tg_user.events_created += 1
            tg_user.save()

        update.message.reply_text(
            f"Событие «{html.escape(event_name)}» создано и имеет номер {event_id}."
        )
        print("[DEBUG] event_create_handler END - SUCCESS")
    except Exception as e:
        print(f"[DEBUG] create_event error: {e}")
        raise


@require_registration
@handle_errors
def event_read_handler(update, context):
    """Обработчик команды /read_event."""
    event_id = parse_event_id(context.args)
    event = _services.calendar.read_event(update.effective_user.id, event_id)
    if not event:
        update.message.reply_text(f"Событие с номером {event_id} не найдено.")
        return

    public_status = "да" if event.get("is_public") else "нет"
    text = (
        f"Событие №{event['id']}\n"
        f"Название: {html.escape(str(event['name']))}\n"
        f"Дата: {html.escape(str(event['date']))}\n"
        f"Время: {html.escape(str(event['time']))}\n"
        f"Описание: {html.escape(str(event['details'] or ''))}\n"
        f"Публичное: {public_status}"
    )
    button_text = "Сделать приватным" if event.get("is_public") else "Сделать публичным"
    keyboard = [[InlineKeyboardButton(button_text, callback_data=f"public_{event_id}")]]
    update.message.reply_text(text, reply_markup=InlineKeyboardMarkup(keyboard))


@require_registration
@handle_errors
def event_edit_handler(update, context):
    """Обработчик команды /edit_event."""
    event_id = parse_event_id(context.args)
    event_name = " ".join(context.args[1:]) if len(context.args) > 1 else None
    success = _services.calendar.edit_event(update.effective_user.id, event_id, event_name=event_name)

    if success:
        tg_user = get_user(update.effective_user.id)
        if tg_user:
            tg_user.events_edited += 1
            tg_user.save()
        update.message.reply_text(f"Событие {event_id} отредактировано.")
    else:
        update.message.reply_text(f"Событие с номером {event_id} не найдено или не принадлежит вам.")


@require_registration
@handle_errors
def event_delete_handler(update, context):
    """Обработчик команды /delete_event."""
    event_id = parse_event_id(context.args)
    success = _services.calendar.delete_event(update.effective_user.id, event_id)

    if success:
        tg_user = get_user(update.effective_user.id)
        if tg_user:
            tg_user.events_cancelled += 1
            # Проверяем, остались ли ещё события
            remaining_events = _services.calendar.get_all_events(update.effective_user.id)
            if not remaining_events:
                tg_user.events_created = 0
                tg_user.save()
                # Сбрасываем последовательность ID
                _services.calendar.reset_id_sequence()
            else:
                tg_user.save()
        update.message.reply_text(f"Событие {event_id} удалено.")
    else:
        update.message.reply_text(f"Событие с номером {event_id} не найдено или не принадлежит вам.")


@require_registration
@handle_errors
def event_show_all_handler(update, context):
    """Обработчик команды /all_events."""
    events = _services.calendar.get_all_events(update.effective_user.id)
    if events:
        lines = [f"№{e['id']}: {html.escape(str(e['name']))} — {html.escape(str(e['date']))} {html.escape(str(e['time']))}" for e in events]
        update.message.reply_text("Ваши события:\n" + "\n".join(lines))
    else:
        update.message.reply_text("У вас пока нет событий.")


@require_registration
@handle_errors
def public_events_handler(update, context):
    """Обработчик команды /public_events."""
    events = _services.calendar.get_public_events(update.effective_user.id)
    if not events:
        update.message.reply_text("Пока нет публичных событий от других пользователей.")
        return

    lines = []
    for ev in events:
        owner_name = get_owner_name(ev["owner_id"])
        lines.append(
            f"№{ev['id']} — {html.escape(str(ev['name']))}\n"
            f"  Дата: {html.escape(str(ev['date']))}  Время: {html.escape(str(ev['time']))}\n"
            f"  Автор: {html.escape(owner_name)}"
        )
    update.message.reply_text("🌍 Публичные события других пользователей:\n\n" + "\n\n".join(lines))


@require_registration
@handle_errors
def share_event_handler(update, context):
    """Обработчик команды /share_event."""
    event_id = parse_event_id(context.args)
    new_status = _services.calendar.toggle_public(update.effective_user.id, event_id)
    if new_status is None:
        update.message.reply_text("Событие не найдено или не принадлежит вам.")
    else:
        status = "публичным" if new_status else "приватным"
        update.message.reply_text(f"Событие №{event_id} стало {status}.")


@require_registration
def export_events_handler(update, context):
    """Обработчик команды /export."""
    user = update.effective_user
    keyboard = [[
        InlineKeyboardButton("Скачать в CSV", url=f"{EXPORT_API_URL}?format=csv&telegram_id={user.id}"),
        InlineKeyboardButton("Скачать в JSON", url=f"{EXPORT_API_URL}?format=json&telegram_id={user.id}")
    ]]
    update.message.reply_text("Выберите формат выгрузки:", reply_markup=InlineKeyboardMarkup(keyboard))
