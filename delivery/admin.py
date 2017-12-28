from django.contrib import admin
from .models import TarifsForCountry, TariffForProduct


class TariffForProductInline(admin.TabularInline):
    model = TariffForProduct


@admin.register(TarifsForCountry)
class TarifAdmin(admin.ModelAdmin):
    inlines = [TariffForProductInline]
    list_display = ['id', 'profile', 'country', 'mark', 'weight', 'type', 'price', 'name']


@admin.register(TariffForProduct)
class TariffForProductAdmin(admin.ModelAdmin):
    list_display = ['id', 'tariff', 'product']