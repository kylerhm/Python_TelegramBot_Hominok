from handlers.registration import is_registered
from datetime import datetime
from telegram import Update
from telegram.ext import ContextTypes, ConversationHandler
from config import EVENT_DATE, EVENT_DESC, EVENT_NAME, EVENT_TIME, INVALID_DATE, INVALID_TIME


async def show_events(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    conn = context.bot_data['conn']
    if not is_registered(conn, user_id):
        await update.message.reply_text("Сначала зарегистрируйтесь: /register")
        return
    calendar = context.bot_data['calendar']
    text = calendar.get_events(user_id)
    await update.message.reply_text(text)


async def add_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    conn = context.bot_data['conn']
    if not is_registered(conn, user_id):
        await update.message.reply_text(
            "Сначала зарегистрируйтесь: /register"
        )
        return ConversationHandler.END
    await update.message.reply_text("Введите название события (или /cancel для отмены):")
    return EVENT_NAME


async def add_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Сохранить название и запросить дату."""
    context.user_data['event_name'] = update.message.text
    await update.message.reply_text("Введите дату в формате ГГГГ-ММ-ДД:")
    return EVENT_DATE


async def add_date(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Валидировать дату и запросить время."""
    text = update.message.text
    try:
        datetime.strptime(text, "%Y-%m-%d")
    except ValueError:
        await update.message.reply_text(INVALID_DATE)
        return EVENT_DATE
    context.user_data['event_date'] = text
    await update.message.reply_text("Введите время в формате ЧЧ:ММ:")
    return EVENT_TIME


async def add_time(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Валидировать время и запросить описание."""
    text = update.message.text
    try:
        datetime.strptime(text, "%H:%M")
    except ValueError:
        await update.message.reply_text(INVALID_TIME)
        return EVENT_TIME
    context.user_data['event_time'] = text
    await update.message.reply_text("Введите описание (или отправьте «-», чтобы пропустить):")
    return EVENT_DESC


async def add_desc(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Сохранить описание и создать событие."""
    desc = update.message.text
    if desc == "-":
        desc = ""
    user_id = update.effective_user.id
    calendar = context.bot_data['calendar']
    result = calendar.create_event(
        user_id,
        context.user_data['event_name'],
        context.user_data['event_date'],
        context.user_data['event_time'],
        desc,
    )
    await update.message.reply_text(result)
    context.user_data.clear()
    return ConversationHandler.END