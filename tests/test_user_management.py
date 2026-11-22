"""
Тесты для управления пользователями.
Проверяют регистрацию, авторизацию и управление профилем.
"""
import pytest
from django.test import TestCase
from events.models import TelegramUser


class TestUserRegistration(TestCase):
    """Тесты регистрации пользователей."""

    def test_create_new_user(self):
        """Тест: создание нового пользователя."""
        user = TelegramUser.objects.create(
            telegram_id=123456789,
            username="new_user",
            first_name="New"
        )

        assert user.id is not None
        assert user.telegram_id == 123456789
        assert user.username == "new_user"
        assert user.first_name == "New"
        assert user.events_created == 0
        assert user.events_edited == 0
        assert user.events_cancelled == 0
        assert user.registered_at is not None

    def test_user_with_only_telegram_id(self):
        """Тест: создание пользователя только с telegram_id."""
        user = TelegramUser.objects.create(
            telegram_id=999888777
        )

        assert user.telegram_id == 999888777
        assert user.username == ""
        assert user.first_name == ""

    def test_duplicate_telegram_id_rejected(self):
        """Тест: отклонение дубликата telegram_id."""
        TelegramUser.objects.create(
            telegram_id=111222333,
            username="first"
        )

        with pytest.raises(Exception):
            TelegramUser.objects.create(
                telegram_id=111222333,
                username="second"
            )

    def test_get_or_create_user(self):
        """Тест: get_or_create для пользователя."""
        user1, created1 = TelegramUser.objects.get_or_create(
            telegram_id=444555666,
            defaults={"username": "test", "first_name": "Test"}
        )
        assert created1 is True

        user2, created2 = TelegramUser.objects.get_or_create(
            telegram_id=444555666,
            defaults={"username": "test", "first_name": "Test"}
        )
        assert created2 is False
        assert user1.id == user2.id


class TestUserAuthentication(TestCase):
    """Тесты авторизации и аутентификации."""

    def test_user_exists_by_telegram_id(self):
        """Тест: проверка существования пользователя по telegram_id."""
        user = TelegramUser.objects.create(
            telegram_id=777888999,
            username="auth_user"
        )

        exists = TelegramUser.objects.filter(
            telegram_id=user.telegram_id
        ).exists()

        assert exists is True

    def test_user_not_found(self):
        """Тест: пользователь не найден."""
        exists = TelegramUser.objects.filter(
            telegram_id=000000000
        ).exists()

        assert exists is False

    def test_get_user_by_telegram_id(self):
        """Тест: получение пользователя по telegram_id."""
        user = TelegramUser.objects.create(
            telegram_id=555666777,
            username="get_user_test"
        )

        retrieved = TelegramUser.objects.get(telegram_id=555666777)
        assert retrieved.id == user.id
        assert retrieved.username == "get_user_test"

    def test_get_user_not_found_returns_none(self):
        """Тест: получение несуществующего пользователя возвращает None."""
        from services import get_user

        result = get_user(000000000)
        assert result is None


class TestUserManagement(TestCase):
    """Тесты управления пользователями."""

    def test_update_username(self):
        """Тест: обновление имени пользователя."""
        user = TelegramUser.objects.create(
            telegram_id=111000222,
            username="old_name"
        )

        user.username = "new_name"
        user.save()

        updated = TelegramUser.objects.get(telegram_id=111000222)
        assert updated.username == "new_name"

    def test_update_first_name(self):
        """Тест: обновление первого имени."""
        user = TelegramUser.objects.create(
            telegram_id=333444555,
            first_name="First"
        )

        user.first_name = "Second"
        user.save()

        updated = TelegramUser.objects.get(telegram_id=333444555)
        assert updated.first_name == "Second"

    def test_user_counters_increment(self):
        """Тест: инкремент счётчиков событий."""
        user = TelegramUser.objects.create(
            telegram_id=666777888,
            username="counter_test"
        )

        user.events_created += 1
        user.events_edited += 1
        user.events_cancelled += 1
        user.save()

        updated = TelegramUser.objects.get(telegram_id=666777888)
        assert updated.events_created == 1
        assert updated.events_edited == 1
        assert updated.events_cancelled == 1

    def test_user_counters_reset(self):
        """Тест: сброс счётчиков событий."""
        user = TelegramUser.objects.create(
            telegram_id=999000111,
            username="reset_test"
        )

        user.events_created = 5
        user.events_edited = 3
        user.events_cancelled = 2
        user.save()

        user.events_created = 0
        user.events_edited = 0
        user.events_cancelled = 0
        user.save()

        updated = TelegramUser.objects.get(telegram_id=999000111)
        assert updated.events_created == 0
        assert updated.events_edited == 0
        assert updated.events_cancelled == 0


