"""
Бизнес-логика бота: управление пользователями, контексты, встречи.
"""
import datetime
import html
import logging
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from events.models import TelegramUser, Meeting

logger = logging.getLogger(__name__)

# Глобальные контексты для многошаговых команд
meeting_context = {}
create_context = {}
edit_context = {}
read_context = {}
delete_context = {}

# Статусы встреч
STATUS_EMOJI = {"pending": "⏳", "confirmed": "✅", "cancelled": "❌"}

# Справочные тексты
COMMANDS_HELP = (
    "📋 Доступные команды:\n\n"
    "👤 Регистрация:\n"
    "/register — повторная регистрация\n"
    "/login — вход в личный кабинет\n\n"
    "📅 События:\n"
    "/calendar — мой календарь\n"
    "/create_event <название> <дата> <время> — создать событие\n"
    "/read_event <id> — посмотреть событие\n"
    "/edit_event <id> <дата> <время> <название> — редактировать\n"
    "/delete_event <id> — удалить событие\n"
    "/all_events — все ваши события\n"
    "/share_event <id> — сделать публичным/приватным\n\n"
    "📊 Статистика:\n"
    "/my_stats — моя статистика\n\n"
    "🤝 Встречи:\n"
    "/invite_meeting — пригласить на встречу\n"
    "/my_meetings — мои встречи\n\n"
    "📤 Экспорт:\n"
    "/public_events — публичные события\n"
    "/export — выгрузить события в CSV или JSON"
)


def get_menu_keyboard():
    """Создаёт клавиатуру с основными командами."""
    keyboard = [
        [
            InlineKeyboardButton("📅 Мой календарь", callback_data="menu_calendar"),
            InlineKeyboardButton("📊 Статистика", callback_data="menu_stats"),
        ],
        [
            InlineKeyboardButton("➕ Создать", callback_data="menu_create"),
            InlineKeyboardButton("📋 Все события", callback_data="menu_all"),
        ],
        [
            InlineKeyboardButton("📖 Посмотреть", callback_data="menu_read"),
            InlineKeyboardButton("✏️ Редактировать", callback_data="menu_edit"),
        ],
        [
            InlineKeyboardButton("🗑️ Удалить", callback_data="menu_delete"),
            InlineKeyboardButton("🤝 Встречи", callback_data="menu_meetings"),
        ],
        [
            InlineKeyboardButton("🌍 Публичные", callback_data="menu_public"),
        ],
        [
            InlineKeyboardButton("👤 Регистрация", callback_data="menu_register"),
        ],
    ]
    return InlineKeyboardMarkup(keyboard)


# --- Управление пользователями ---

def register_user(telegram_id, username, first_name=""):
    """Создание или обновление пользователя."""
    from django.db import connection
    try:
        user, created = TelegramUser.objects.get_or_create(
            telegram_id=telegram_id,
            defaults={"username": username or "", "first_name": first_name or ""}
        )
        if not created:
            if username:
                user.username = username
            if first_name:
                user.first_name = first_name
            user.save()
        logger.info(f"[REGISTER] telegram_id={telegram_id}, created={created}")
        # Проверка: пользователь действительно в БД
        check = TelegramUser.objects.filter(telegram_id=telegram_id).exists()
        logger.info(f"[REGISTER] Verified in DB: {check}")
        return user
    except Exception as e:
        logger.error(f"[REGISTER ERROR] {type(e).__name__}: {e}", exc_info=True)
        return None


def get_user(telegram_id):
    """Получение пользователя по telegram_id."""
    try:
        return TelegramUser.objects.get(telegram_id=telegram_id)
    except TelegramUser.DoesNotExist:
        return None


# --- Логика встреч ---

MEETING_STEPS = ["title", "participant", "date", "time"]


def _parse_meeting_input(step, text):
    """Парсит ввод пользователя на каждом шаге."""
    if step == "title":
        return text, None
    if step == "participant":
        try:
            return int(text), None
        except ValueError:
            return None, "Нужно ввести число. Попробуйте снова:"
    if step == "date":
        try:
            return datetime.datetime.strptime(text, "%Y-%m-%d").date(), None
        except ValueError:
            return None, "Неверный формат. Пример: 2025-01-15"
    if step == "time":
        try:
            return datetime.datetime.strptime(text, "%H:%M").time(), None
        except ValueError:
            return None, "Неверный формат. Пример: 14:30"
    return None, None


def _process_meeting_step(update, context, ctx, text):
    """Обрабатывает один шаг создания встречи."""
    step = ctx["step"]
    value, error = _parse_meeting_input(step, text)

    if error:
        update.message.reply_text(error)
        return True

    ctx[step] = value
    next_step = MEETING_STEPS[MEETING_STEPS.index(step) + 1] if step != "time" else None

    if next_step:
        prompts = {
            "participant": "Введите Telegram ID участника (число):",
            "date": "Введите дату встречи (ГГГГ-ММ-ДД):",
            "time": "Введите время встречи (ЧЧ:ММ):",
        }
        ctx["step"] = next_step
        update.message.reply_text(prompts[next_step])
        return True

    # Финальный шаг — создаём встречу
    return _finalize_meeting(update, context, ctx)


def _finalize_meeting(update, context, ctx):
    """Создаёт встречу и отправляет приглашение."""
    user = update.effective_user

    if not is_user_free(ctx["participant_id"], ctx["date"], ctx["time"]):
        update.message.reply_text("Участник занят в это время. Выберите другое время.")
        ctx["step"] = "date"
        update.message.reply_text("Введите новую дату (ГГГГ-ММ-ДД):")
        return True

    organizer_name = user.username or user.first_name or str(user.id)
    meeting = Meeting.objects.create(
        title=html.escape(ctx["title"]),
        date=ctx["date"],
        time=ctx["time"],
        organizer_id=user.id,
        organizer_name=html.escape(organizer_name),
        participant_id=ctx["participant_id"],
        participant_name="",
        status='pending'
    )

    keyboard = [[
        InlineKeyboardButton("Подтвердить", callback_data=f"confirm_{meeting.id}"),
        InlineKeyboardButton("Отклонить", callback_data=f"decline_{meeting.id}"),
    ]]

    try:
        context.bot.send_message(
            chat_id=ctx["participant_id"],
            text=(
                f"Вас приглашают на встречу!\n\n"
                f"Название: {ctx['title']}\n"
                f"Организатор: {organizer_name}\n"
                f"Дата: {ctx['date']}\n"
                f"Время: {ctx['time']}\n\n"
                f"Подтверждаете или отклоняете?"
            ),
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
        update.message.reply_text(f"Приглашение отправлено пользователю {ctx['participant_id']}.")
    except Exception as e:
        update.message.reply_text(
            f"Не удалось отправить приглашение. "
            f"Возможно, пользователь не запускал бота. Ошибка: {e}"
        )

    del meeting_context[user.id]
    return True


def is_user_free(telegram_id, meeting_date, meeting_time):
    """Проверка свободности участника в указанное время."""
    return not Meeting.objects.filter(
        participant_id=telegram_id,
        date=meeting_date,
        time=meeting_time,
        status__in=['pending', 'confirmed']
    ).exists()
