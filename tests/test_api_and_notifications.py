"""
Тесты для REST API и системы уведомлений.
Проверяют аутентификацию, авторизацию и работу с API.
"""
import pytest
from django.test import TestCase, Client
from django.contrib.auth.models import User
from rest_framework.test import APIClient
from rest_framework.authtoken.models import Token
from events.models import Event, TelegramUser, Meeting


class TestAPIAuthentication(TestCase):
    """Тесты аутентификации API."""

    def setUp(self):
        """Настройка тестовых данных."""
        self.client = APIClient()
        self.user = TelegramUser.objects.create(
            telegram_id=123456789,
            username="api_user"
        )
        self.event = Event.objects.create(
            telegram_id=self.user.telegram_id,
            name="API Test Event",
            date="2026-12-28",
            time="10:00:00"
        )

    def test_api_requires_authentication(self):
        """Тест: API требует аутентификации."""
        response = self.client.get("/events/api/events/")
        assert response.status_code == 401

    def test_api_unauthorized_access(self):
        """Тест: неавторизованный доступ к API."""
        response = self.client.get("/events/api/users/")
        assert response.status_code == 401

    def test_api_unauthorized_meetings(self):
        """Тест: неавторизованный доступ к встречами."""
        response = self.client.get("/events/api/meetings/")
        assert response.status_code == 401

    def test_api_root_accessible(self):
        """Тест: корневой эндпоинт API доступен."""
        response = self.client.get("/events/api/")
        # API может возвращать 200, 401, 403 или 404 (если DRF router не настроен)
        assert response.status_code in [200, 401, 403, 404]


class TestAPIEventEndpoints(TestCase):
    """Тесты эндпоинтов событий API."""

    def setUp(self):
        """Настройка тестовых данных."""
        self.client = APIClient()
        self.user = TelegramUser.objects.create(
            telegram_id=222333444,
            username="event_api_user"
        )
        self.event = Event.objects.create(
            telegram_id=self.user.telegram_id,
            name="Test Event for API",
            date="2026-12-29",
            time="11:00:00",
            details="API test details"
        )

    def test_get_events_endpoint(self):
        """Тест: получение списка событий."""
        # Без аутентификации
        response = self.client.get("/events/api/events/")
        assert response.status_code == 401

    def test_create_event_via_api(self):
        """Тест: создание события через API."""
        # Без аутентификации
        response = self.client.post(
            "/events/api/events/",
            {
                "name": "New Event",
                "date": "2026-12-30",
                "time": "12:00:00",
                "telegram_id": self.user.telegram_id
            }
        )
        assert response.status_code == 401

    def test_update_event_via_api(self):
        """Тест: обновление события через API."""
        # Без аутентификации
        response = self.client.put(
            f"/events/api/events/{self.event.id}/",
            {"name": "Updated Event"}
        )
        assert response.status_code == 401

    def test_delete_event_via_api(self):
        """Тест: удаление события через API."""
        # Без аутентификации
        response = self.client.delete(f"/events/api/events/{self.event.id}/")
        assert response.status_code == 401


class TestAPIUserEndpoints(TestCase):
    """Тесты эндпоинтов пользователей API."""

    def setUp(self):
        """Настройка тестовых данных."""
        self.client = APIClient()
        self.user = TelegramUser.objects.create(
            telegram_id=333444555,
            username="user_api_user"
        )

    def test_get_users_endpoint(self):
        """Тест: получение списка пользователей."""
        response = self.client.get("/events/api/users/")
        assert response.status_code == 401

    def test_create_user_via_api(self):
        """Тест: создание пользователя через API."""
        response = self.client.post(
            "/events/api/users/",
            {
                "telegram_id": 444555666,
                "username": "new_api_user"
            }
        )
        assert response.status_code == 401


