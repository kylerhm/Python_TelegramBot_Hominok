"""
Входная точка Telegram-бота.
Настройка и запуск poller'а.
"""
import sys
from telegram.ext import Updater

from config import API_TOKEN, DB_HOST, DB_PORT, DB_NAME, DB_USER, DB_PASSWORD
from models import Calendar
from handlers import register_handlers


def main():
    """Настройка и запуск бота."""
    calendar = Calendar()

    # --- Сброс последовательности ID при пустом календаре ---
    try:
        from django.db import connection
        with connection.cursor() as cursor:
            cursor.execute("SELECT COUNT(*) FROM events;")
            count = cursor.fetchone()[0]
            if count == 0:
                cursor.execute("ALTER SEQUENCE events_id_seq RESTART WITH 1;")
                print("Последовательность ID сброшена (календарь пуст)")
    except Exception as e:
        print(f"Не удалось сбросить последовательность: {e}")

    # --- Настройка бота ---
    updater = Updater(API_TOKEN)
    dispatcher = updater.dispatcher

    # Передаём calendar в services (для контекстов)
    import services
    services.calendar = calendar

    # Регистрация всех хендлеров
    register_handlers(dispatcher)

    print("Бот запущен и ждёт команд...")
    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    main()
