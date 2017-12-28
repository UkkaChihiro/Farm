from django.contrib import admin
from bank.models import Currency


@admin.register(Currency)
class CurrencyAdmin(admin.ModelAdmin):
    pass