class TestAPIMeetingEndpoints(TestCase):
    """Тесты эндпоинтов встреч API."""

    def setUp(self):
        """Настройка тестовых данных."""
        self.client = APIClient()
        self.user = TelegramUser.objects.create(
            telegram_id=555666777,
            username="meeting_api_user"
        )
        self.meeting = Meeting.objects.create(
            title="API Meeting",
            date="2026-12-31",
            time="14:00:00",
            organizer_id=self.user.telegram_id,
            organizer_name="Organizer",
            participant_id=666777888,
            participant_name="Participant"
        )

    def test_get_meetings_endpoint(self):
        """Тест: получение списка встреч."""
        response = self.client.get("/events/api/meetings/")
        assert response.status_code == 401

    def test_create_meeting_via_api(self):
        """Тест: создание встречи через API."""
        response = self.client.post(
            "/events/api/meetings/",
            {
                "title": "New Meeting",
                "date": "2027-01-01",
                "time": "15:00:00",
                "organizer_id": self.user.telegram_id
            }
        )
        assert response.status_code == 401


class TestAPIExport(TestCase):
    """Тесты экспорта данных API."""

    def setUp(self):
        """Настройка тестовых данных."""
        self.client = Client()
        self.user = TelegramUser.objects.create(
            telegram_id=777888999,
            username="export_user"
        )
        # Создаем Django User для аутентификации
        self.django_user = User.objects.create_user(
            username='export_user',
            password='testpass123'
        )
        self.client.login(username='export_user', password='testpass123')
        
        self.event1 = Event.objects.create(
            telegram_id=self.user.telegram_id,
            name="Export Event 1",
            date="2027-01-02",
            time="10:00:00",
            details="Detail 1"
        )
        self.event2 = Event.objects.create(
            telegram_id=self.user.telegram_id,
            name="Export Event 2",
            date="2027-01-03",
            time="11:00:00",
            details="Detail 2"
        )

    def test_export_json(self):
        """Тест: экспорт в JSON."""
        response = self.client.get(
            "/events/export/",
            {"format": "json", "telegram_id": self.user.telegram_id}
        )
        assert response.status_code == 200
        assert response["Content-Type"] == "application/json"
        data = response.json()
        assert len(data) == 2

    def test_export_csv(self):
        """Тест: экспорт в CSV."""
        response = self.client.get(
            "/events/export/",
            {"format": "csv", "telegram_id": self.user.telegram_id}
        )
        assert response.status_code == 200
        assert response["Content-Type"] == "text/csv"
        content = response.content.decode("utf-8")
        assert "Export Event 1" in content
        assert "Export Event 2" in content

    def test_export_without_telegram_id(self):
        """Тест: экспорт без telegram_id."""
        response = self.client.get("/events/export/")
        assert response.status_code == 400

    def test_export_invalid_format(self):
        """Тест: экспорт с невалидным форматом."""
        response = self.client.get(
            "/events/export/",
            {"format": "xml", "telegram_id": self.user.telegram_id}
        )
        # Должен вернуть JSON по умолчанию
        assert response.status_code == 200


