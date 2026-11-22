"""
Пакет обработчиков Telegram-бота.
Регистрация всех хендлеров в dispatcher.
"""
from telegram.ext import Filters, CommandHandler, CallbackQueryHandler, MessageHandler


def make_calendar_handler(handler):
    """Обёртка для передачи calendar в обработчики."""
    def wrapper(update, context):
        return handler(update, context)
    return wrapper


def register_handlers(dispatcher):
    """Регистрирует все обработчики в dispatcher."""
    from handlers.commands import (
        start_handler, register_handler, login_handler, calendar_handler,
        my_stats_handler, event_create_handler, event_read_handler,
        event_edit_handler, event_delete_handler, event_show_all_handler,
        public_events_handler, share_event_handler, export_events_handler,
    )
    from handlers.callbacks import menu_callback_handler, public_callback_handler
    from handlers.meetings import (
        invite_meeting, my_meetings, meeting_callback_handler, text_handler,
    )

    # Основные команды
    dispatcher.add_handler(CommandHandler('start', start_handler))
    dispatcher.add_handler(CommandHandler('register', register_handler))
    dispatcher.add_handler(CommandHandler('login', login_handler))

    # Команды календаря
    dispatcher.add_handler(CommandHandler('calendar', make_calendar_handler(calendar_handler)))
    dispatcher.add_handler(CommandHandler('my_stats', my_stats_handler))
    dispatcher.add_handler(CommandHandler('create_event', make_calendar_handler(event_create_handler)))
    dispatcher.add_handler(CommandHandler('read_event', make_calendar_handler(event_read_handler)))
    dispatcher.add_handler(CommandHandler('edit_event', make_calendar_handler(event_edit_handler)))
    dispatcher.add_handler(CommandHandler('delete_event', make_calendar_handler(event_delete_handler)))
    dispatcher.add_handler(CommandHandler('all_events', make_calendar_handler(event_show_all_handler)))
    dispatcher.add_handler(CommandHandler('public_events', make_calendar_handler(public_events_handler)))
    dispatcher.add_handler(CommandHandler('share_event', make_calendar_handler(share_event_handler)))

    # Callback-обработчики
    dispatcher.add_handler(CallbackQueryHandler(
        make_calendar_handler(public_callback_handler), pattern=r"^public_"
    ))
    dispatcher.add_handler(CallbackQueryHandler(menu_callback_handler, pattern=r"^menu_"))

    # Команды встреч
    dispatcher.add_handler(CommandHandler('invite_meeting', invite_meeting))
    dispatcher.add_handler(CommandHandler('my_meetings', my_meetings))
    dispatcher.add_handler(CallbackQueryHandler(meeting_callback_handler, pattern=r"^(confirm|decline)_"))

    # Экспорт и текстовые сообщения
    dispatcher.add_handler(CommandHandler('export', export_events_handler))
    dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, text_handler))
