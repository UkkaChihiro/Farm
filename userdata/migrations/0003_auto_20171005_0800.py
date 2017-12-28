# -*- coding: utf-8 -*-
# Generated by Django 1.11.3 on 2017-10-05 08:00
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('userdata', '0002_auto_20170925_0607'),
    ]

    operations = [
        migrations.CreateModel(
            name='PickUpWorkTime',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('day', models.PositiveSmallIntegerField(choices=[(1, 'Monday'), (2, 'Tuesday'), (3, 'Wednesday'), (4, 'Thursday'), (5, 'Friday'), (6, 'Saturday'), (7, 'Sunday')])),
                ('open', models.TimeField(null=True)),
                ('close', models.TimeField(null=True)),
                ('break_start', models.TimeField(blank=True, null=True)),
                ('break_stop', models.TimeField(blank=True, null=True)),
                ('pickup', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='userdata.AddressPickUp')),
            ],
        ),
        migrations.AlterUniqueTogether(
            name='pickupworktime',
            unique_together=set([('pickup', 'day')]),
        ),
    ]
