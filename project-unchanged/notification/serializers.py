from rest_framework import serializers
from .models import Notification

class CreateNotification(serializers.ModelSerializer):
    class Meta:
        model = Notification

class NotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notification
        fields = '__all__'