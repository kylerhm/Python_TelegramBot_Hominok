from rest_framework import viewsets, permissions
from rest_framework.permissions import IsAuthenticated
from .models import Event, TelegramUser, Meeting, BotStatistics
from .serializers import EventSerializer, TelegramUserSerializer, MeetingSerializer, BotStatisticsSerializer


class IsOwnerOrReadOnly(permissions.BasePermission):
    """Разрешение только владельцу объекта."""
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        if hasattr(obj, 'telegram_id'):
            return obj.telegram_id == request.user.telegram_id
        if hasattr(obj, 'organizer_id'):
            return obj.organizer_id == request.user.telegram_id
        return False


class EventViewSet(viewsets.ModelViewSet):
    queryset = Event.objects.all()
    serializer_class = EventSerializer
    permission_classes = [IsAuthenticated, IsOwnerOrReadOnly]

    def get_queryset(self):
        return Event.objects.filter(telegram_id=self.request.user.telegram_id)


class TelegramUserViewSet(viewsets.ModelViewSet):
    queryset = TelegramUser.objects.all()
    serializer_class = TelegramUserSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return TelegramUser.objects.filter(telegram_id=self.request.user.telegram_id)


class MeetingViewSet(viewsets.ModelViewSet):
    queryset = Meeting.objects.all()
    serializer_class = MeetingSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user_id = self.request.user.telegram_id
        return Meeting.objects.filter(
            participant_id=user_id
        ) | Meeting.objects.filter(
            organizer_id=user_id
        )


class BotStatisticsViewSet(viewsets.ModelViewSet):
    """API ViewSet для статистики бота.
    
    Статистика является глобальной и доступна всем аутентифицированным пользователям.
    """
    queryset = BotStatistics.objects.all()
    serializer_class = BotStatisticsSerializer
    permission_classes = [IsAuthenticated]
