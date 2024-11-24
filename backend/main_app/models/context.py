from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()

class Context(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='context')
    context = models.JSONField(default=dict)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self) -> str:
        return f"Context for {self.user.username}"

    def get_recent_context(self, limit=10) -> list:
        context = self.context.get('context', [])
        return context[-limit:] if len(context) > limit else context
    
    def add_context(self, content: list):
        self.context['context'] = content
        self.save()

    def clear_context(self):
        self.context['context'] = []
        self.save()