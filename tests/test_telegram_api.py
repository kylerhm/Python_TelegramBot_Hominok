"""
Тесты для интеграции с Telegram API.
Проверяют корректность работы с Telegram Bot API.
"""
import os
import pytest
from unittest.mock import Mock, patch, MagicMock


class TestTelegramAPIIntegration:
    """Тесты интеграции с Telegram API."""

    def test_bot_token_is_set(self):
        """Тест: токен бота загружен из переменных окружения."""
        token = os.getenv("TELEGRAM_BOT_TOKEN")
        assert token is not None, "TELEGRAM_BOT_TOKEN не задан"
        assert token != "your_bot_token_here", "Токен бота не задан"
        assert ":" in token, "Неверный формат токена бота"

    def test_bot_token_format(self):
        """Тест: токен бота имеет правильный формат."""
        token = os.getenv("TELEGRAM_BOT_TOKEN")
        # Токен Telegram имеет формат: ID:SECRET
        parts = token.split(":")
        assert len(parts) == 2, "Токен должен содержать ':'"
        assert parts[0].isdigit(), "Первая часть токена должна быть числом"
        assert len(parts[1]) >= 30, "Секретная часть токена слишком короткая"

    def test_django_setup(self):
        """Тест: Django корректно настроен."""
        import django
        from django.conf import settings

        assert django.conf.settings.DATABASES is not None
        assert "default" in django.conf.settings.DATABASES
        assert settings.INSTALLED_APPS is not None
        assert "events" in settings.INSTALLED_APPS

    def test_telegram_bot_import(self):
        """Тест: библиотека python-telegram-bot доступна."""
        try:
            import telegram
            import telegram.ext
            assert telegram is not None
            assert telegram.ext is not None
        except ImportError as e:
            pytest.fail(f"Не удалось импортировать telegram: {e}")

    def test_bot_can_connect_to_api(self):
        """Тест: бот может подключиться к Telegram API (mock)."""
        from telegram import Bot
        from unittest.mock import MagicMock
        
        token = os.getenv("TELEGRAM_BOT_TOKEN")
        
        # Мокаем ответ API внутри теста
        mock_user = Mock()
        mock_user.id = 123456789
        mock_user.username = "test_bot"
        mock_user.first_name = "Test"
        
        with patch.object(Bot, 'get_me', MagicMock(return_value=mock_user)) as mock_get_me:
            bot = Bot(token=token)

            # Проверяем, что get_me вызывается корректно
            result = bot.get_me()
            assert result is not None
            assert result.username == "test_bot"

    def test_config_loads_correctly(self):
        """Тест: конфигурация загружается корректно."""
        from config import API_TOKEN, DB_HOST, DB_NAME, DB_USER, DB_PASSWORD

        assert API_TOKEN is not None
        assert DB_HOST is not None
        assert DB_NAME is not None
        assert DB_USER is not None
        assert DB_PASSWORD is not None

    def test_export_api_url_configured(self):
        """Тест: URL для экспорта событий настроен."""
        from config import EXPORT_API_URL

        assert EXPORT_API_URL is not None
        assert "localhost" in EXPORT_API_URL or "127.0.0.1" in EXPORT_API_URL
        assert "8000" in EXPORT_API_URL


class TestTelegramBotHandlers:
    """Тесты обработчиков Telegram бота."""

    def test_menu_keyboard_structure(self):
        """Тест: структура клавиатуры меню корректна."""
        from services import get_menu_keyboard
        from telegram import InlineKeyboardMarkup

        keyboard = get_menu_keyboard()
        assert isinstance(keyboard, InlineKeyboardMarkup)
        assert len(keyboard.inline_keyboard) > 0
        # Проверяем, что есть кнопки
        for row in keyboard.inline_keyboard:
            assert len(row) > 0
            for button in row:
                assert button.text is not None
                assert button.callback_data is not None

    def test_commands_help_text_exists(self):
        """Тест: текст помощи с командами существует."""
        from services import COMMANDS_HELP

        assert COMMANDS_HELP is not None
        assert len(COMMANDS_HELP) > 0
        assert "/register" in COMMANDS_HELP
        assert "/calendar" in COMMANDS_HELP
        assert "/create_event" in COMMANDS_HELP

    def test_status_emoji_mapping(self):
        """Тест: отображение статусов встреч корректно."""
        from services import STATUS_EMOJI

        assert "pending" in STATUS_EMOJI
        assert "confirmed" in STATUS_EMOJI
        assert "cancelled" in STATUS_EMOJI
        assert STATUS_EMOJI["pending"] == "⏳"
        assert STATUS_EMOJI["confirmed"] == "✅"
        assert STATUS_EMOJI["cancelled"] == "❌"

    def test_meeting_steps_defined(self):
        """Тест: шаги создания встречи определены."""
        from services import MEETING_STEPS

        assert MEETING_STEPS == ["title", "participant", "date", "time"]

    def test_contexts_initialized(self):
        """Тест: контексты многошаговых команд инициализированы."""
        from services import (
            meeting_context, create_context, edit_context,
            read_context, delete_context
        )

        assert isinstance(meeting_context, dict)
        assert isinstance(create_context, dict)
        assert isinstance(edit_context, dict)
        assert isinstance(read_context, dict)
        assert isinstance(delete_context, dict)


class TestTelegramBotUtils:
    """Тесты утилит бота."""

    def test_parse_event_id_valid(self):
        """Тест: парсинг ID события с валидными данными."""
        from utils.parsers import parse_event_id

        assert parse_event_id(["1"]) == 1
        assert parse_event_id(["123"]) == 123
        assert parse_event_id(["999999"]) == 999999

    def test_parse_event_id_empty(self):
        """Тест: парсинг ID события с пустыми данными."""
        from utils.parsers import parse_event_id

        with pytest.raises(ValueError):
            parse_event_id([])

    def test_parse_event_id_invalid(self):
        """Тест: парсинг ID события с невалидными данными."""
        from utils.parsers import parse_event_id

        with pytest.raises(ValueError):
            parse_event_id(["abc"])

    def test_require_registration_decorator_exists(self):
        """Тест: декоратор require_registration существует."""
        from utils.decorators import require_registration

        assert callable(require_registration)

    def test_handle_errors_decorator_exists(self):
        """Тест: декоратор handle_errors существует."""
        from utils.decorators import handle_errors

        assert callable(handle_errors)

    def test_group_events_by_date(self):
        """Тест: группировка событий по дате."""
        from utils.formatters import group_events_by_date

        events = [
            {"id": 1, "date": "2026-11-20", "name": "Event 1"},
            {"id": 2, "date": "2026-11-20", "name": "Event 2"},
            {"id": 3, "date": "2026-11-21", "name": "Event 3"},
        ]

        grouped = group_events_by_date(events)
        assert "2026-11-20" in grouped
        assert "2026-11-21" in grouped
        assert len(grouped["2026-11-20"]) == 2
        assert len(grouped["2026-11-21"]) == 1

    def test_format_events_text_empty(self):
        """Тест: форматирование пустого календаря."""
        from utils.formatters import format_events_text

        result = format_events_text({})
        assert result is None

    def test_format_events_text_with_events(self):
        """Тест: форматирование событий с данными."""
        from utils.formatters import format_events_text, group_events_by_date

        events = [
            {"id": 1, "date": "2026-11-20", "time": "14:00", "name": "Test"},
        ]
        grouped = group_events_by_date(events)
        result = format_events_text(grouped)

        assert result is not None
        assert "2026-11-20" in result
        assert "Test" in result
        assert "14:00" in result
