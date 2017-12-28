from django.contrib import admin
from .models import Country, Region, City, NotExistCity, NotExistRegion


class CityInline(admin.TabularInline):
    model = City


class RegionInline(admin.TabularInline):
    model = Region


@admin.register(Country)
class CountryAdmin(admin.ModelAdmin):
    inlines = [RegionInline, ]
    ordering = ('id',)
    list_display = ['name_en', 'group', 'id']

    def group(self, obj):
        return obj.group


@admin.register(Region)
class RegionAdmin(admin.ModelAdmin):
    inlines = [CityInline, ]
    ordering = ('id',)
    list_display = ['name_en', 'name_ru', 'country', 'id']


@admin.register(City)
class CityAdmin(admin.ModelAdmin):
    list_display = ['name_en', 'name_ru', 'region', 'country', 'id']
    ordering = ('id',)
    def country(self, obj):
        return obj.region.country


@admin.register(NotExistCity)
class NotExistCityAdmin(admin.ModelAdmin):
    list_display = ['content_type', 'object_id', 'name_en', 'region', 'country', 'id']

    def region(self, obj):
        return obj.region if obj.region else None

    def country(self, obj):
        return obj.region.country if obj.region else None


@admin.register(NotExistRegion)
class NotExistRegionAdmin(admin.ModelAdmin):
    list_display = ['name_en', 'country', 'id']

    def country(self, obj):
        return obj.country
