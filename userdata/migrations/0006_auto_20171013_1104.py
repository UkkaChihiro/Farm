# -*- coding: utf-8 -*-
# Generated by Django 1.11.3 on 2017-10-13 11:04
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('userdata', '0005_photoaboutbusiness'),
    ]

    operations = [
        migrations.AlterField(
            model_name='aboutbusiness',
            name='video',
            field=models.URLField(blank=True, null=True),
        ),
    ]
