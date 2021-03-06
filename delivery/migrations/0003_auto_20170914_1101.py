# -*- coding: utf-8 -*-
# Generated by Django 1.11.4 on 2017-09-14 11:01
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('userdata', '0001_initial'),
        ('delivery', '0002_tarifsforcountry_country'),
        ('catalog', '0002_auto_20170914_1101'),
    ]

    operations = [
        migrations.AddField(
            model_name='tarifsforcountry',
            name='profile',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='userdata.ProfileBusiness'),
        ),
        migrations.AddField(
            model_name='tariffforproduct',
            name='product',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='catalog.Product'),
        ),
        migrations.AddField(
            model_name='tariffforproduct',
            name='tariff',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='delivery.TarifsForCountry'),
        ),
    ]
