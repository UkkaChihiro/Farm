# -*- coding: utf-8 -*-
# Generated by Django 1.11.3 on 2017-10-13 05:36
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('catalog', '0010_auto_20171013_0500'),
    ]

    operations = [
        migrations.RenameField(
            model_name='product',
            old_name='expiration_date',
            new_name='expiry_days',
        ),
    ]