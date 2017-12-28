from django.db import models

from djmoney.models.fields import MoneyField
from geodata.models import Country
from userdata.models import ProfileBusiness
from catalog.models import Product


class TarifsForCountry(models.Model):
    class Meta:
        verbose_name = 'Tariff for country'
        verbose_name_plural = 'Tariffs for countries'

    MARK_CHOISE = (
        (1, '='),
        (2, '>'),
        (3, '->')
    )
    DELIVERY_TYPE = (
        (1, 'Standart'),
        (2, 'Express')
    )

    name = models.CharField(max_length=150, blank=True, null=True)
    profile = models.ForeignKey(ProfileBusiness)
    country = models.ForeignKey(Country)
    mark = models.PositiveSmallIntegerField(choices=MARK_CHOISE, default=1)
    weight = models.IntegerField(default=0)
    delivery_time_from = models.IntegerField(default=1)
    delivery_time_to = models.IntegerField(default=1)
    price = MoneyField(max_digits=10, decimal_places=2, default_currency='EUR')
    type = models.SmallIntegerField(choices=DELIVERY_TYPE, default=1)

    def __str__(self):
        return str(self.id)


class TariffForProduct(models.Model):
    class Meta:
        unique_together = ('tariff', 'product')
        verbose_name = 'Tariff for product'
        verbose_name_plural = 'Tariffs for products'

    tariff = models.ForeignKey(TarifsForCountry)
    product = models.ForeignKey(Product)

    def __str__(self):
        return str(self.id)
