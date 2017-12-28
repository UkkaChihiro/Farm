# -*- coding: utf-8 -*-
# Generated by Django 1.11.4 on 2017-09-14 11:01
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion
import userdata.models.address


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('userdata', '0001_initial'),
        ('contenttypes', '0002_remove_content_type_name'),
        ('farm', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='farm',
            name='profile',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='userdata.ProfileBusiness'),
        ),
        migrations.AddField(
            model_name='addressfarm',
            name='content_type',
            field=models.ForeignKey(default=userdata.models.address.get_city_default_id, on_delete=django.db.models.deletion.CASCADE, to='contenttypes.ContentType'),
        ),
        migrations.AddField(
            model_name='addressfarm',
            name='profile',
            field=models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='farm.Farm'),
        ),
        migrations.AlterUniqueTogether(
            name='farmgroupmap',
            unique_together=set([('farm', 'group')]),
        ),
    ]
