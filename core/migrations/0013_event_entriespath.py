# Generated by Django 4.0.1 on 2022-01-17 23:49

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0012_alter_meet_meetid'),
    ]

    operations = [
        migrations.AddField(
            model_name='event',
            name='entriesPath',
            field=models.CharField(default='None', max_length=100),
            preserve_default=False,
        ),
    ]
