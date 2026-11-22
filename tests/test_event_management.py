"""
Тесты для управления событиями.
Проверяют CRUD-операции с событиями, публичность и экспорт.
"""
import pytest
from django.test import TestCase
from events.models import Event, TelegramUser


class TestEventCreation(TestCase):
    """Тесты создания событий."""

    def test_create_event(self):
        """Тест: создание события."""
        user = TelegramUser.objects.create(
            telegram_id=123456789,
            username="event_creator"
        )

        event = Event.objects.create(
            telegram_id=user.telegram_id,
            name="Test Event",
            date="2026-12-01",
            time="14:00:00",
            details="Test details"
        )

        assert event.id is not None
        assert event.name == "Test Event"
        assert str(event.date) == "2026-12-01"
        assert str(event.time) == "14:00:00"
        assert event.details == "Test details"
        assert event.is_public is False
        assert event.telegram_id == user.telegram_id

    def test_create_event_without_details(self):
        """Тест: создание события без описания."""
        user = TelegramUser.objects.create(
            telegram_id=222333444,
            username="no_details_user"
        )

        event = Event.objects.create(
            telegram_id=user.telegram_id,
            name="Event without details",
            date="2026-12-02",
            time="15:00:00"
        )

        assert event.details is None
        assert event.name == "Event without details"

    def test_create_event_with_public_status(self):
        """Тест: создание публичного события."""
        user = TelegramUser.objects.create(
            telegram_id=333444555,
            username="public_user"
        )

        event = Event.objects.create(
            telegram_id=user.telegram_id,
            name="Public Event",
            date="2026-12-03",
            time="16:00:00",
            is_public=True
        )

        assert event.is_public is True

    def test_create_event_with_minimal_data(self):
        """Тест: создание события с минимальными данными."""
        user = TelegramUser.objects.create(
            telegram_id=444555666,
            username="minimal_user"
        )

        event = Event.objects.create(
            telegram_id=user.telegram_id,
            name="Minimal",
            date="2026-12-04",
            time="17:00:00"
        )

        assert event.id is not None
        assert event.name == "Minimal"


class TestEventReading(TestCase):
    """Тесты чтения событий."""

    def test_read_event_by_id(self):
        """Тест: чтение события по ID."""
        user = TelegramUser.objects.create(
            telegram_id=555666777,
            username="reader"
        )

        event = Event.objects.create(
            telegram_id=user.telegram_id,
            name="Read Test",
            date="2026-12-05",
            time="18:00:00"
        )

        retrieved = Event.objects.get(id=event.id)
        assert retrieved.id == event.id
        assert retrieved.name == "Read Test"

    def test_read_event_not_found(self):
        """Тест: чтение несуществующего события."""
        with pytest.raises(Event.DoesNotExist):
            Event.objects.get(id=999999)

    def test_read_event_by_telegram_id(self):
        """Тест: чтение событий по telegram_id."""
        user = TelegramUser.objects.create(
            telegram_id=666777888,
            username="multi_events"
        )

        for i in range(3):
            Event.objects.create(
                telegram_id=user.telegram_id,
                name=f"Event {i}",
                date="2026-12-06",
                time=f"{10 + i}:00:00"
            )

        events = Event.objects.filter(telegram_id=user.telegram_id)
        assert events.count() == 3


class TestEventUpdate(TestCase):
    """Тесты обновления событий."""

    def test_update_event_name(self):
        """Тест: обновление названия события."""
        user = TelegramUser.objects.create(
            telegram_id=777888999,
            username="updater"
        )

        event = Event.objects.create(
            telegram_id=user.telegram_id,
            name="Old Name",
            date="2026-12-07",
            time="19:00:00"
        )

        event.name = "New Name"
        event.save()

        updated = Event.objects.get(id=event.id)
        assert updated.name == "New Name"

    def test_update_event_date(self):
        """Тест: обновление даты события."""
        user = TelegramUser.objects.create(
            telegram_id=888999000,
            username="date_updater"
        )

        event = Event.objects.create(
            telegram_id=user.telegram_id,
            name="Date Update",
            date="2026-12-08",
            time="20:00:00"
        )

        event.date = "2026-12-09"
        event.save()

        updated = Event.objects.get(id=event.id)
        assert str(updated.date) == "2026-12-09"

    def test_update_event_time(self):
        """Тест: обновление времени события."""
        user = TelegramUser.objects.create(
            telegram_id=999000111,
            username="time_updater"
        )

        event = Event.objects.create(
            telegram_id=user.telegram_id,
            name="Time Update",
            date="2026-12-10",
            time="21:00:00"
        )

        event.time = "22:00:00"
        event.save()

        updated = Event.objects.get(id=event.id)
        assert updated.time.strftime("%H:%M:%S") == "22:00:00"

    def test_update_event_details(self):
        """Тест: обновление описания события."""
        user = TelegramUser.objects.create(
            telegram_id=111222333,
            username="details_updater"
        )

        event = Event.objects.create(
            telegram_id=user.telegram_id,
            name="Details Update",
            date="2026-12-11",
            time="23:00:00",
            details="Old details"
        )

        event.details = "New details"
        event.save()

        updated = Event.objects.get(id=event.id)
        assert updated.details == "New details"

    def test_update_event_multiple_fields(self):
        """Тест: обновление нескольких полей события."""
        user = TelegramUser.objects.create(
            telegram_id=222333444,
            username="multi_updater"
        )

        event = Event.objects.create(
            telegram_id=user.telegram_id,
            name="Multi Update",
            date="2026-12-12",
            time="10:00:00",
            details="Old details"
        )

        event.name = "Updated Name"
        event.date = "2026-12-13"
        event.time = "11:00:00"
        event.details = "Updated details"
        event.save()

        updated = Event.objects.get(id=event.id)
        assert updated.name == "Updated Name"
        assert str(updated.date) == "2026-12-13"
        assert str(updated.time) == "11:00:00"
        assert updated.details == "Updated details"


