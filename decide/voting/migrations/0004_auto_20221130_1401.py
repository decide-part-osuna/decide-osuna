# Generated by Django 2.0 on 2022-11-30 14:01

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('voting', '0003_auto_20180605_0842'),
    ]

    operations = [
        migrations.AddField(
            model_name='question',
            name='questionYesNO',
            field=models.BooleanField(default=False, help_text='¿Quieres una pregunta de sí o no?'),
        ),
        migrations.AddField(
            model_name='questionoption',
            name='boolean',
            field=models.NullBooleanField(verbose_name='Sí o No'),
        ),
        migrations.AlterField(
            model_name='questionoption',
            name='option',
            field=models.TextField(blank=True),
        ),
    ]
