# Generated by Django 5.1.3 on 2025-02-20 09:34

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0003_user_ttm_stage'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='time_zone',
            field=models.CharField(blank=True, default='Europe/Berlin', help_text='Time zone of the user.', max_length=50, null=True),
        ),
    ]
