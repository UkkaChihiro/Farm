# -*- coding: utf-8 -*-
# Generated by Django 1.11.3 on 2017-10-13 07:38
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('userdata', '0003_auto_20171005_0800'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='aboutbusiness',
            unique_together=set([]),
        ),
        migrations.RemoveField(
            model_name='aboutbusiness',
            name='img_1',
        ),
        migrations.RemoveField(
            model_name='aboutbusiness',
            name='img_2',
        ),
        migrations.RemoveField(
            model_name='aboutbusiness',
            name='img_3',
        ),
        migrations.RemoveField(
            model_name='aboutbusiness',
            name='num',
        ),
    ]
