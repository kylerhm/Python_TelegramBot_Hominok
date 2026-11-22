"""
Модели и работа с БД: класс Calendar для CRUD-операций с событиями.
Использует Django ORM для надёжности.
"""
from events.models import Event


class Calendar:
    """Класс для работы с событиями через Django ORM."""

    def __init__(self, *args, **kwargs):
        """Инициализация — ORM уже настроена в config.py."""
        pass

    def create_event(self, telegram_id, event_name, event_date, event_time, event_details):
        """Создание нового события."""
        event = Event.objects.create(
            telegram_id=telegram_id,
            name=event_name,
            date=event_date,
            time=event_time,
            details=event_details or "",
            is_public=False
        )
        return event.id

    def read_event(self, telegram_id, event_id):
        """Получение события по ID."""
        try:
            event = Event.objects.get(id=event_id, telegram_id=telegram_id)
            return {
                "id": event.id,
                "name": event.name,
                "date": event.date,
                "time": event.time,
                "details": event.details,
                "is_public": event.is_public,
            }
        except Event.DoesNotExist:
            return None

    def edit_event(self, telegram_id, event_id, event_name=None, event_date=None,
                   event_time=None, event_details=None):
        """Редактирование события."""
        try:
            event = Event.objects.get(id=event_id, telegram_id=telegram_id)
            if event_name is not None:
                event.name = event_name
            if event_date is not None:
                event.date = event_date
            if event_time is not None:
                event.time = event_time
            if event_details is not None:
                event.details = event_details
            event.save()
            return True
        except Event.DoesNotExist:
            return False

    def delete_event(self, telegram_id, event_id):
        """Удаление события."""
        try:
            event = Event.objects.get(id=event_id, telegram_id=telegram_id)
            event.delete()
            return True
        except Event.DoesNotExist:
            return False

    def reset_id_sequence(self):
        """Сброс последовательности ID при удалении всех событий."""
        from django.db import connection
        with connection.cursor() as cursor:
            cursor.execute("ALTER SEQUENCE events_id_seq RESTART WITH 1;")

    def get_all_events(self, telegram_id):
        """Получение всех событий пользователя."""
        events = Event.objects.filter(
            telegram_id=telegram_id
        ).order_by('date', 'time')
        return [
            {"id": e.id, "name": e.name, "date": e.date, "time": e.time}
            for e in events
        ]

    def toggle_public(self, telegram_id, event_id):
        """Переключение публичности события."""
        try:
            event = Event.objects.get(id=event_id, telegram_id=telegram_id)
            event.is_public = not event.is_public
            event.save()
            return event.is_public
        except Event.DoesNotExist:
            return None

    def get_public_events(self, telegram_id, limit=20):
        """Получение публичных событий других пользователей."""
        events = Event.objects.filter(
            is_public=True
        ).exclude(
            telegram_id=telegram_id
        ).order_by('date', 'time')[:limit]
        return [
            {"id": e.id, "name": e.name, "date": e.date,
             "time": e.time, "owner_id": e.telegram_id}
            for e in events
        ]
