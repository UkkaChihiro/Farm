from django.conf.urls import url
from .views import *


urlpatterns = [
    url(r'^check_auth/', check_auth, name='check_auth'),
    url(r'^sign_in/$',sign_in, name='sign_in'),
    url(r'^sign_out/$', sign_out, name='sign_out'),
    url(r'^logout_from_all_devices/$', logout_from_all_devices, name='logout_from_all_devices'),
    url(r'^change_profile/$', change_profile, name='change_profile'),
    url(r'^create_account/$', create_account, name='create_account'),
    url(r'^gen_email_confirmation/$', gen_email_confirmation, name='gen_email_confirmation'),
    url(r'^confirm_email/$', confirm_email, name='confirm_email'),
    url(r'^gen_email_reset_password/$', gen_email_reset_password, name='gen_email_reset_password'),
    url(r'^reset_password/$', reset_password, name='reset_password'),
]