class TestUserQueries(TestCase):
    """Тесты запросов к пользователям."""

    def test_get_all_users(self):
        """Тест: получение всех пользователей."""
        TelegramUser.objects.create(telegram_id=100, username="user1")
        TelegramUser.objects.create(telegram_id=200, username="user2")
        TelegramUser.objects.create(telegram_id=300, username="user3")

        users = TelegramUser.objects.all()
        assert users.count() == 3

    def test_get_users_by_username(self):
        """Тест: получение пользователей по имени."""
        TelegramUser.objects.create(telegram_id=100, username="john")
        TelegramUser.objects.create(telegram_id=200, username="john")
        TelegramUser.objects.create(telegram_id=300, username="jane")

        users = TelegramUser.objects.filter(username="john")
        assert users.count() == 2

    def test_get_users_ordered_by_registered_at(self):
        """Тест: сортировка пользователей по дате регистрации."""
        user1 = TelegramUser.objects.create(
            telegram_id=100,
            username="first"
        )
        user2 = TelegramUser.objects.create(
            telegram_id=200,
            username="second"
        )

        users = TelegramUser.objects.order_by("-registered_at")
        assert users[0].id == user2.id

    def test_delete_user(self):
        """Тест: удаление пользователя."""
        user = TelegramUser.objects.create(
            telegram_id=400,
            username="to_delete"
        )
        user_id = user.id

        user.delete()

        assert not TelegramUser.objects.filter(id=user_id).exists()


class TestUserIntegration(TestCase):
    """Интеграционные тесты для пользователей."""

    def test_full_user_lifecycle(self):
        """Тест: полный жизненный цикл пользователя."""
        # 1. Создание
        user = TelegramUser.objects.create(
            telegram_id=500,
            username="lifecycle_user",
            first_name="Lifecycle"
        )
        assert user.id is not None

        # 2. Проверка существования
        assert TelegramUser.objects.filter(telegram_id=500).exists()

        # 3. Обновление
        user.username = "updated_user"
        user.save()
        assert TelegramUser.objects.get(telegram_id=500).username == "updated_user"

        # 4. Удаление
        user.delete()
        assert not TelegramUser.objects.filter(telegram_id=500).exists()

    def test_user_with_all_counters(self):
        """Тест: пользователь со всеми счётчиками."""
        user = TelegramUser.objects.create(
            telegram_id=600,
            username="full_counters"
        )

        # Создаём события
        from events.models import Event
        for i in range(3):
            Event.objects.create(
                telegram_id=600,
                name=f"Event {i}",
                date="2026-12-01",
                time="10:00"
            )

        # Обновляем счётчики
        user.events_created = 3
        user.save()

        updated = TelegramUser.objects.get(telegram_id=600)
        assert updated.events_created == 3

    def test_multiple_users_different_telegram_ids(self):
        """Тест: несколько пользователей с разными telegram_id."""
        users = []
        for i in range(5):
            user = TelegramUser.objects.create(
                telegram_id=1000 + i,
                username=f"user_{i}"
            )
            users.append(user)

        assert TelegramUser.objects.count() == 5

        for user in users:
            assert TelegramUser.objects.filter(
                telegram_id=user.telegram_id
            ).exists()
