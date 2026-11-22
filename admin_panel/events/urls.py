
from django.urls import path, include
from . import views
from rest_framework import routers
from .api_views import EventViewSet, TelegramUserViewSet, MeetingViewSet, BotStatisticsViewSet

router = routers.DefaultRouter()
router.register(r'api/events', EventViewSet)
router.register(r'api/users', TelegramUserViewSet)
router.register(r'api/meetings', MeetingViewSet)
router.register(r'api/statistics', BotStatisticsViewSet)

urlpatterns = [
    path('export/', views.export_events, name='export_events'),
]

urlpatterns += router.urls
