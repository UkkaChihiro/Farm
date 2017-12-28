from django.contrib import admin
from farm.models import *


class AddressFarmInline(admin.TabularInline):
    model = AddressFarm

class FarmGroupInline(admin.TabularInline):
    model = FarmGroupMap


@admin.register(Farm)
class FarmAdmin(admin.ModelAdmin):
    inlines = [FarmGroupInline, AddressFarmInline, ]
    list_display = ['name', 'profile', 'mark_deleted', 'address_exists', 'id']
    readonly_fields = ('Address',)

    def address_exists(self,obj):
        fa = AddressFarm.objects.filter(profile=obj).exists()
        return fa

    def Address(self, obj):
        address = AddressFarm.objects.filter(profile=obj).first()
        city = address.city
        region = address.city.region
        country = address.city.region.country
        addr = address.address
        post = address.postal_code

        return '{0}, {1}, {2}, {3}, {4}'.format(addr, city, region, country, post)


@admin.register(AddressFarm)
class AddressFarmAdmin(admin.ModelAdmin):
    fields = ['name', 'address', 'postal_code']
    list_display = ['id', 'name', 'content_type', 'object_id', 'city', 'region', 'country', 'address', 'postal_code', 'profile']

    def city(self, obj):
        return obj.city if obj.city else None
    def region(self, obj):
        return obj.city.region if obj.city else None
    def country(self, obj):
        return obj.city.region.country if obj.city else None
