from django.db import models

from . import MainTask

class Subtask(models.Model):
    """
    Subtasks of MainTask
    """
    main_task = models.ForeignKey(
        to=MainTask,
        on_delete=models.CASCADE,
        related_name="subtasks",
    )
    title = models.CharField(max_length=255)
    is_completed = models.BooleanField(default=False)
    due_date = models.DateTimeField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "subtask"
        verbose_name = "Sub Task"
        verbose_name_plural = "Sub Tasks"

    def __str__(self):
        return self.title
