# Generated by Django 5.1.3 on 2025-01-15 16:20

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='assistant_id',
            field=models.CharField(blank=True, help_text='Unique Assistant ID from OpenAI for the user.', max_length=100, null=True),
        ),
        migrations.AddField(
            model_name='user',
            name='thread_id',
            field=models.CharField(blank=True, help_text='Unique Thread ID from OpenAI for the user.', max_length=100, null=True),
        ),
    ]
