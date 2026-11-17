from handlers.registration import is_registered
from datetime import datetime
from telegram import Update
from telegram.ext import ContextTypes, ConversationHandler
from config import DELETE_NAME, EDIT_DATE, EDIT_NAME, EDIT_TIME, INVALID_DATE, INVALID_TIME


# ---------- Удаление ----------


async def delete_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    conn = context.bot_data['conn']
    if not is_registered(conn, user_id):
        await update.message.reply_text("Сначала зарегистрируйтесь: /register")
        return ConversationHandler.END
    await update.message.reply_text("Введите название события для удаления (или /cancel):")
    return DELETE_NAME


async def delete_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    name = update.message.text
    user_id = update.effective_user.id
    calendar = context.bot_data['calendar']
    result = calendar.delete_event(user_id, name)
    await update.message.reply_text(result)
    return ConversationHandler.END

# ---------- Редактирование ----------


async def edit_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Начать редактирование события — запросить название."""
    user_id = update.effective_user.id
    conn = context.bot_data['conn']
    if not is_registered(conn, user_id):
        await update.message.reply_text("Сначала зарегистрируйтесь: /register")
        return ConversationHandler.END
    await update.message.reply_text("Введите название события для редактирования (или /cancel):")
    return EDIT_NAME


async def edit_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Сохранить название и запросить новую дату."""
    context.user_data['edit_name'] = update.message.text
    await update.message.reply_text("Введите новую дату (ГГГГ-ММ-ДД):")
    return EDIT_DATE


async def edit_date(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Валидировать новую дату и запросить новое время."""
    text = update.message.text
    try:
        datetime.strptime(text, "%Y-%m-%d")
    except ValueError:
        await update.message.reply_text(INVALID_DATE)
        return EDIT_DATE
    context.user_data['edit_date'] = text
    await update.message.reply_text("Введите новое время (ЧЧ:ММ):")
    return EDIT_TIME


async def edit_time(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Валидировать новое время и обновить событие."""
    text = update.message.text
    try:
        datetime.strptime(text, "%H:%M")
    except ValueError:
        await update.message.reply_text(INVALID_TIME)
        return EDIT_TIME
    user_id = update.effective_user.id
    calendar = context.bot_data['calendar']
    result = calendar.edit_event(
        user_id,
        context.user_data['edit_name'],
        new_date=context.user_data['edit_date'],
        new_time=text,
    )
    await update.message.reply_text(result)
    context.user_data.clear()
    return ConversationHandler.END