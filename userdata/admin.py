from django.contrib import admin

from catalog.models import TypeProductForProfile, CategoryForProfile, \
    SubcategoryForProfile, GroupForProfile
from userdata.models.address import PickUpWorkTime
from userdata.models.profile_business import PhotoAboutBusiness
from .models import Profile, ProfileBusiness, AboutBusiness

from userdata.models import (
    AddressDeliveryBusiness, AddressDeliveryProfile,
    AddressLegal, AddressDeliveryDocs, AddressPickUp, ClassProductForProfile,
    AddressPayment
)


class AddressPaymentInline(admin.TabularInline):
    fields = ("name", "id")
    model = AddressPayment


class PickUpWorkTimeInline(admin.TabularInline):
    model = PickUpWorkTime


class AddressDeliveryProfileInline(admin.TabularInline):
    model = AddressDeliveryProfile


class ClassProductForProfileInline(admin.TabularInline):
    model = ClassProductForProfile


class CategoryForProfileInline(admin.TabularInline):
    model = CategoryForProfile


class SubcategoryForProfileInline(admin.TabularInline):
    model = SubcategoryForProfile


class GroupForProfileInline(admin.TabularInline):
    model = GroupForProfile


class TypeProductForProfileInline(admin.TabularInline):
    model = TypeProductForProfile


class PhotoAboutBusinessInline(admin.TabularInline):
    model = PhotoAboutBusiness


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    AddressDeliveryProfileInline, ClassProductForProfileInline, TypeProductForProfileInline,
               AddressPaymentInline, GroupForProfileInline, CategoryForProfileInline, SubcategoryForProfileInline]

    list_display = ['id', 'user', 'number_phone']


@admin.register(ProfileBusiness)
class ProfileBusinessAdmin(admin.ModelAdmin):
    list_display = ['id', 'profile', 'email']


@admin.register(AddressDeliveryProfile)
class AddressDeliveryProfileAdmin(admin.ModelAdmin):
    fields = ['name', 'address', 'postal_code']
    list_display = ['id', 'content_type', 'object_id', 'city', 'region', 'country', 'address', 'postal_code', 'profile', 'default']

    def city(self, obj):
        return obj.city if obj.city else None
    def region(self, obj):
        return obj.city.region if obj.city else None
    def country(self, obj):
        return obj.city.region.country if obj.city else None


@admin.register(AddressLegal)
class AddressLegalAdmin(admin.ModelAdmin):
    fields = ['name', 'address', 'postal_code']
    list_display = ['id', 'name', 'content_type', 'object_id', 'city', 'region', 'country', 'address', 'postal_code', 'profile']

    def city(self, obj):
        return obj.city if obj.city else None
    def region(self, obj):
        return obj.city.region if obj.city else None
    def country(self, obj):
        return obj.city.region.country if obj.city else None


@admin.register(AddressDeliveryBusiness)
class AddressDeliveryBusinessAdmin(admin.ModelAdmin):
    fields = ['name', 'address', 'postal_code']
    list_display = ['id', 'name', 'content_type', 'object_id', 'city', 'region', 'country', 'address', 'postal_code', 'profile']

    def city(self, obj):
        return obj.city if obj.city else None
    def region(self, obj):
        return obj.city.region if obj.city else None
    def country(self, obj):
        return obj.city.region.country if obj.city else None


@admin.register(AddressDeliveryDocs)
class AddressDeliveryDocsAdmin(admin.ModelAdmin):
    fields = ['name', 'address', 'postal_code']
    list_display = ['id', 'name', 'content_type', 'object_id', 'city', 'region', 'country', 'address', 'postal_code', 'profile']
    def city(self, obj):
        return obj.city if obj.city else None
    def region(self, obj):
        return obj.city.region if obj.city else None
    def country(self, obj):
        return obj.city.region.country if obj.city else None


@admin.register(AddressPickUp)
class AddressPickUpAdmin(admin.ModelAdmin):
    inlines = [PickUpWorkTimeInline, ]
    fields = ['name', 'address', 'postal_code']
    list_display = ['id', 'name', 'content_type', 'object_id', 'city', 'region', 'country', 'address', 'postal_code', 'profile']
    def city(self, obj):
        return obj.city if obj.city else None
    def region(self, obj):
        return obj.city.region if obj.city else None
    def country(self, obj):
        return obj.city.region.country if obj.city else None


@admin.register(PickUpWorkTime)
class PickUpWorkTimeAdmin(admin.ModelAdmin):
    list_display = ['id', 'pickup_address', 'day', 'open', 'close', 'break_start', 'break_stop']

    def pickup_address(self, obj):
        return obj.pickup


@admin.register(AddressPayment)
class AddressPaymentAdmin(admin.ModelAdmin):
    fields = ['name', 'address', 'postal_code']
    list_display = ['id', 'name', 'content_type', 'object_id', 'city', 'region', 'country', 'address', 'postal_code', 'profile']
    def city(self, obj):
        return obj.city if obj.city else None
    def region(self, obj):
        return obj.city.region if obj.city else None
    def country(self, obj):
        return obj.city.region.country if obj.city else None


@admin.register(AboutBusiness)
class AboutBusinessAdmin(admin.ModelAdmin):
    inlines = [PhotoAboutBusinessInline, ]
    list_display = ['id', 'profile', 'title', 'video', 'image_count']

    def image_count(self, obj):
        return PhotoAboutBusiness.objects.filter(about_business=obj).count()


@admin.register(PhotoAboutBusiness)
class PhotoAboutBusinessAdmin(admin.ModelAdmin):
    list_display = ['id', 'business_profile']
    def business_profile(self, obj):
        return obj.about_business.profile







