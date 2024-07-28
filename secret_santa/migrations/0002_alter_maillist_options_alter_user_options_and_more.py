# Generated by Django 5.0.7 on 2024-07-25 14:42

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('secret_santa', '0001_initial'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='maillist',
            options={'verbose_name': 'Рассылка', 'verbose_name_plural': 'Рассылки'},
        ),
        migrations.AlterModelOptions(
            name='user',
            options={'verbose_name': 'Участник', 'verbose_name_plural': 'Участники'},
        ),
        migrations.AddField(
            model_name='user',
            name='giver_to',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='secret_santa.user'),
        ),
    ]