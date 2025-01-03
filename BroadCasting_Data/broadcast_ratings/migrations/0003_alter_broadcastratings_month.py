# Generated by Django 5.1.1 on 2024-12-12 05:44

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('broadcast_ratings', '0002_broadcastratings_month'),
    ]

    operations = [
        migrations.AlterField(
            model_name='broadcastratings',
            name='month',
            field=models.CharField(max_length=7, validators=[django.core.validators.RegexValidator(message='날짜는 "YYYY-MM" 형식이어야 합니다.', regex='^\\d{4}-(0[1-9]|1[0-2])$')]),
        ),
    ]