class TestEventDeletion(TestCase):
    """Тесты удаления событий."""

    def test_delete_event(self):
        """Тест: удаление события."""
        user = TelegramUser.objects.create(
            telegram_id=333444555,
            username="deleter"
        )

        event = Event.objects.create(
            telegram_id=user.telegram_id,
            name="To Delete",
            date="2026-12-14",
            time="12:00:00"
        )
        event_id = event.id

        event.delete()

        assert not Event.objects.filter(id=event_id).exists()

    def test_delete_event_not_found(self):
        """Тест: удаление несуществующего события."""
        with pytest.raises(Event.DoesNotExist):
            Event.objects.get(id=999999).delete()

    def test_delete_all_user_events(self):
        """Тест: удаление всех событий пользователя."""
        user = TelegramUser.objects.create(
            telegram_id=444555666,
            username="all_deleted"
        )

        for i in range(3):
            Event.objects.create(
                telegram_id=user.telegram_id,
                name=f"Event {i}",
                date="2026-12-15",
                time=f"{10 + i}:00:00"
            )

        Event.objects.filter(telegram_id=user.telegram_id).delete()

        assert Event.objects.filter(telegram_id=user.telegram_id).count() == 0


class TestEventPublic(TestCase):
    """Тесты публичных событий."""

    def test_toggle_event_public(self):
        """Тест: переключение публичности события."""
        user = TelegramUser.objects.create(
            telegram_id=555666777,
            username="public_toggler"
        )

        event = Event.objects.create(
            telegram_id=user.telegram_id,
            name="Public Toggle",
            date="2026-12-16",
            time="14:00:00",
            is_public=False
        )

        event.is_public = True
        event.save()

        assert Event.objects.get(id=event.id).is_public is True

    def test_get_public_events(self):
        """Тест: получение публичных событий."""
        user1 = TelegramUser.objects.create(
            telegram_id=666777888,
            username="public_user1"
        )
        user2 = TelegramUser.objects.create(
            telegram_id=777888999,
            username="public_user2"
        )

        # Публичное событие
        Event.objects.create(
            telegram_id=user1.telegram_id,
            name="Public Event",
            date="2026-12-17",
            time="15:00:00",
            is_public=True
        )

        # Приватное событие
        Event.objects.create(
            telegram_id=user2.telegram_id,
            name="Private Event",
            date="2026-12-17",
            time="16:00:00",
            is_public=False
        )

        public_events = Event.objects.filter(is_public=True)
        assert public_events.count() == 1
        assert public_events[0].name == "Public Event"

    def test_get_public_events_for_user(self):
        """Тест: получение публичных событий другого пользователя."""
        user1 = TelegramUser.objects.create(
            telegram_id=888999000,
            username="owner"
        )
        user2 = TelegramUser.objects.create(
            telegram_id=999000111,
            username="viewer"
        )

        Event.objects.create(
            telegram_id=user1.telegram_id,
            name="Shared Event",
            date="2026-12-18",
            time="17:00:00",
            is_public=True
        )

        from django.db.models import Q
        events = Event.objects.filter(
            is_public=True,
            telegram_id__lt=user2.telegram_id
        )
        assert events.count() == 1


