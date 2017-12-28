from django.contrib.contenttypes.fields import GenericForeignKey
from django.db import models
from userdata.models import Profile, ProfileBusiness
from django.contrib.contenttypes.models import ContentType
from geodata.models import City


def get_city_default_id():
    return ContentType.objects.get_for_model(City).id


class Address(models.Model):
    class Meta:
        abstract = True

    CITY_CHOICE = models.Q(app_label='geodata', model='city') | models.Q(app_label='geodata', model='notexistcity')

    content_type = models.ForeignKey(
        ContentType,
        on_delete=models.CASCADE,
        default=get_city_default_id,
        limit_choices_to=CITY_CHOICE
    )

    object_id = models.PositiveIntegerField(default=0)
    city = GenericForeignKey('content_type', 'object_id')
    address = models.CharField(max_length=256, default='Default address')
    postal_code = models.CharField(max_length=10, default='000000')
    name = models.CharField(max_length=256, blank=True, null=True)
    default = models.BooleanField(default=False)
    created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.address


class AddressLegal(Address):
    class Meta:
        verbose_name = 'Legal address'
        verbose_name_plural = 'Legal addresses'

    profile = models.OneToOneField(ProfileBusiness)


class AddressDeliveryProfile(Address):
    class Meta:
        verbose_name = 'Personal delivery address'
        verbose_name_plural = 'Personal delivery addresses'

    profile = models.ForeignKey(Profile)


class AddressPayment(Address):
    class Meta:
        verbose_name = 'Payment address'
        verbose_name_plural = 'Payment addresses'

    profile = models.ForeignKey(Profile)


class AddressDeliveryBusiness(Address):
    class Meta:
        verbose_name = 'Business delivery address'
        verbose_name_plural = 'Business delivery addresses'

    profile = models.ForeignKey(ProfileBusiness)


class AddressDeliveryDocs(Address):
    class Meta:
        verbose_name = 'Documents delivery address'
        verbose_name_plural = 'Documents delivery addresses'

    profile = models.ForeignKey(ProfileBusiness)


class AddressPickUp(Address):
    class Meta:
        verbose_name = 'Pick up point address'
        verbose_name_plural = 'Pick up point addresses'

    profile = models.ForeignKey(ProfileBusiness)
    name = models.CharField(max_length=100, blank=True, null=True)
    description = models.TextField(blank=True, null=True)


class PickUpWorkTime(models.Model):
    class Meta:
        unique_together = ['pickup', 'day']
        verbose_name = 'Pick up point work time'
        verbose_name_plural = 'Pick up point work schedule'

    DAY_OF_WEEK = (
        (1, 'Monday'),
        (2, 'Tuesday'),
        (3, 'Wednesday'),
        (4, 'Thursday'),
        (5, 'Friday'),
        (6, 'Saturday'),
        (7, 'Sunday')
    )

    pickup = models.ForeignKey(AddressPickUp)
    day = models.PositiveSmallIntegerField(choices=DAY_OF_WEEK)
    open = models.TimeField(null=True)
    close = models.TimeField(null=True)
    break_start = models.TimeField(null=True, blank=True)
    break_stop = models.TimeField(null=True, blank=True)




