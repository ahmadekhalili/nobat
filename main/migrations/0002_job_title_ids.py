# Generated by Django 5.2 on 2025-04-17 12:57

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='job',
            name='title_ids',
            field=models.TextField(blank=True),
        ),
    ]
