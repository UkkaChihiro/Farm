from django.contrib.auth.backends import ModelBackend
from django.contrib.auth.models import User
from django.contrib.auth import get_user_model
from django.core.cache import cache

from rest_framework.authentication import SessionAuthentication




# authenticated_user_cache = 'authenticated_user:{0}'
#
#
# def get_authenticated_user_from_cache(user_id):
#     cached_authenticated_user_key = authenticated_user_cache.format(user_id,)
#
#     return cache.get(cached_authenticated_user_key)
#
#
# def set_authenticated_user_to_cache(user):
#     cached_authenticated_user_key = authenticated_user_cache.format(user.pk,)
#
#     cache.set(cached_authenticated_user_key, user, None)


class CsrfExemptSessionAuthentication(SessionAuthentication):

    def enforce_csrf(self, request):
        return


class CustomBackend(ModelBackend):
    def authenticate(self, username=None, password=None):
        try:
            user = User.objects.get(email=username)
            if user.check_password(password):
                return user
            else:
                return None
        except User.DoesNotExist:
            pass
        try:
            user = User.objects.get(username=username)
            if user.check_password(password):
                return user
            else:
                return None
        except User.DoesNotExist:
            return None

    def get_user(self, user_id):
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None