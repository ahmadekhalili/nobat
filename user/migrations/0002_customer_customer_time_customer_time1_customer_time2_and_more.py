# Generated by Django 5.1.6 on 2025-03-10 09:24

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('user', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='customer',
            name='customer_time',
            field=models.CharField(blank=True, max_length=30),
        ),
        migrations.AddField(
            model_name='customer',
            name='time1',
            field=models.CharField(blank=True, max_length=30),
        ),
        migrations.AddField(
            model_name='customer',
            name='time2',
            field=models.CharField(blank=True, max_length=30),
        ),
        migrations.AddField(
            model_name='customer',
            name='time3',
            field=models.CharField(blank=True, max_length=30),
        ),
        migrations.AddField(
            model_name='customer',
            name='time4',
            field=models.CharField(blank=True, max_length=30),
        ),
    ]
