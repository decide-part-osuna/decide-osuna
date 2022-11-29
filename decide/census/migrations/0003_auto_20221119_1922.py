# Generated by Django 2.0 on 2022-11-19 19:22

from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('census', '0002_auto_20221119_1916'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='census',
            name='voter_id',
        ),
        migrations.AddField(
            model_name='census',
            name='voter_id',
            field=models.ManyToManyField(to=settings.AUTH_USER_MODEL),
        ),
    ]