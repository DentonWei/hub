# -*- coding: utf-8 -*-
# Generated by Django 1.11.5 on 2017-11-02 15:44
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('hub_migrate', '0003_job_finished_table'),
    ]

    operations = [
        migrations.RenameField(
            model_name='sqoopsentence',
            old_name='connect',
            new_name='host',
        ),
        migrations.AddField(
            model_name='sqoopsentence',
            name='database',
            field=models.CharField(default=192, max_length=30),
            preserve_default=False,
        ),
    ]