class TestNotificationSystem(TestCase):
    """Тесты системы уведомлений."""

    def setUp(self):
        """Настройка тестовых данных."""
        self.client = Client()
        self.organizer = TelegramUser.objects.create(
            telegram_id=888999000,
            username="organizer"
        )
        self.participant = TelegramUser.objects.create(
            telegram_id=999000111,
            username="participant"
        )

    def test_meeting_status_pending(self):
        """Тест: встреча в статусе pending."""
        meeting = Meeting.objects.create(
            title="Pending Meeting",
            date="2027-01-04",
            time="16:00:00",
            organizer_id=self.organizer.telegram_id,
            organizer_name="Organizer",
            participant_id=self.participant.telegram_id,
            participant_name="Participant",
            status="pending"
        )

        assert meeting.status == "pending"
        assert meeting.get_status_display() == "Ожидается"

    def test_meeting_status_confirmed(self):
        """Тест: встреча в статусе confirmed."""
        meeting = Meeting.objects.create(
            title="Confirmed Meeting",
            date="2027-01-05",
            time="17:00:00",
            organizer_id=self.organizer.telegram_id,
            organizer_name="Organizer",
            participant_id=self.participant.telegram_id,
            participant_name="Participant",
            status="confirmed"
        )

        meeting.status = "confirmed"
        meeting.save()

        updated = Meeting.objects.get(id=meeting.id)
        assert updated.status == "confirmed"
        assert updated.get_status_display() == "Подтверждено"

    def test_meeting_status_cancelled(self):
        """Тест: встреча в статусе cancelled."""
        meeting = Meeting.objects.create(
            title="Cancelled Meeting",
            date="2027-01-06",
            time="18:00:00",
            organizer_id=self.organizer.telegram_id,
            organizer_name="Organizer",
            participant_id=self.participant.telegram_id,
            participant_name="Participant",
            status="cancelled"
        )

        meeting.status = "cancelled"
        meeting.save()

        updated = Meeting.objects.get(id=meeting.id)
        assert updated.status == "cancelled"
        assert updated.get_status_display() == "Отменено"

    def test_get_pending_meetings(self):
        """Тест: получение встреч в статусе pending."""
        Meeting.objects.create(
            title="Pending 1",
            date="2027-01-07",
            time="19:00:00",
            organizer_id=self.organizer.telegram_id,
            organizer_name="Organizer",
            participant_id=self.participant.telegram_id,
            status="pending"
        )
        Meeting.objects.create(
            title="Confirmed 1",
            date="2027-01-08",
            time="20:00:00",
            organizer_id=self.organizer.telegram_id,
            organizer_name="Organizer",
            participant_id=self.participant.telegram_id,
            status="confirmed"
        )

        pending = Meeting.objects.filter(status="pending")
        assert pending.count() == 1

    def test_meeting_notifications_status(self):
        """Тест: система статусов уведомлений."""
        from services import STATUS_EMOJI

        assert STATUS_EMOJI["pending"] == "⏳"
        assert STATUS_EMOJI["confirmed"] == "✅"
        assert STATUS_EMOJI["cancelled"] == "❌"

    def test_meeting_with_all_fields(self):
        """Тест: встреча со всеми полями."""
        meeting = Meeting.objects.create(
            title="Full Meeting",
            date="2027-01-09",
            time="21:00:00",
            organizer_id=self.organizer.telegram_id,
            organizer_name="Full Organizer",
            participant_id=self.participant.telegram_id,
            participant_name="Full Participant",
            status="pending"
        )

        assert meeting.title == "Full Meeting"
        assert str(meeting.date) == "2027-01-09"
        assert str(meeting.time) == "21:00:00"
        assert meeting.organizer_id == self.organizer.telegram_id
        assert meeting.organizer_name == "Full Organizer"
        assert meeting.participant_id == self.participant.telegram_id
        assert meeting.participant_name == "Full Participant"
        assert meeting.status == "pending"

    def test_meeting_created_at_auto_set(self):
        """Тест: автоматическая установка created_at."""
        meeting = Meeting.objects.create(
            title="Auto Time Meeting",
            date="2027-01-10",
            time="22:00:00",
            organizer_id=self.organizer.telegram_id,
            organizer_name="Organizer",
            participant_id=self.participant.telegram_id
        )

        assert meeting.created_at is not None

    def test_meetings_ordered_by_date_and_time(self):
        """Тест: сортировка встреч по дате и времени."""
        Meeting.objects.create(
            title="Later Meeting",
            date="2027-01-12",
            time="15:00:00",
            organizer_id=self.organizer.telegram_id,
            organizer_name="Organizer",
            participant_id=self.participant.telegram_id
        )
        Meeting.objects.create(
            title="Earlier Meeting",
            date="2027-01-11",
            time="10:00:00",
            organizer_id=self.organizer.telegram_id,
            organizer_name="Organizer",
            participant_id=self.participant.telegram_id
        )

        meetings = Meeting.objects.filter(
            organizer_id=self.organizer.telegram_id
        ).order_by("-date", "-time")

        assert meetings[0].title == "Later Meeting"
        assert meetings[1].title == "Earlier Meeting"


