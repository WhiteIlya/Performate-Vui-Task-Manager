from rest_framework import serializers

class AssistantRequestSerializer(serializers.Serializer):
    message = serializers.CharField(required=True)