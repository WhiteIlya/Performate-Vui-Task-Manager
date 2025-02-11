from rest_framework import serializers
from ..models import Notification

class NotificationSerializer(serializers.ModelSerializer):
    task_title = serializers.CharField(source="main_task.title", read_only=True)

    class Meta:
        model = Notification
        fields = ["id", "task_title", "created_at", "is_read"]
