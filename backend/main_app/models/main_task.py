from django.db import models
from django.conf import settings

class MainTask(models.Model):
    """
    Main task in Todo App
    """
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="main_tasks",
    )
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    due_date = models.DateTimeField(blank=True, null=True)
    is_completed = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "main_task"
        verbose_name = "Main Task"
        verbose_name_plural = "Main Tasks"

    def __str__(self):
        return f'{self.title} with an id of {self.id} task for {self.user.first_name} {self.user.last_name}'