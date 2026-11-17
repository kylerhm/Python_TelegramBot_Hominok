import logging
from telegram import Update
import psycopg2
from telegram.ext import (
    Application,
    CommandHandler,
    ContextTypes,
    ConversationHandler,
    MessageHandler,
    filters,
)
from secrets import API_TOKEN, DB_HOST, DB_NAME, DB_USER, DB_PASS
from calendar_logic import Calendar

from handlers.common import cancel, help_command, start
from handlers.edit_delete import (
    delete_name,
    delete_start,
    edit_date,
    edit_name,
    edit_start,
    edit_time,
)
from handlers.registration import register
from handlers.events import (
    add_date,
    add_desc,
    add_name,
    add_start,
    add_time,
    show_events,
)
from config import (
    DELETE_NAME,
    EDIT_DATE,
    EDIT_NAME,
    EDIT_TIME,
    EVENT_DATE,
    EVENT_DESC,
    EVENT_NAME,
    EVENT_TIME,
)

# Включаем логи, чтобы видеть ошибки
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO,
)


async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE):
    print(f"ОШИБКА: {context.error}")


def main():
    # Создаём приложение с нашим токеном
    application = Application.builder().token(API_TOKEN).build()

    application.add_handler(CommandHandler("start", start))

    if not all([DB_HOST, DB_NAME, DB_USER, DB_PASS, API_TOKEN]):
        logging.error("Не все необходимые переменные окружения заданы. Проверьте .env файл.")
        return

    try:
        conn = psycopg2.connect(
            host=DB_HOST,
            database=DB_NAME,
            user=DB_USER,
            password=DB_PASS
        )
    except psycopg2.OperationalError as e:
        logging.error(f"Не удалось подключиться к базе данных: {e}")
        return

    calendar = Calendar(conn)
    application.bot_data['calendar'] = calendar
    application.bot_data['conn'] = conn

    
    # Диалог создания события
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("add", add_start)],
        states={
            EVENT_NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, add_name)],
            EVENT_DATE: [MessageHandler(filters.TEXT & ~filters.COMMAND, add_date)],
            EVENT_TIME: [MessageHandler(filters.TEXT & ~filters.COMMAND, add_time)],
            EVENT_DESC: [MessageHandler(filters.TEXT & ~filters.COMMAND, add_desc)],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )
    application.add_handler(conv_handler)

    # Диалог удаления событий
    delete_conv = ConversationHandler(
        entry_points=[CommandHandler("delete", delete_start)],
        states={
            DELETE_NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, delete_name)],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )
    application.add_handler(delete_conv)

    # Диалог редактирования событий
    edit_conv = ConversationHandler(
        entry_points=[CommandHandler("edit", edit_start)],
        states={
            EDIT_NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, edit_name)],
            EDIT_DATE: [MessageHandler(filters.TEXT & ~filters.COMMAND, edit_date)],
            EDIT_TIME: [MessageHandler(filters.TEXT & ~filters.COMMAND, edit_time)],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )
    application.add_handler(edit_conv)

    # Остальные обработчики
    application.add_handler(CommandHandler("events", show_events))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("register", register))

    # Запускаем бота (он будет работать, пока вы не остановите его)
    print("Бот запущен...")

    application.add_error_handler(error_handler)

    try:
        application.run_polling()
    except KeyboardInterrupt:
        conn.close()
        print("Бот остановлен.")


if __name__ == '__main__':
    main()