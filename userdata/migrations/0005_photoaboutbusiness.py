# -*- coding: utf-8 -*-
# Generated by Django 1.11.3 on 2017-10-13 07:55
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion
import userdata.models.profile_business


class Migration(migrations.Migration):

    dependencies = [
        ('userdata', '0004_auto_20171013_0738'),
    ]

    operations = [
        migrations.CreateModel(
            name='PhotoAboutBusiness',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('photo', models.ImageField(blank=True, null=True, upload_to=userdata.models.profile_business.ab_directory_path)),
                ('about_business', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='userdata.AboutBusiness')),
            ],
        ),
    ]