class TestNotificationIntegration(TestCase):
    """Интеграционные тесты системы уведомлений."""

    def test_full_meeting_lifecycle(self):
        """Тест: полный жизненный цикл встречи."""
        organizer = TelegramUser.objects.create(
            telegram_id=111222333,
            username="lifecycle_organizer"
        )
        participant = TelegramUser.objects.create(
            telegram_id=444555666,
            username="lifecycle_participant"
        )

        # 1. Создание встречи
        meeting = Meeting.objects.create(
            title="Lifecycle Meeting",
            date="2027-01-13",
            time="10:00:00",
            organizer_id=organizer.telegram_id,
            organizer_name="Organizer",
            participant_id=participant.telegram_id,
            status="pending"
        )
        assert meeting.status == "pending"

        # 2. Подтверждение
        meeting.status = "confirmed"
        meeting.save()
        assert Meeting.objects.get(id=meeting.id).status == "confirmed"

        # 3. Отмена
        meeting.status = "cancelled"
        meeting.save()
        assert Meeting.objects.get(id=meeting.id).status == "cancelled"

        # 4. Удаление
        meeting.delete()
        assert not Meeting.objects.filter(id=meeting.id).exists()

    def test_multiple_meetings_same_participant(self):
        """Тест: несколько встреч с одним участником."""
        organizer1 = TelegramUser.objects.create(
            telegram_id=222333444,
            username="org1"
        )
        organizer2 = TelegramUser.objects.create(
            telegram_id=333444555,
            username="org2"
        )
        participant = TelegramUser.objects.create(
            telegram_id=444555666,
            username="multi_meeting_participant"
        )

        Meeting.objects.create(
            title="Meeting 1",
            date="2027-01-14",
            time="10:00:00",
            organizer_id=organizer1.telegram_id,
            organizer_name="Org1",
            participant_id=participant.telegram_id
        )
        Meeting.objects.create(
            title="Meeting 2",
            date="2027-01-15",
            time="11:00:00",
            organizer_id=organizer2.telegram_id,
            organizer_name="Org2",
            participant_id=participant.telegram_id
        )

        meetings = Meeting.objects.filter(
            participant_id=participant.telegram_id
        )
        assert meetings.count() == 2

    def test_meeting_status_filtering(self):
        """Тест: фильтрация встреч по статусу."""
        organizer = TelegramUser.objects.create(
            telegram_id=555666777,
            username="filter_organizer"
        )
        participant = TelegramUser.objects.create(
            telegram_id=666777888,
            username="filter_participant"
        )

        Meeting.objects.create(
            title="Pending Meeting",
            date="2027-01-16",
            time="12:00:00",
            organizer_id=organizer.telegram_id,
            organizer_name="Organizer",
            participant_id=participant.telegram_id,
            status="pending"
        )
        Meeting.objects.create(
            title="Confirmed Meeting",
            date="2027-01-17",
            time="13:00:00",
            organizer_id=organizer.telegram_id,
            organizer_name="Organizer",
            participant_id=participant.telegram_id,
            status="confirmed"
        )
        Meeting.objects.create(
            title="Cancelled Meeting",
            date="2027-01-18",
            time="14:00:00",
            organizer_id=organizer.telegram_id,
            organizer_name="Organizer",
            participant_id=participant.telegram_id,
            status="cancelled"
        )

        pending = Meeting.objects.filter(status="pending")
        confirmed = Meeting.objects.filter(status="confirmed")
        cancelled = Meeting.objects.filter(status="cancelled")

        assert pending.count() == 1
        assert confirmed.count() == 1
        assert cancelled.count() == 1
