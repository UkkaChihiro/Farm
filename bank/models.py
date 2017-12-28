from django.db import models


class Currency(models.Model):
    name = models.CharField(max_length=50)
    short_name = models.CharField(max_length=3)

    def __str__(self):
        return self.short_name


class ExchangeRate(models.Model):
    currency = models.ForeignKey(Currency)
    rate = models.FloatField()
    created = models.DateTimeField()
