from django.contrib import admin

from .models import Language, CountryNumberphone




@admin.register(Language)
class LanguageAdmin(admin.ModelAdmin):
    pass


@admin.register(CountryNumberphone)
class CountryNumberphoneAdmin(admin.ModelAdmin):
    pass
