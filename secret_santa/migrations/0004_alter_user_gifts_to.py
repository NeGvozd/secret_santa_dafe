# Generated by Django 5.0.7 on 2024-07-25 20:00

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('secret_santa', '0003_alter_user_gifts_to_alter_user_giver_to'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='gifts_to',
            field=models.IntegerField(blank=True, null=True, unique=True, verbose_name='Дарит(кому)'),
        ),
    ]
