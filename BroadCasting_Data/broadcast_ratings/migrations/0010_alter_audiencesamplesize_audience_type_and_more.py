# Generated by Django 5.1.1 on 2024-12-16 08:21

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('broadcast_ratings', '0009_alter_audiencesamplesize_audience_type_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='audiencesamplesize',
            name='audience_type',
            field=models.CharField(max_length=40),
        ),
        migrations.AlterField(
            model_name='broadcastratings',
            name='ratings_type',
            field=models.CharField(max_length=40),
        ),
    ]