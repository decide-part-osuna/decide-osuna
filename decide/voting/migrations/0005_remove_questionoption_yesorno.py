# Generated by Django 2.0 on 2022-11-30 09:50

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('voting', '0004_auto_20221130_0934'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='questionoption',
            name='yesorno',
        ),
    ]
