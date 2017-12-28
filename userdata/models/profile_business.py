from django.core.exceptions import ValidationError
from django.db import models
import os
from django.conf import settings

from core.models import CountryNumberphone
from userdata.models.profile import Profile


def bp_directory_path(instance, filename):
    return os.path.join(settings.AVATAR_BUSINESS_URL, str(instance.id), filename)

def ab_directory_path(instance, filename):
    return os.path.join(settings.ABOUT_BUSINESS_URL, str(instance.id), filename)


class ProfileBusiness(models.Model):
    class Meta:
        verbose_name = 'Business profile'
        verbose_name_plural = 'Business profiles'

    ORGANIZATION_TYPE = (
        (1, 'self-employed'),
        (2, 'Limited Liablility Company (LLC or LTD)'),
        (3, 'Open Joint Stock Company (OJSC)'),
        (4, 'Close Joint Stock Company (CJSC)')
    )

    TYPE_BUSINESS = (
        (1, 'farmer'),
        (2, 'recycler'),
    )
    IMG_COUNT = 10

    profile = models.OneToOneField(Profile)
    terms_of_use = models.BooleanField(default=False)   #согласие с условиями
    type_of_business = models.PositiveSmallIntegerField(choices=TYPE_BUSINESS, default=1)
    organization_type = models.PositiveSmallIntegerField(choices=ORGANIZATION_TYPE, default=1)
    organization_name = models.CharField(max_length=256)
    vat = models.CharField(max_length=256)
    registration_number = models.CharField(max_length=256)
    first_name = models.CharField(max_length=50)
    middle_name = models.CharField(max_length=50, blank=True, null=True)
    last_name = models.CharField(max_length=50)
    position_in_com = models.CharField(max_length=50)
    code_num_phone = models.ForeignKey(CountryNumberphone, blank=True, null=True)
    phone_number = models.BigIntegerField(blank=True, null=True)
    email = models.EmailField()
    about_me = models.TextField(blank=True, null=True)
    about_me_eng = models.TextField(blank=True, null=True)
    avatar = models.ImageField(blank=True, null=True, upload_to=bp_directory_path)
    confirmed_profile_bus = models.BooleanField(default=False)
    addition_receiver = models.TextField(blank=True, null=True, max_length=100)
    receiver_phonenumber = models.BigIntegerField(blank=True, null=True)

    def __str__(self):
        return self.profile.user.username


class AboutBusiness(models.Model):
    class Meta:
        verbose_name = 'About me page'
        verbose_name_plural = 'About me pages'

    profile = models.OneToOneField(ProfileBusiness)
    title = models.CharField(max_length=256, blank=True, null=True)
    text = models.TextField(blank=True, null=True)
    video = models.URLField(blank=True, null=True)

    def __str__(self):
        return self.profile.profile.user.username


class PhotoAboutBusiness(models.Model):
    class Meta:
        verbose_name = 'About me image'
        verbose_name_plural = 'About me images'

    about_business = models.ForeignKey(AboutBusiness)
    photo = models.ImageField(blank=True, null=True, upload_to=ab_directory_path)

    def clean(self):
        cleaned_data = super(PhotoAboutBusiness, self).clean()
        if self._state.adding and PhotoAboutBusiness.objects.filter(photo=self.photo).count() >= ProfileBusiness.IMG_COUNT:
            raise ValidationError('You can attach only {0} pictures to the business account!'.format(ProfileBusiness.IMG_COUNT))

        return cleaned_data

    def save(self):
        self.clean()
        super(PhotoAboutBusiness, self).save()

