# -*- coding: utf-8 -*-
# Generated by Django 1.11.4 on 2017-09-14 11:01
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
from django.core import serializers
import django.db.models.deletion

import os


def load_data_group(apps, schema_editor):
    group_model = apps.get_model('catalog', 'Group')
    with open(os.path.join(settings.BASE_DIR, 'catalog', 'fixtures', 'group.json'), 'rb') as data:
        groups = serializers.deserialize('json', data)
        group_model.objects.bulk_create((group.object for group in groups))

def unload_data_group(apps, schema_editor):
    apps.get_model('catalog', 'Group').objects.all().delete()


def load_data_category(apps, schema_editor):
    cat_model = apps.get_model('catalog', 'Category')
    with open(os.path.join(settings.BASE_DIR, 'catalog', 'fixtures', 'category.json'), 'rb') as data:
        categories = serializers.deserialize('json', data)
        cat_model.objects.bulk_create((cat.object for cat in categories))

def unload_data_category(apps, schema_editor):
    apps.get_model('catalog', 'Category').objects.all().delete()


def load_data_subcategory(apps, schema_editor):
    subcat_model = apps.get_model('catalog', 'SubCategory')
    with open(os.path.join(settings.BASE_DIR, 'catalog', 'fixtures', 'subcategory.json'), 'rb') as data:
        subcategories = serializers.deserialize('json', data)
        subcat_model.objects.bulk_create((subcat.object for subcat in subcategories))

def unload_data_subcategory(apps, schema_editor):
    apps.get_model('catalog', 'SubCategory').objects.all().delete()


def load_data_types(apps, schema_editor):
    type_model = apps.get_model('catalog', 'TypeInCategory')
    with open(os.path.join(settings.BASE_DIR, 'catalog', 'fixtures', 'typeincategory.json'), 'rb') as data:
        types = serializers.deserialize('json', data)
        type_model.objects.bulk_create((type.object for type in types))

def unload_data_types(apps, schema_editor):
    apps.get_model('catalog', 'SubCategory').objects.all().delete()


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('catalog', '0001_initial'),
        ('bank', '0001_initial'),
        ('userdata', '0001_initial'),
        ('geodata', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AddField(
            model_name='typeproductforprofile',
            name='profile',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='userdata.Profile'),
        ),
        migrations.AddField(
            model_name='typeincategory',
            name='category',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='catalog.Category'),
        ),
        migrations.AddField(
            model_name='tagsforproduct',
            name='product',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='catalog.Product'),
        ),
        migrations.AddField(
            model_name='subcategory',
            name='parent',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='catalog.Category'),
        ),
        migrations.AddField(
            model_name='soldproduct',
            name='currency',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to='bank.Currency'),
        ),
        migrations.AddField(
            model_name='soldproduct',
            name='product',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='catalog.Product'),
        ),
        migrations.AddField(
            model_name='soldproduct',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='producttype',
            name='product',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='catalog.Product'),
        ),
        migrations.AddField(
            model_name='producttype',
            name='type',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='catalog.TypeInCategory'),
        ),
        migrations.AddField(
            model_name='product',
            name='category',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='catalog.SubCategory'),
        ),
        migrations.AddField(
            model_name='product',
            name='country',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='geodata.Country'),
        ),
        migrations.AddField(
            model_name='product',
            name='currency',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to='bank.Currency'),
        ),
        migrations.AddField(
            model_name='product',
            name='profile_business',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='userdata.ProfileBusiness'),
        ),
        migrations.AddField(
            model_name='pickupaddressforproduct',
            name='address',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='userdata.AddressPickUp'),
        ),
        migrations.AddField(
            model_name='pickupaddressforproduct',
            name='product',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='catalog.Product'),
        ),
        migrations.AddField(
            model_name='listoffavorites',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='imgproduct',
            name='product',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='catalog.Product'),
        ),
        migrations.AddField(
            model_name='favoriteproduct',
            name='list',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='catalog.ListOfFavorites'),
        ),
        migrations.AddField(
            model_name='favoriteproduct',
            name='product',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='catalog.Product'),
        ),
        migrations.AddField(
            model_name='favoriteproduct',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='classproduct',
            name='product',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='catalog.Product'),
        ),
        migrations.AddField(
            model_name='category',
            name='parent',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='catalog.Group'),
        ),
        migrations.AlterUniqueTogether(
            name='typeproductforprofile',
            unique_together=set([('name', 'profile')]),
        ),
        migrations.AlterUniqueTogether(
            name='typeincategory',
            unique_together=set([('name', 'category')]),
        ),
        migrations.AlterUniqueTogether(
            name='producttype',
            unique_together=set([('type', 'product')]),
        ),
        migrations.AlterUniqueTogether(
            name='pickupaddressforproduct',
            unique_together=set([('product', 'address')]),
        ),
        migrations.AlterUniqueTogether(
            name='favoriteproduct',
            unique_together=set([('user', 'product')]),
        ),
        migrations.AlterUniqueTogether(
            name='classproduct',
            unique_together=set([('name', 'product')]),
        ),
        migrations.RunPython(
            load_data_group,
            reverse_code=unload_data_group
        ),
        migrations.RunPython(
            load_data_category,
            reverse_code=unload_data_category
        ),
        migrations.RunPython(
            load_data_subcategory,
            reverse_code=unload_data_subcategory
        ),

        migrations.RunPython(
            load_data_types,
            reverse_code=unload_data_types
        ),

    ]
