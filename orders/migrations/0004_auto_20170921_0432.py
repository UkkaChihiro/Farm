# -*- coding: utf-8 -*-
# Generated by Django 1.11.3 on 2017-09-21 04:32
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('orders', '0003_auto_20170919_1110'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='order',
            name='order_status',
        ),
        migrations.AlterField(
            model_name='orderstatus',
            name='order',
            field=models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='orders.Order'),
        ),
        migrations.AlterField(
            model_name='orderstatus',
            name='status',
            field=models.PositiveSmallIntegerField(choices=[(1, 'new'), (2, 'paid for'), (3, 'ready to ship'), (4, 'shipped'), (5, 'canceled'), (6, 'delivered')]),
        ),
    ]
