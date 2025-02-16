from rest_framework import serializers
from ..models import VoiceConfig

class VoiceConfigSerializer(serializers.ModelSerializer):
    class Meta:
        model = VoiceConfig
        fields = [
            "voice_id",
            "voice_name",
            "accent",
            "gender",
            "age",
            "description",
            "use_case",
            "stability",
            "similarity_boost",
            "style",
            "use_speaker_boost",
            "persona_tone",
            "persona_traits",
            "interaction_style",
            "formality_level",
            "response_length",
            "paraphrase_variability",
            "personalized_naming",
            "emotional_expressiveness",
            "reminder_frequency",
            "preferred_reminder_time",
            "reminder_tone",
            "voice_feedback_style",
            "other_preferences",
            "progress_reporting",
        ]

    def validate_stability(self, value):
        if not 0.0 <= value <= 1.0:
            raise serializers.ValidationError("Stability must be between 0.0 and 1.0")
        return value

    def validate_similarity_boost(self, value):
        if not 0.0 <= value <= 1.0:
            raise serializers.ValidationError("Similarity Boost must be between 0.0 and 1.0")
        return value

    def validate_style(self, value):
        if not 0.0 <= value <= 1.0:
            raise serializers.ValidationError("Style must be between 0.0 and 1.0")
        return value
