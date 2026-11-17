from telegram import Update
from telegram.ext import ContextTypes, ConversationHandler
from config import HELP_TEXT


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Приветствие пользователя."""
    await update.message.reply_text("Привет! Я бот-календарь. Нажми /help, чтобы увидеть команды.")


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Вывести справку по командам."""
    await update.message.reply_text(HELP_TEXT)


async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Отменить текущий диалог."""
    context.user_data.clear()
    await update.message.reply_text("Диалог отменён.")
    return ConversationHandler.END