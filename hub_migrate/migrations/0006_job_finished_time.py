# -*- coding: utf-8 -*-
# Generated by Django 1.11.5 on 2017-11-03 14:48
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('hub_migrate', '0005_job_migrating_table'),
    ]

    operations = [
        migrations.AddField(
            model_name='job',
            name='finished_time',
            field=models.DateTimeField(blank=True, null=True),
        ),
    ]
