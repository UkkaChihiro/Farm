# -*- coding: utf-8 -*-
# Generated by Django 1.11.3 on 2017-10-24 08:30
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('userdata', '0006_auto_20171013_1104'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='aboutbusiness',
            options={'verbose_name': 'About me page', 'verbose_name_plural': 'About me pages'},
        ),
        migrations.AlterModelOptions(
            name='addressdeliverybusiness',
            options={'verbose_name': 'Business delivery address', 'verbose_name_plural': 'Business delivery addresses'},
        ),
        migrations.AlterModelOptions(
            name='addressdeliverydocs',
            options={'verbose_name': 'Documents delivery address', 'verbose_name_plural': 'Documents delivery addresses'},
        ),
        migrations.AlterModelOptions(
            name='addressdeliveryprofile',
            options={'verbose_name': 'Personal delivery address', 'verbose_name_plural': 'Personal delivery addresses'},
        ),
        migrations.AlterModelOptions(
            name='addresslegal',
            options={'verbose_name': 'Legal address', 'verbose_name_plural': 'Legal addresses'},
        ),
        migrations.AlterModelOptions(
            name='addresspayment',
            options={'verbose_name': 'Payment address', 'verbose_name_plural': 'Payment addresses'},
        ),
        migrations.AlterModelOptions(
            name='addresspickup',
            options={'verbose_name': 'Pick up point address', 'verbose_name_plural': 'Pick up point addresses'},
        ),
        migrations.AlterModelOptions(
            name='photoaboutbusiness',
            options={'verbose_name': 'About me image', 'verbose_name_plural': 'About me images'},
        ),
        migrations.AlterModelOptions(
            name='pickupworktime',
            options={'verbose_name': 'Pick up point work time', 'verbose_name_plural': 'Pick up point work schedule'},
        ),
        migrations.AlterModelOptions(
            name='profile',
            options={'verbose_name': 'Personal profile', 'verbose_name_plural': 'Personal profiles'},
        ),
        migrations.AlterModelOptions(
            name='profilebusiness',
            options={'verbose_name': 'Business profile', 'verbose_name_plural': 'Business profiles'},
        ),
        migrations.AlterField(
            model_name='aboutbusiness',
            name='profile',
            field=models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='userdata.ProfileBusiness'),
        ),
    ]