import os

from django.contrib.auth.models import User
from django.db import models
from django.conf import settings
from rest_framework.authtoken.models import Token

from django.db.models.signals import post_save
from django.dispatch import receiver

from core.models import CountryNumberphone, Language


@receiver(post_save, sender=User)
def create_auth_token(sender, instance=None, created=False, **kwargs):
    if created:
        Token.objects.create(user=instance)


@receiver(post_save, sender=User)
def save_profile(sender, instance, **kwargs):
    profile, created = Profile.objects.get_or_create(user=instance)
    if created:
        profile.save()


def pp_directory_path(instance, filename):
    return os.path.join(settings.AVATAR_PERSONAL_URL, str(instance.id), filename)


class Profile(models.Model):
    class Meta:
        verbose_name = 'Personal profile'
        verbose_name_plural = 'Personal profiles'

    GENDER = (
        (1, 'not set'),
        (2, 'male'),
        (3, 'female'),
    )

    user = models.OneToOneField(User)
    middle_name = models.CharField(max_length=30, blank=True, null=True)
    gender = models.PositiveSmallIntegerField(choices=GENDER, default=1)
    birthday = models.DateField(blank=True, null=True)
    avatar = models.ImageField(blank=True, null=True, upload_to=pp_directory_path)
    code_num_phone = models.ForeignKey(CountryNumberphone, blank=True, null=True)
    number_phone = models.BigIntegerField(blank=True, null=True)
    tax_number = models.CharField(max_length=256, blank=True, null=True)
    confirmed_email = models.BooleanField(default=False)
    confirmed_phone = models.BooleanField(default=False)
    about_me = models.TextField(blank=True, null=True)
    about_me_eng = models.TextField(blank=True, null=True)
    language = models.ForeignKey(Language, default=1)
    confirmed_profile = models.BooleanField(default=False)
    password_updated = models.DateTimeField(null=True)
    personal_offers_email = models.BooleanField(default=False)
    newsletter_email = models.BooleanField(default=False)
    #new_message_email = models.BooleanField(default=False)
    #new_message_msg = models.BooleanField(default=False)
    #payment_success_email = models.BooleanField(default=False)
    #payment_success_msg = models.BooleanField(default=False)
    #order_fail_email = models.BooleanField(default=False)
    #order_fail_msg = models.BooleanField(default=False)
    #delivery_start_email = models.BooleanField(default=False)
    #delivery_start_msg = models.BooleanField(default=False)
    addition_receiver = models.TextField(blank=True, null=True, max_length=100)
    receiver_phonenumber = models.BigIntegerField(blank=True, null=True)

    def __str__(self):
        return self.user.username


class Confirmation(models.Model):
    user = models.ForeignKey(User)
    key = models.CharField(max_length=50)
    e_mail = models.EmailField()
    conf = models.BooleanField(default=False)
    email = models.BooleanField(default=False)
    phone = models.BooleanField(default=False)
    created = models.DateTimeField(auto_now=True, blank=True)


class ClassProductForProfile(models.Model):
    class Meta:
        unique_together = ("name", "profile")

    CLASS_PROD = (
        (1, 'Halal'),
        (2, 'Kosher'),
        (3, 'Vegetarian'),
        (4, 'Vegan'),
        (5, 'BIO'),
        (6, 'Lactose Free'),
        (7, 'Gluten Free'),
        (8, 'Allergen Free')
    )

    name = models.SmallIntegerField(choices=CLASS_PROD)
    profile = models.ForeignKey(Profile)


class FileForProfile(models.Model):
    TYPE_PROFILE = (
        (1, 'personal'),
        (2, 'business'),
    )

    user = models.ForeignKey(User)
    type_profile = models.PositiveSmallIntegerField(choices=TYPE_PROFILE, default=1)
    for_confirmation = models.BooleanField(default=False)
    img = models.ImageField()
    created = models.DateTimeField(auto_now_add=True)
