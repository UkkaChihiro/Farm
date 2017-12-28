from django.db import models
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey


NAME_GROUP_OF_COUNTRY = (
    (0, 'Does not consist'),
    (1, 'European Union'),
    (2, 'Customs Union'),
    (3, 'Common market of South America'),
    (4, 'Andean Community'),
    (5, 'South Asian Union'),
    (6, 'The North American Union'),
    (7, 'Central American Common Market'),
    (8, 'South African Customs Union'),
    (9, 'Caribbean Community'),
)
#
# class GroupsOfCountries(models.Model):
#     group = models.PositiveSmallIntegerField(choices=NAME_GROUP_OF_COUNTRY, default=0)
    # def __str__(self):
    #     GROUP_NAMES_MAP = dict(NAME_GROUP_OF_COUNTRY)
    #     return dict(NAME_GROUP_OF_COUNTRY)[self.group]


class Country(models.Model):
    class Meta:
        verbose_name = 'Country'
        verbose_name_plural = 'Countries'

    group = models.PositiveSmallIntegerField(choices=NAME_GROUP_OF_COUNTRY, default=0)
    code = models.CharField(max_length=2, verbose_name='Country code', default=0)
    name_ru = models.CharField(max_length=255, verbose_name='Country name (russian)')
    name_en = models.CharField(max_length=255, verbose_name='Country name (english)')
    show = models.BooleanField(default=False)

    def __str__(self):
        return str(self.name_en)


class Region(models.Model):
    class Meta:
        verbose_name = 'Region'
        verbose_name_plural = 'Regions'

    country = models.ForeignKey(Country, verbose_name='Country')
    code = models.CharField(max_length=2, verbose_name='Region code', default=0)
    name_ru = models.CharField(max_length=255, verbose_name='Region name (russian)')
    name_en = models.CharField(max_length=255, verbose_name='Region name (english)')

    def __str__(self):
        return self.name_en


class City(models.Model):
    class Meta:
        verbose_name = 'City'
        verbose_name_plural = 'Cities'

    region = models.ForeignKey(Region, verbose_name='Region')
    code = models.CharField(max_length=2, verbose_name='City code', default=0)
    name_ru = models.CharField(max_length=255, verbose_name='City name (russian)')
    name_en = models.CharField(max_length=255, verbose_name='City name (english)')

    def __str__(self):
        return self.name_en

def get_country_default_id():
    return Country.objects.all().first().id

class NotExistRegion(models.Model):
    class Meta:
        verbose_name = 'Nonexistent region'
        verbose_name_plural = 'Nonexistent regions'

    country = models.ForeignKey(Country, verbose_name='Country', default=get_country_default_id)
    code = models.CharField(max_length=2, verbose_name='Region code', default=0)
    name_en = models.CharField(max_length=255, verbose_name='Region name (english)')

    def __str__(self):
        return self.name_en

    def name_ru(self):
        return ''


def get_region_default_id():
    return ContentType.objects.get_for_model(Region).id


class NotExistCity(models.Model):
    class Meta:
        verbose_name = 'Nonexistent city'
        verbose_name_plural = 'Nonexistent cities'

    REGION_CHOICE = models.Q(app_label='geodata', model='region') | models.Q(app_label='geodata', model='notexistregion')

    content_type = models.ForeignKey(
        ContentType,
        on_delete=models.CASCADE,
        default=get_region_default_id,
        limit_choices_to=REGION_CHOICE
    )

    object_id = models.PositiveIntegerField(default=0)
    region = GenericForeignKey('content_type', 'object_id')
    code = models.CharField(max_length=2,verbose_name='City code', default=0)
    name_en = models.CharField(max_length=255, verbose_name='City name (english)')

    def __str__(self):
        return self.name_en

    def name_ru(self):
        return ''


