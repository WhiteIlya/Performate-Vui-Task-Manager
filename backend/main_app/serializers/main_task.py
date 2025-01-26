from rest_framework import serializers

from .subtask import SubTaskSerializer

from ..models import MainTask

class MainTaskSerializer(serializers.ModelSerializer):
    subtasks = SubTaskSerializer(many=True, read_only=True)

    class Meta:
        model = MainTask
        fields = ['id', 'title', 'created_at', 'description', 'due_date', 'is_completed', 'subtasks']
