# Generated by Django 5.0.3 on 2024-04-05 09:57

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ebmsapp', '0002_alter_booking_customer_alter_event_organizer_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='ticket',
            name='event',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='ebmsapp.event'),
        ),
    ]
