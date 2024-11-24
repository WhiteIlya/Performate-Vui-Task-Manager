from rest_framework import serializers
from ..models.context import Context

class ContextSerializer(serializers.ModelSerializer):
    class Meta:
        model = Context
        fields = '__all__'