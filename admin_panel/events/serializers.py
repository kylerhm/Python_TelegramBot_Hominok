from rest_framework import serializers
from .models import Event, TelegramUser, Meeting, BotStatistics


class EventSerializer(serializers.ModelSerializer):
    class Meta:
        model = Event
        fields = '__all__'


class TelegramUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = TelegramUser
        fields = '__all__'


class MeetingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Meeting
        fields = '__all__'


class BotStatisticsSerializer(serializers.ModelSerializer):
    class Meta:
        model = BotStatistics
        fields = '__all__'
        read_only_fields = ('date',)