class TestEventQueries(TestCase):
    """��есты запросов к событиям."""

    def test_get_all_events_for_user(self):
        """Тест: получение всех событий пользователя."""
        user = TelegramUser.objects.create(
            telegram_id=111222333,
            username="multi_events_user"
        )

        for i in range(5):
            Event.objects.create(
                telegram_id=user.telegram_id,
                name=f"Event {i}",
                date="2026-12-19",
                time=f"{10 + i}:00:00"
            )

        events = Event.objects.filter(telegram_id=user.telegram_id)
        assert events.count() == 5

    def test_get_events_by_date(self):
        """Тест: получение событий по дате."""
        user = TelegramUser.objects.create(
            telegram_id=222333444,
            username="date_query_user"
        )

        Event.objects.create(
            telegram_id=user.telegram_id,
            name="Event 1",
            date="2026-12-20",
            time="10:00:00"
        )
        Event.objects.create(
            telegram_id=user.telegram_id,
            name="Event 2",
            date="2026-12-20",
            time="11:00:00"
        )
        Event.objects.create(
            telegram_id=user.telegram_id,
            name="Event 3",
            date="2026-12-21",
            time="12:00:00"
        )

        events = Event.objects.filter(
            telegram_id=user.telegram_id,
            date="2026-12-20"
        )
        assert events.count() == 2

    def test_get_events_ordered_by_date_and_time(self):
        """Тест: сортировка событий по дате и времени."""
        user = TelegramUser.objects.create(
            telegram_id=333444555,
            username="ordered_user"
        )

        Event.objects.create(
            telegram_id=user.telegram_id,
            name="Later",
            date="2026-12-22",
            time="15:00:00"
        )
        Event.objects.create(
            telegram_id=user.telegram_id,
            name="Earlier",
            date="2026-12-21",
            time="10:00:00"
        )

        events = Event.objects.filter(
            telegram_id=user.telegram_id
        ).order_by("date", "time")

        assert events[0].name == "Earlier"
        assert events[1].name == "Later"

    def test_get_events_with_limit(self):
        """Тест: получение событий с ограничением."""
        user = TelegramUser.objects.create(
            telegram_id=444555666,
            username="limited_user"
        )

        for i in range(10):
            Event.objects.create(
                telegram_id=user.telegram_id,
                name=f"Event {i}",
                date="2026-12-23",
                time="10:00:00"
            )

        events = Event.objects.filter(
            telegram_id=user.telegram_id
        )[:5]

        assert events.count() == 5


class TestEventIntegration(TestCase):
    """Интеграционные тесты для событий."""

    def test_full_event_lifecycle(self):
        """Тест: полный жизненный цикл события."""
        user = TelegramUser.objects.create(
            telegram_id=555666777,
            username="lifecycle_user"
        )

        # 1. Создание
        event = Event.objects.create(
            telegram_id=user.telegram_id,
            name="Lifecycle Event",
            date="2026-12-24",
            time="12:00:00",
            details="Test"
        )
        assert event.id is not None

        # 2. Чтение
        retrieved = Event.objects.get(id=event.id)
        assert retrieved.name == "Lifecycle Event"

        # 3. Обновление
        event.name = "Updated Lifecycle Event"
        event.save()
        assert Event.objects.get(id=event.id).name == "Updated Lifecycle Event"

        # 4. Удаление
        event.delete()
        assert not Event.objects.filter(id=event.id).exists()

    def test_event_with_user_counters(self):
        """Тест: события и счётчики пользователя."""
        user = TelegramUser.objects.create(
            telegram_id=666777888,
            username="counter_user"
        )

        # Создаём события
        for i in range(3):
            Event.objects.create(
                telegram_id=user.telegram_id,
                name=f"Event {i}",
                date="2026-12-25",
                time="10:00:00"
            )

        # Обновляем счётчик
        user.events_created = 3
        user.save()

        updated_user = TelegramUser.objects.get(telegram_id=666777888)
        assert updated_user.events_created == 3

    def test_multiple_events_same_date(self):
        """Тест: несколько событий в один день."""
        user = TelegramUser.objects.create(
            telegram_id=777888999,
            username="same_day_user"
        )

        for i in range(5):
            Event.objects.create(
                telegram_id=user.telegram_id,
                name=f"Event {i}",
                date="2026-12-26",
                time=f"{10 + i}:00:00"
            )

        events = Event.objects.filter(
            telegram_id=user.telegram_id,
            date="2026-12-26"
        )
        assert events.count() == 5

    def test_event_owner_verification(self):
        """Тест: проверка владельца события."""
        user1 = TelegramUser.objects.create(
            telegram_id=888999000,
            username="owner1"
        )
        user2 = TelegramUser.objects.create(
            telegram_id=999000111,
            username="owner2"
        )

        event = Event.objects.create(
            telegram_id=user1.telegram_id,
            name="Owner Test",
            date="2026-12-27",
            time="14:00:00"
        )

        # Проверка: событие принадлежит user1
        assert Event.objects.filter(
            id=event.id,
            telegram_id=user1.telegram_id
        ).exists()

        # Проверка: событие не принадлежит user2
        assert not Event.objects.filter(
            id=event.id,
            telegram_id=user2.telegram_id
        ).exists()
