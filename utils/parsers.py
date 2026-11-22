"""
Парсеры для обработки входных данных.
"""
from events.models import TelegramUser


def parse_event_id(args):
    """Парсит ID события из аргументов команды. Бросает ValueError при ошибке."""
    if not args:
        raise ValueError("Аргумент не передан")
    return int(args[0])


def get_owner_name(owner_id):
    """Возвращает имя пользователя по telegram_id или 'Аноним'."""
    try:
        owner = TelegramUser.objects.get(telegram_id=owner_id)
        return owner.username or owner.first_name or "Аноним"
    except TelegramUser.DoesNotExist:
        return "Аноним"
