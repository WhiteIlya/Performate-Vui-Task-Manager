from rest_framework import serializers

from ..models import MainTask

class MainTaskSerializer(serializers.ModelSerializer):
    class Meta:
        model = MainTask
        fields = ['id', 'title', 'created_at', 'description', 'due_date', 'is_completed']
