# -*- coding: utf-8 -*-
# Generated by Django 1.11.3 on 2017-10-24 10:11
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('catalog', '0012_auto_20171023_1258'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='bestproduct',
            options={'verbose_name': 'Best product', 'verbose_name_plural': 'Best products'},
        ),
        migrations.AlterModelOptions(
            name='category',
            options={'verbose_name': 'Category', 'verbose_name_plural': 'Categories'},
        ),
        migrations.AlterModelOptions(
            name='categoryforprofile',
            options={'verbose_name': 'Category for profile', 'verbose_name_plural': 'Categories for profiles'},
        ),
        migrations.AlterModelOptions(
            name='favoriteproduct',
            options={'verbose_name': 'Favorite product', 'verbose_name_plural': 'Favorite products'},
        ),
        migrations.AlterModelOptions(
            name='groupforprofile',
            options={'verbose_name': 'Group for profile', 'verbose_name_plural': 'Groups for profiles'},
        ),
        migrations.AlterModelOptions(
            name='imgproduct',
            options={'verbose_name': 'Product image', 'verbose_name_plural': 'Product images'},
        ),
        migrations.AlterModelOptions(
            name='listoffavorites',
            options={'verbose_name': 'Favorite list', 'verbose_name_plural': 'Favorite lists'},
        ),
        migrations.AlterModelOptions(
            name='pickupaddressforproduct',
            options={'verbose_name': 'Sold product', 'verbose_name_plural': 'Sold products'},
        ),
        migrations.AlterModelOptions(
            name='product',
            options={'verbose_name': 'Product', 'verbose_name_plural': 'Products'},
        ),
        migrations.AlterModelOptions(
            name='producttype',
            options={'verbose_name': 'Product type', 'verbose_name_plural': 'Product types'},
        ),
        migrations.AlterModelOptions(
            name='soldproduct',
            options={'verbose_name': 'Sold product', 'verbose_name_plural': 'Sold products'},
        ),
        migrations.AlterModelOptions(
            name='subcategory',
            options={'verbose_name': 'SubCategory', 'verbose_name_plural': 'SubCategories'},
        ),
        migrations.AlterModelOptions(
            name='subcategoryforprofile',
            options={'verbose_name': 'SubCategory for profile', 'verbose_name_plural': 'SubCategories for profiles'},
        ),
        migrations.AlterModelOptions(
            name='tagsforproduct',
            options={'verbose_name': 'Tag', 'verbose_name_plural': 'Tags'},
        ),
        migrations.AlterModelOptions(
            name='typeincategory',
            options={'verbose_name': 'Type in category', 'verbose_name_plural': 'Types in categories'},
        ),
        migrations.AlterModelOptions(
            name='typeproductforprofile',
            options={'verbose_name': 'Product type for profile', 'verbose_name_plural': 'Product types for profiles'},
        ),
        migrations.AlterModelOptions(
            name='videoproduct',
            options={'verbose_name': 'Product video', 'verbose_name_plural': 'Product video'},
        ),
        migrations.AlterModelOptions(
            name='viewedproduct',
            options={'verbose_name': 'Viewed product', 'verbose_name_plural': 'Viewed products'},
        ),
    ]
