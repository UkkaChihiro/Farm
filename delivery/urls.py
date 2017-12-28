from django.conf.urls import url
from .views import *


urlpatterns = [
    url(r'^add_tariff_for_country/$', add_tariff_for_country, name='add_tariff_for_country'),
    url(r'^add_tariff_for_group/$', add_tariff_for_group, name='add_tariff_for_group'),
    url(r'^delete_tariff_for_country/$', delete_tariff_for_country, name='delete_tariff_for_country'),
    url(r'^get_tariff_for_country/$', get_tariff_for_country, name='get_tariff_for_country'),
    url(r'^get_tariff_for_group/$', get_tariff_for_group, name='get_tariff_for_group'),
    url(r'^get_group_of_countries/$', get_group_of_countries, name='get_group_of_countries'),
    url(r'^add_tariff_for_product/$', add_tariff_for_product, name='add_tariff_for_product'),
    url(r'^get_tariff_for_product/$', get_tariff_for_product, name='get_tariff_for_product'),
]