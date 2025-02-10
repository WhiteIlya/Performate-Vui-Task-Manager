from django.conf import settings
from django.db import models

from . import MainTask

class Notification(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="notifications",
    )
    main_task = models.ForeignKey(
        to=MainTask,
        on_delete=models.CASCADE,
        related_name="MainTask",
    )
    reminder_count = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)

    def __str__(self):
        return f"Notification for {self.user} for the task {self.main_task}"
