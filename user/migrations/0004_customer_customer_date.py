# Generated by Django 5.1.6 on 2025-03-10 12:54

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('user', '0003_customer_date1_customer_date2_customer_date3_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='customer',
            name='customer_date',
            field=models.CharField(blank=True, max_length=30),
        ),
    ]
