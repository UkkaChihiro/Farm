from django.db import models
from geodata.models import Country


class ResetPassword(models.Model):
    key = models.CharField(max_length=50)
    email = models.EmailField(max_length=256)
    updated = models.DateTimeField(auto_now=True)


class Language(models.Model):
    name = models.CharField(max_length=255)
    short_name = models.CharField(max_length=3)
    flag = models.ImageField(null=True, upload_to='uploads/languages/')

    def __str__(self):
        return self.name


class CountryNumberphone(models.Model):
    country = models.ForeignKey(Country)
    code = models.PositiveSmallIntegerField()
    max_digits = models.PositiveSmallIntegerField(blank=True, null=True)

    def __str__(self):
        return self.country.name_en