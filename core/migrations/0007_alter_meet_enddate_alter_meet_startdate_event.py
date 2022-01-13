# Generated by Django 4.0.1 on 2022-01-12 17:42

import datetime
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0006_remove_event_meet_delete_entry_delete_event'),
    ]

    operations = [
        migrations.AlterField(
            model_name='meet',
            name='endDate',
            field=models.DateField(default=datetime.date(2022, 1, 12), verbose_name='End Date'),
        ),
        migrations.AlterField(
            model_name='meet',
            name='startDate',
            field=models.DateField(default=datetime.date(2022, 1, 12), verbose_name='Start Date'),
        ),
        migrations.CreateModel(
            name='Event',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=200)),
                ('entriesPath', models.CharField(max_length=100)),
                ('date', models.DateField(default=datetime.date(2022, 1, 12), verbose_name='Event Date')),
                ('meet', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='core.meet')),
            ],
        ),
    ]