import os

from django.core.exceptions import ValidationError
from django.db import models
from django.contrib.auth.models import User
from django.dispatch import receiver

from django.db.models.signals import pre_delete
from django import forms

from bank.models import Currency
from efarm_bio import settings
from userdata.models import ProfileBusiness, Profile, AddressPickUp, ClassProductForProfile
from geodata.models import Country
from djmoney.models.fields import MoneyField
from django.contrib import messages

def pi_directory_path(instance, filename):
    return os.path.join(settings.PHOTO_PROD_URL, str(instance.id), filename)

class Group(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(max_length=100, blank=True, null=True)

    def __str__(self):
        return self.name


class Category(models.Model):
    class Meta:
        verbose_name = 'Category'
        verbose_name_plural = 'Categories'

    name = models.CharField(max_length=100)
    slug = models.SlugField(max_length=100, blank=True, null=True)
    parent = models.ForeignKey(Group)

    def __str__(self):
        return self.name


class SubCategory(models.Model):
    class Meta:
        verbose_name = 'SubCategory'
        verbose_name_plural = 'SubCategories'

    name = models.CharField(max_length=100)
    slug = models.SlugField(max_length=100, blank=True, null=True)
    parent = models.ForeignKey(Category)

    def __str__(self):
        return self.name


MEASURE = (
        (1, 'kg'),
        (2, 'liter'),
        (3, 'object'),
    )


class Product(models.Model):
    class Meta:
        verbose_name = 'Product'
        verbose_name_plural = 'Products'

    IMG_COUNT = 4
    profile_business = models.ForeignKey(ProfileBusiness)
    category = models.ForeignKey(SubCategory)
    currency = models.ForeignKey(Currency, default=1)
    name = models.CharField(max_length=256)
    description = models.TextField()
    price = MoneyField(max_digits=10, decimal_places=2, default_currency='EUR')
    name_en = models.CharField(max_length=256, blank=True, null=True)
    description_en = models.TextField(blank=True, null=True)
    number_of_packages = models.IntegerField(default=0)
    weight_of_pack = models.FloatField(default=0)
    nondurable = models.BooleanField(default=False)
    expiry_days = models.PositiveSmallIntegerField(default=1)
    measure = models.PositiveSmallIntegerField(choices=MEASURE, default=1)
    measure_count = models.IntegerField(default=0)
    discount_price = MoneyField(max_digits=10, decimal_places=2, default_currency='EUR', default=0, blank=True, null=True)
    video = models.URLField(blank=True, null=True)
    country = models.ForeignKey(Country, blank=True, null=True)
    region = models.CharField(max_length=100, blank=True, null=True)
    active = models.BooleanField(default=False)
    checked = models.BooleanField(default=False)
    mark_deleted = models.BooleanField(default=False)
    updated_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)
    start_of_sales_date = models.DateTimeField(blank=True, null=True)
    end_of_sales_date = models.DateTimeField(blank=True, null=True)

    @staticmethod
    def for_buyer(user, ship_to):
        '''
        :param user:
        :param ship_to:
        :return: list(available_products)
        '''
        from delivery.models import TariffForProduct

        class_prod = {c.name for c in ClassProductForProfile.objects.filter(profile=user) if user}

        group = [g.group for g in GroupForProfile.objects.filter(profile=user) if user]

        category = [c.category for c in CategoryForProfile.objects.filter(profile=user) if user]

        subcategory = [s.subcategory for s in SubcategoryForProfile.objects.filter(profile=user) if user]

        if not group:
            group = Group.objects.all()

        if not category:
            category = Category.objects.all()

        if not subcategory:
            subcategory = SubCategory.objects.all()

        list_prod = [p.product for p in TariffForProduct.objects.filter(tariff__country=ship_to)
                     if p.product.checked and p.product.mark_deleted == False
                     and p.product.category.parent.parent in group
                     and p.product.category.parent in category
                     and p.product.category in subcategory
                     ]
        if class_prod:
            prod_for_user = [p for p in list_prod if set(p.classproduct_set.all().values_list('name', flat=True)) & set(class_prod)]
        else:
            prod_for_user = [p for p in list_prod]

        # добавить фильтр по типам

        return prod_for_user

    @staticmethod
    def product_list(user, ship_to, price_min, price_max, group, category, subcategory, prod_types=[]):
        from delivery.models import TariffForProduct

        class_prod = {c.name for c in ClassProductForProfile.objects.filter(profile=user) if user}

        if not price_min:
            price_min = 0.00

        if not price_max:
            price_max = 99999.00

        if prod_types:
            prod_types = ProductType.objects.filter(type_id__in=prod_types)
        else:
            prod_types = ProductType.objects.all()

        list_prod = set(p.product for p in TariffForProduct.objects.filter(tariff__country=ship_to)
                        if p.product.checked and p.product.mark_deleted == False
                        and p.product.category.parent.parent in group
                        and p.product.category.parent in category
                        and p.product.category in subcategory
                        and price_min <= p.product.price.amount <= price_max)

        class_cross = lambda p: bool(set(p.classproduct_set.all().values_list('name', flat=True)) & set(class_prod)) if class_prod else True
        type_cross = lambda p: bool(set(p.producttype_set.all()) & set(prod_types))

        prod_for_user = list(p for p in list_prod if (class_cross(p) and type_cross(p)))

        return prod_for_user

    def __str__(self):
        return self.name


