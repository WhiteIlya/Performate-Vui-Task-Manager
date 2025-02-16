from django.conf import settings
from django.db import models

class VoiceConfig(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="voice_config"
    )
    voice_id = models.CharField(max_length=50)
    voice_name = models.CharField(max_length=100)
    accent = models.CharField(max_length=50, blank=True, null=True)
    gender = models.CharField(max_length=10, blank=True, null=True)
    age = models.CharField(max_length=20, blank=True, null=True)
    description = models.CharField(max_length=100, blank=True, null=True)
    use_case = models.CharField(max_length=20, blank=True, null=True)

    stability = models.FloatField(default=0.5)
    similarity_boost = models.FloatField(default=0.8)
    style = models.FloatField(default=0.0)
    use_speaker_boost = models.BooleanField(default=True)

    persona_tone = models.CharField(max_length=50, blank=True, null=True)
    interaction_style = models.CharField(max_length=50, blank=True, null=True)
    formality_level = models.CharField(max_length=50, blank=True, null=True)
    response_length = models.CharField(max_length=50, blank=True, null=True)
    paraphrase_variability = models.CharField(max_length=50, blank=True, null=True)
    personalized_naming = models.CharField(max_length=50, blank=True, null=True)
    emotional_expressiveness = models.CharField(max_length=50, blank=True, null=True)
    reminder_frequency = models.CharField(max_length=50, blank=True, null=True)
    preferred_reminder_time = models.CharField(max_length=50, blank=True, null=True)
    reminder_tone = models.CharField(max_length=50, blank=True, null=True)
    voice_feedback_style = models.CharField(max_length=50, blank=True, null=True)
    other_preferences = models.CharField(max_length=250, blank=True, null=True)
    progress_reporting = models.CharField(max_length=50, blank=True, null=True)
    persona_traits = models.CharField(max_length=50, blank=True, null=True)



    def __str__(self):
        return f"{self.user.full_name} has eleven labs voice config: {self.voice_id} - {self.voice_name}"
