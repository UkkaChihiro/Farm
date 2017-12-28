from django.db import models

from catalog.models import Group
from userdata.models import ProfileBusiness, Address


class Farm(models.Model):
    class Meta:
        verbose_name = 'Farm'
        verbose_name_plural = 'Farms'

    profile = models.ForeignKey(ProfileBusiness)
    name = models.CharField(max_length=256)
    mark_deleted = models.BooleanField(default=False)

    def __str__(self):
        return self.name


class AddressFarm(Address):
    class Meta:
        verbose_name = 'Farm address'
        verbose_name_plural = 'Farm addresses'

    profile = models.OneToOneField(Farm)


class FarmGroupMap(models.Model):
    class Meta:
        unique_together = (("farm", "group"),)

    farm = models.ForeignKey(Farm)
    group = models.ForeignKey(Group)

    def __str__(self):
        return str(self.id)