class TagsForProduct(models.Model):
    class Meta:
        verbose_name = 'Tag'
        verbose_name_plural = 'Tags'

    product = models.ForeignKey(Product)
    name = models.CharField(max_length=60)

    def __str__(self):
        return self.name


class ClassProduct(models.Model):
    class Meta:
        unique_together = ("name", "product")
        verbose_name = 'Class'
        verbose_name_plural = 'Classes'

    name = models.SmallIntegerField(choices=ClassProductForProfile.CLASS_PROD)
    product = models.ForeignKey(Product)

    def __str__(self):
        return str(self.name)


class TypeInCategory(models.Model):
    class Meta:
        unique_together = ("name", "category")
        verbose_name = 'Type in category'
        verbose_name_plural = 'Types in categories'

    name = models.CharField(max_length=50)
    category = models.ForeignKey(Category)

    def __str__(self):
        return str(self.name)


class ProductType(models.Model):
    class Meta:
        unique_together = ("type", "product")
        verbose_name = 'Product type'
        verbose_name_plural = 'Product types'

    type = models.ForeignKey(TypeInCategory)
    product = models.ForeignKey(Product)

    def __str__(self):
        return str(self.type)


class TypeProductForProfile(models.Model):
    class Meta:
        unique_together = ("name", "profile")
        verbose_name = 'Product type for profile'
        verbose_name_plural = 'Product types for profiles'

    name = models.ForeignKey(ProductType)
    profile = models.ForeignKey(Profile)


class ImgProduct(models.Model):
    class Meta:
        verbose_name = 'Product image'
        verbose_name_plural = 'Product images'

    product = models.ForeignKey(Product)
    img = models.ImageField(upload_to=pi_directory_path)
    avatar = models.BooleanField(default=False)
    created = models.DateTimeField(auto_now_add=True)

    def clean(self, delete=False):
        cleaned_data = super(ImgProduct, self).clean()
        if self._state.adding and ImgProduct.objects.filter(product=self.product).count() >= Product.IMG_COUNT:
            raise ValidationError('You can attach only {0} pictures to the product!'.format(Product.IMG_COUNT))
        if delete:
            raise forms.ValidationError('You can not delete the last image from product!')

        return cleaned_data

    def save(self):
        self.clean()
        super(ImgProduct, self).save()

#
# @receiver(pre_delete, sender=ImgProduct)
# def delete_imgproduct(sender, instance, **kwargs):
#     print(instance)
#     print(sender)
#     if ImgProduct.objects.filter(product=instance.product).count() == 1:
#         # raise ValidationError('You can not delete the last image from product!')
#         return instance.clean(True)


class VideoProduct(models.Model):
    class Meta:
        verbose_name = 'Product video'
        verbose_name_plural = 'Product video'

    product = models.ForeignKey(Product)
    video = models.FileField()
    created = models.DateTimeField(auto_now_add=True),


class ListOfFavorites(models.Model):
    class Meta:
        verbose_name = 'Favorite list'
        verbose_name_plural = 'Favorite lists'

    user = models.ForeignKey(User)
    name = models.CharField(max_length=15)
    created = models.DateTimeField(auto_now_add=True)


class FavoriteProduct(models.Model):
    class Meta:
        unique_together = ("user", "product")
        verbose_name = 'Favorite product'
        verbose_name_plural = 'Favorite products'

    user = models.ForeignKey(User)
    list = models.ForeignKey(ListOfFavorites, blank=True, null=True)
    product = models.ForeignKey(Product)
    created = models.DateTimeField(auto_now_add=True)


class ViewedProduct(models.Model):
    class Meta:
        verbose_name = 'Viewed product'
        verbose_name_plural = 'Viewed products'

    user = models.ForeignKey(User)
    product = models.ForeignKey(Product)
    created = models.DateTimeField(auto_now_add=True)


class SoldProduct(models.Model):
    class Meta:
        verbose_name = 'Sold product'
        verbose_name_plural = 'Sold products'

    user = models.ForeignKey(User)
    product = models.ForeignKey(Product)
    sold_time = models.DateTimeField(auto_now_add=True)
    price = models.FloatField(default=0)
    currency = models.ForeignKey(Currency, default=1)
    count = models.FloatField(default=0)
    measure = models.PositiveSmallIntegerField(choices=MEASURE, default=1)


class PickUpAddressForProduct(models.Model):
    class Meta:
        unique_together = ("product", "address")
        verbose_name = 'Sold product'
        verbose_name_plural = 'Sold products'

    product = models.ForeignKey(Product)
    address = models.ForeignKey(AddressPickUp)


class BestProduct(models.Model):
    class Meta:
        unique_together = ("product", "seller")
        verbose_name = 'Best product'
        verbose_name_plural = 'Best products'

    seller = models.ForeignKey(ProfileBusiness)
    product = models.ForeignKey(Product)


class GroupForProfile(models.Model):
    class Meta:
        verbose_name = 'Group for profile'
        verbose_name_plural = 'Groups for profiles'

    profile = models.ForeignKey(Profile)
    group = models.ForeignKey(Group)


class CategoryForProfile(models.Model):
    class Meta:
        verbose_name = 'Category for profile'
        verbose_name_plural = 'Categories for profiles'

    profile = models.ForeignKey(Profile)
    category = models.ForeignKey(Category)


class SubcategoryForProfile(models.Model):
    class Meta:
        verbose_name = 'SubCategory for profile'
        verbose_name_plural = 'SubCategories for profiles'

    profile = models.ForeignKey(Profile)
    subcategory = models.ForeignKey(SubCategory)

