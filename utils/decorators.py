"""
Декораторы для обработчиков бота.
"""
import functools
import logging
from django.db import connection
from events.models import TelegramUser

logger = logging.getLogger(__name__)


def require_registration(handler):
    """Декоратор: проверяет, что пользователь зарегистрирован."""
    @functools.wraps(handler)
    def wrapper(update, context):
        user = update.effective_user
        if not TelegramUser.objects.filter(telegram_id=user.id).exists():
            update.message.reply_text("Сначала зарегистрируйтесь: /register")
            return
        return handler(update, context)
    return wrapper


def handle_errors(handler):
    """Декоратор: перехватывает ошибки и отправляет сообщение пользователю."""
    @functools.wraps(handler)
    def wrapper(update, context):
        try:
            return handler(update, context)
        except ValueError:
            update.message.reply_text("ID события должно быть числом.")
        except Exception as e:
            logger.error(f"Error in handler: {e}", exc_info=True)
            update.message.reply_text("Произошла ошибка. Попробуйте позже.")
    return wrapper
