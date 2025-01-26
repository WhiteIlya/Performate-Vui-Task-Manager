from rest_framework import serializers

from ..models import Subtask

class SubTaskSerializer(serializers.ModelSerializer):
    class Meta:
        model = Subtask
        fields = ['id', 'title', 'is_completed', 'due_date']
