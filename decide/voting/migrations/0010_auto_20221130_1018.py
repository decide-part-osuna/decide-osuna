# Generated by Django 2.0 on 2022-11-30 10:18

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('voting', '0009_auto_20221130_1006'),
    ]

    operations = [
        migrations.RenameField(
            model_name='questionoption',
            old_name='boolean',
            new_name='sino',
        ),
        migrations.AlterField(
            model_name='questionoption',
            name='option',
            field=models.TextField(blank=True),
        ),
    ]
