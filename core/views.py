# -*- coding: utf-8 -*-
from django.conf import settings
from django.contrib.auth.models import User
from django.contrib.sessions.models import Session
from django.core.cache import cache
from django.core.mail import send_mail
from django.core.exceptions import ValidationError
from django.core.validators import validate_email
from django.contrib.auth import authenticate, login, logout, password_validation
from django.db.models import Q

from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.authtoken.models import Token

from random import choice
from string import digits, ascii_letters
from datetime import datetime

from userdata.models import Confirmation, ProfileBusiness, FileForProfile
from core.models import ResetPassword, CountryNumberphone
from core.tools import gen_url_with_keys_email, token_renew, photo_business_upload
from geodata.models import Country, Region, City


@api_view(['POST'])
def sign_in(request):
    """
    :param request:
    {
        "username": "Buyer",
        "password": "123qwe123qwe",
        "remember_me": true
    }
    :return:
    """
    username = request.data.get('username', False)  # username or email
    password = request.data.get('password', False)
    remember_me = request.data.get('remember_me', False)

    if request.user.is_authenticated():
        return Response({'error': 'you are already signed in'}, status=400)

    if not username:
        return Response({'error': 'empty username'}, status=400)
    if not password:
        return Response({'error': 'empty password'}, status=400)

    try:
        u = User.objects.get(email=username)
    except User.DoesNotExist:
        pass
    else:
        username = u.username

    user = authenticate(
        username=username,
        password=password
    )

    if user is not None:
        login(request, user)
        if remember_me: request.session.set_expiry(1209600)
        token, created = Token.objects.get_or_create(user=user)

        if created:token.save()
        return Response({"token": token.key})
    else:
        return Response({"error": "incorrect data"}, status=400)


@api_view(['GET'])
def sign_out(request):
    logout(request)
    return Response({"status": "ok"})


@api_view(['GET'])
def check_auth(request):
    user = request.user
    if user.is_authenticated():
        key = str(user.id)
        use_prof = cache.get(key, False)
        if not use_prof:
            cache.set(key, 'personal', None)
            use_prof = 'personal'
        try:
            bus_prof = bool(user.profile.profilebusiness)
            business_confirmed = bool(user.profile.profilebusiness.confirmed_profile_bus)
            if not business_confirmed: use_prof = 'personal'
        except ProfileBusiness.DoesNotExist:
            bus_prof = False
            business_confirmed = False
            use_prof = 'personal'

        out_vars = {
            'is_business': bus_prof,
            'business_confirmed': business_confirmed,
            'profile': use_prof
        }

        return Response(out_vars)
    else:
        return Response({"error": "not authenticated"}, status=401)


@api_view(['GET'])
@permission_classes((IsAuthenticated,))
def logout_from_all_devices(request):
    user = request.user

    [s.delete() for s in Session.objects.all() if s.get_decoded().get('_auth_user_id') == str(user.id)]

    token = token_renew(user)

    return Response({'token': token})


@api_view(['GET'])
@permission_classes((IsAuthenticated,))
def change_profile(request):
    user = request.user
    key = str(user.id)
    try:
        bus_prof = user.profile.profilebusiness
        if not bus_prof.confirmed_profile_bus:
            bus_prof = False
    except ProfileBusiness.DoesNotExist:
        bus_prof = False
    act = cache.get(key, False)
    if not act:
        cache.set(key, 'personal', None)
        prof = 'personal'
    else:
        if act == 'personal' and bus_prof:
            cache.set(key, 'business', None)
            prof = 'business'
        elif act == 'personal' and not bus_prof:
            prof = 'personal'
        elif act == 'business':
            cache.set(key, 'personal', None)
            prof = 'personal'

    out_vars = {
        'use_profile': prof
    }

    return Response(out_vars)


@api_view(['POST'])
@permission_classes((IsAuthenticated,))
def upgrade_profile_to_business(request):
    '''
    :param request:
    {
        "terms_of_use": bool,
        "type_of_business": int,
        "organization_type": int,
        "organization_name": "",
        "vat": "",
        "registration_number": "",
        "first_name": "",
        "middle_name": "",
        "last_name": "",
        "position": "",
        "code_number_phone": int,
        "phone_number": "",
        "email": email,
        "addition_receiver": "",
        "receiver_phonenumber": ""
    }
    :return:
    '''
    user = request.user

    terms_of_use = request.data.get('terms_of_use', None)
    type_of_business = request.data.get('type_of_business', False)
    organization_type = request.data.get('organization_type', False)
    organization_name = request.data.get('organization_name', False)
    vat = request.data.get('vat', False)
    registration_number = request.data.get('registration_number', False)
    first_name = request.data.get('first_name', False)
    middle_name = request.data.get('middle_name', False)
    last_name = request.data.get('last_name', False)
    position = request.data.get('position', False)
    code_number_phone = request.data.get('code_number_phone', False)
    phone_number = request.data.get('phone_number', False)
    email = request.data.get('email', False)
    addition_receiver = request.data.get("addition_receiver", False)
    receiver_phonenumber = request.data.get("receiver_phonenumber", False)

    photos = request.data.get('photos', False)

    bus_prof_exist = False

    if type(terms_of_use) != bool:
        return Response({'error': 'Incorrect type terms_of_use (need bool)'}, status=400)
    if not terms_of_use:
        return Response({'error': 'You should agree with terms of use'}, status=400)
    if not type_of_business:
        return Response({'error': 'Empty type of business'}, status=400)
    if type(type_of_business) != int:
        return Response({'error', 'Incorrect type type_of_business (need int)'}, status=400)
    if not organization_type:
        return Response({'error': 'Empty organization information'}, status=400)
    if type(organization_type) != int:
        return Response({'error': 'Incorrect type organization_type (need int)'}, status=400)
    if not organization_name:
        return Response({'error': 'Empty organization name'}, status=400)
    if type(organization_name) != str:
        return Response({'error': 'incorrect type organization_name (need str)'}, status=400)
    if not vat:
        return Response({'error': 'Empty vat'}, status=400)
    if type(vat) != str:
        return Response({'error': 'Incorrect type vat (need str)'}, status=400)
    if not registration_number:
        return Response({'error': 'Empty registration number'}, status=400)
    if type(registration_number) != str:
        return Response({'error':'incorrect type registration_number (need str)'}, status=400)
    if not first_name:
        return Response({'error': 'Empty first name'}, status=400)
    if type(first_name) != str:
        return Response({'error':'Incorrect type first_name (need str)'}, status=400)
    if not last_name:
        return Response({'error': 'Empty last name'}, status=400)
    if type(last_name) != str:
        return Response({'error':'Incorrect type last_name (need str)'}, status=400)
    if not position:
        return Response({'error': 'Empty position'}, status=400)
    if type(position) != str:
        return Response({'error':'Incorrect type position (need str)'}, status=400)
    if not code_number_phone:
        return Response({'error': 'Empty code_number_phone'}, status=400)
    if type(code_number_phone) != int:
        return Response({'error': 'Incorrect type code_number_phone (need int)'}, status=400)
    if not phone_number:
        return Response({'error': 'Empty phonenumber'}, status=400)
    if type(phone_number) != int:
        return Response({'error': 'Incorrect type phone_number (need int)'}, status=400)
    if not email:
        return Response({'error': 'Empty email'}, status=400)
    if type(email) != str:
        return Response({'error':'Incorrect type email (need str)'}, status=400)
    if middle_name and type(middle_name) != str:
        return Response({'error': 'incorrect type middle_name (need str)'}, status=400)

    types_of_bus = list(map(lambda x: x[0], ProfileBusiness.TYPE_BUSINESS))

    if not type_of_business in types_of_bus:
        return Response({'error':'Incorrect type of business'}, status=400)

    organ_types = list(map(lambda x: x[0], ProfileBusiness.ORGANIZATION_TYPE))

    if not organization_type in organ_types:
        return Response({'error':'Incorrect type of organization'}, status=400)

    try:
        validate_email(email)
    except ValidationError:
        return Response({'error': 'Incorrect email'}, status=400)

    try:
        num_code = CountryNumberphone.objects.get(id=code_number_phone)
    except CountryNumberphone.DoesNotExist:
        return Response({'error': 'incorrect code_number_phone'}, status=400)

    try:
        prof = user.profile.profilebusiness
    except ProfileBusiness.DoesNotExist:
        pass
    else:
        bus_prof_exist = True
        prof.terms_of_use = terms_of_use
        prof.type_of_business = type_of_business
        prof.organization_type = organization_type
        prof.organization_name = organization_name
        prof.vat = vat
        prof.registration_number = registration_number
        prof.first_name = first_name
        prof.middle_name = middle_name
        prof.last_name = last_name
        prof.position_in_com = position
        prof.code_num_phone = num_code
        prof.phone_number = phone_number
        prof.email = email
        prof.confirmed_profile = False
        prof.addition_receiver = addition_receiver
        prof.receiver_phonenumber = receiver_phonenumber

        prof.save()

    if not bus_prof_exist:
        # if not photos:
        #     return Response({'error': 'Empty photos'}, status=400)

        prof = ProfileBusiness(
            profile = user.profile,
            terms_of_use = terms_of_use,
            type_of_business = type_of_business,
            organization_type = organization_type,
            organization_name = organization_name,
            vat = vat,
            registration_number = registration_number,
            first_name = first_name,
            middle_name = middle_name,
            last_name = last_name,
            position_in_com = position,
            code_num_phone = num_code,
            phone_number = phone_number,
            email = email,
            addition_receiver = addition_receiver,
            receiver_phonenumber = receiver_phonenumber
        )
        prof.save()

    # if photos:
    #     for p in photos:
    #         photo = photo_business_upload(p, prof.id)
    #         ph = FileForProfile.objects.create(
    #             user=user,
    #             type_profile=2,
    #             for_confirmation=True,
    #             img=photo
    #         )
    #         ph.save()

    return Response({'status': 'ok'})


@api_view(['POST'])
def send_msg_reset_password(request):
    '''
    :param request:
    {
        "email": str
    }
    :return:
    '''
    email = request.data.get('email')

    if not email:
        return Response({'error': 'Empty email'}, status=400)

    try:
        user = User.objects.get(email=str(email))
    except User.DoesNotExist:
        return Response({'error': 'User with such email not found'}, status=400)

    key = ''.join(choice(digits + ascii_letters) for i in range(25))
    try:
        ResetPassword(
            key=key,
            email=email,
        ).save()
    except:
        return Response({'error': 'system error'}, status=400)
    data = 'email={0}&key={1}'.format(email, key)
    url = ''.join((
        settings.ALLOWED_HOSTS[0],
        '/core/reset_password?',
        data
    ))

    try:
        send_mail(
            'Reset password',
            '\n'.join(('Please click url to change your password', url, 'Thank you!')),
            settings.EMAIL_HOST_USER,
            [email]
        )
    except:
        return Response({'error': 'Message was not sent'}, status=400)

    return Response({'status': 'ok'})


@api_view(['POST'])
@permission_classes((IsAuthenticated,))
def gen_email_confirmation(request):
    user = request.user
    email = request.data.get('email', False)

    if not email:
        email = user.email
    else:
        if email != user.email:
            try:
                validate_email(email)
            except ValidationError:
                return Response({'error': 'incorrect email'}, status=400)
            try:
                User.objects.get(email=email)
            except User.DoesNotExist:
                pass
            else:
                return Response({'error': 'this email already exist'}, status=400)

    if email == user.email and user.profile.confirmed_email:
        return Response({'error': 'email already confirmed'}, status=400)

    url, key = gen_url_with_keys_email(email, 'email-confirm')

    conf, created = Confirmation.objects.get_or_create(
        user=user,
        email=True,
        phone=False
    )
    conf.key = key
    conf.e_mail = email
    conf.conf = False
    conf.save()

    try:
        send_mail(
            'Verification email',
            '\r\n'.join(('Please click url to confirm your email', url, 'Thank you!')),
            settings.EMAIL_HOST_USER,
            [email]
        )
    except:
        return Response({'error': 'Message could not be sent'}, status=400)

    return Response({'status': 'ok'})


@api_view(['POST'])
@permission_classes((IsAuthenticated,))
def confirm_email(request):
    user = request.user
    email = request.data.get('email', False)
    key = request.data.get('key', False)

    if email and key:
        try:
            conf_email = Confirmation.objects.get(user=user, email=True)
        except Confirmation.DoesNotExist:
            return Response({'error': 'User has not confirmation key for email'}, status=400)
        if key == conf_email.key and email == conf_email.e_mail and not conf_email.conf:
            user.email = email
            user.save()

            user.profile.confirmed_email = True
            user.profile.save()

            conf_email.conf = True
            conf_email.save()

            return Response({'status': 'ok'})

        elif key == conf_email.key and email == conf_email.e_mail and conf_email.conf:
            return Response({'error': 'Email has already confirmed'}, status=400)

        else:
            return Response({'error': 'Email and key are incorrect'}, status=400)
    else:
        return Response({'error': 'Empty email or key'}, status=400)


@api_view(['GET'])
@permission_classes((IsAuthenticated,))
def gen_sms(request):
    user = request.user
    phonenumber = User.objects.get(username=user).phonenumber
    key = ''.join(choice(digits) for i in range(6))

    conf, created = Confirmation.objects.get_or_create(
        user=user,
        key=key,
        phone=True,
        email=False
    )
    conf.key = key
    conf.save()
    # отправка смс
    return Response({'status': 'ok'})


@api_view(['GET'])
@permission_classes((IsAuthenticated,))
def check_numberphone(request):
    user = request.user
    key = request.query_params.get('key', False)

    if key:

        try:
            conf_phone = Confirmation.objects.get(user=user, phone=True)
        except Confirmation.DoesNotExist:
            return Response({'error': 'User has not such numberphone'}, status=400)

        if key == conf_phone.key:
            user.profile.confirmed_phone = True
            user.profile.save()
            return Response({'status': 'ok'})
        else:
            return Response({'error': 'Key is wrong'}, status=400)
    else:
        return Response({'error': 'Empty key'}, status=400)


@api_view(['POST'])
def gen_email_reset_password(request):
    email = request.data.get('email', False)

    if not email:
        return Response({'error': 'Empty email'}, status=400)

    try:
        user = User.objects.get(email=email)
    except User.DoesNotExist:
        return Response({'error': 'Incorrect email'}, status=400)

    url, key = gen_url_with_keys_email(email, 'reset_password')

    rp, created = ResetPassword.objects.get_or_create(
        email = email
    )
    rp.key = key
    rp.email = email
    rp.save()

    try:
        send_mail(
            'Reset password',
            '\r\n'.join(('Please click url to reset your password', url, 'Thank you!')),
            settings.EMAIL_HOST_USER,
            [email]
        )
    except:
        return Response({'error': 'Message could not be sent'}, status=400)

    return Response({'status': 'ok'})


@api_view(['POST'])
def reset_password(request):
    email = request.data.get('email', False)
    key = request.data.get('key', False)
    password = request.data.get('password', False)

    if not email:
        return Response({'error': 'Empty email'}, status=400)
    if not key:
        return Response({'error': 'Empty key'}, status=400)
    if not password:
        return Response({'error': 'Empty password'}, status=400)

    try:
        rp = ResetPassword.objects.get(key=key,email=email)
    except ResetPassword.DoesNotExist:
        return Response({'error': 'Incorrect email or key'}, status=400)

    rp.delete()

    try:
        user = User.objects.get(email=email)
    except User.DoesNotExist:
        return Response({'error': 'User not found'}, status=400)

    password_1 = password.get('first', False)
    password_2 = password.get('second', False)

    if not password_1 or not password_2:
        return Response({'error': 'Incorrect password'}, status=400)
    if password_1 == password_2 and type(password_1) == str and len(password_1) > 8:
        try:
            user.set_password(password_1)
        except:
            return Response({'error': 'Incorrect password'}, status=400)
        user.save()

        user.profile.password_updated = datetime.now()
        user.profile.save()

        login(request, user)
        token = token_renew(user)

        return Response({"token": token})

    else:
        return Response({'error': 'Incorrect password'}, status=400)


@api_view(['POST'])
def create_account(request):
    email = request.data.get('email', False)
    password = request.data.get('password', False)
    first_name = request.data.get('first_name', False)
    middle_name = request.data.get('middle_name', False)
    last_name = request.data.get('last_name', False)
    code_phone = request.data.get('code_id', False)
    num_phone = request.data.get('number_phone', False)
    check = request.data.get('check', None)

    if not email:
        return Response({'error': 'Empty email'}, status=400)
    if type(email) != str:
        return Response({'error': 'Incorrect type email (need str)'}, status=400)
    if not password:
        return Response({'error': 'Empty password'}, status=400)
    if type(password) != dict:
        return Response({'error': 'Incorrect type password (need dict)'}, status=400)
    if not first_name:
        return Response({'error': 'Empty first name'}, status=400)
    if type(first_name) != str:
        return Response({'error': 'Incorrect type first_name (need str)'}, status=400)
    if not last_name:
        return Response({'error': 'Empty last name'}, status=400)
    if type(last_name) != str:
        return Response({'error': 'Incorrect type last_name (need str)'}, status=400)
    if not check:
        return Response({'error': 'You should agree with rools'}, status=400)

    if middle_name and type(middle_name) != str:
        return Response({'error': 'Incorrect type middle_name (need str)'}, status=400)
    if code_phone and type(code_phone) != int:
        return Response({'error': 'Incorrect type code_id (need int)'}, status=400)
    if num_phone and type(num_phone) != int:
        return Response({'error': 'Incorrect type number_phone (need int)'}, status=400)


    username_flag = False

    while username_flag == False:

        username = email.split('@')[0] + '_' + ''.join(choice(digits) for i in range(10))
        if User.objects.filter(username=username).count() == 0:
            username_flag = True

    password_1 = password.get('first', False)
    password_2 = password.get('second', False)

    if not password_1 or not password_2:
        return Response({'error': 'Empty piece of passwords'}, status=400)

    try:
        validate_email(email)
    except ValidationError:
        return Response({'error': 'Incorrect email'}, status=400)
    users = User.objects.filter(email=email).exists()
    if not users:
        if code_phone:
            try:
                code = CountryNumberphone.objects.get(id=code_phone)
            except CountryNumberphone.DoesNotExist:
                return Response({'error': 'Incorrect code_id'}, status=400)
        if password_1 == password_2 and type(password_1) == str:
            try:
                password_validation.validate_password(password_1)
            except ValidationError as e:
                return Response({'error': e}, status=400)
            try:
                user = User.objects.create_user(
                    username=username,
                    email=email,
                    password=password_1
                )
            except Exception as e:
                return Response({'error': e}, status=400)
            else:
                user.first_name = first_name
                user.last_name = last_name
                user.save()

                if num_phone and code_phone:
                    user.profile.code_num_phone = code
                    user.profile.number_phone = num_phone

                if middle_name:

                    user.profile.middle_name = middle_name

                user.profile.password_updated = user.date_joined

                user.profile.save()

                token, created = Token.objects.get_or_create(user=user)
                if created:
                    token.save()

                return Response({"token": token.key})
        else:
            return Response({'error': 'Passwords are incorrect'}, status=400)
    else:
        return Response({'error': 'Email already exists'}, status=400)


@api_view(['GET'])
def get_countries(request):
    def form_json(obj):
        country[obj.id] = {
            'code': obj.code,
            'name_en': obj.name_en
        }

    country = {}

    list(map(form_json, Country.objects.filter(show=True)))

    out_vars = {
        'countries': country
    }

    return Response(out_vars)


@api_view(['GET'])
def get_regions(request):
    def form_json(obj):
        region[obj.id] = {
            'country': obj.country.id,
            'code': obj.code,
            'name_en': obj.name_en
        }

    region = {}

    list(map(form_json, Region.objects.filter(country__show=True)))

    out_vars = {
        'regions': region
    }

    return Response(out_vars)


@api_view(['GET'])
def get_country_groups(request):
    out_vars = sorted([{"group": c.group,
                 "country_id": c.id,
                 "country_name": c.name_en} for c in Country.objects.filter(~Q(group=0))], key=lambda c: c['group'])
    return Response(out_vars)


@api_view(['GET'])
def get_cities(request):
    def form_json(obj):
        city[obj.id] = {
            'country': obj.region.country.id,
            'code': obj.code,
            'name_en': obj.name_en
        }

    city = {}

    list(map(form_json, City.objects.filter(region__country__show=True)))

    out_vars = {
        'cities': city
    }

    return Response(out_vars)


@api_view(['POST'])
def autocomplete_country(request):
    '''
    :param request:
    {
        "country": ""
    }
    :return:
    '''
    country = request.data.get('country', '')

    if type(country) != str:
        return Response({'error': 'Incorrect type country (need str)'}, status=400)

    out_vars = {
        'countries': list(map(
            lambda x: {'id': x.id, 'name_en': x.name_en},
            Country.objects.filter(show=True, name_en__istartswith=country)[:10]
        ))
    }

    return Response(out_vars)


@api_view(['POST'])
def autocomplete_region(request):
    '''
    :param request:
    {
        "country_id": 73,
        "region": ""
    }
    :return:
    '''
    country = request.data.get('country_id', False)
    region = request.data.get('region', '')

    if type(region) != str:
        return Response({'error': 'incorrect type region (need str)'}, status=400)
    if country and type(country) != int:
        return Response({'error': 'incorrect type country_id (need int)'}, status=400)
    if country:
        out_vars = {
            'regions': list(map(
                lambda x: {'id': x.id, 'name_en': x.name_en},
                Region.objects.filter(
                    country__show=True, country_id=country, name_en__istartswith=region)[:10]
            ))
        }
    else:
        out_vars = {
            'regions': list(map(
                lambda x: {'id': x.id, 'name_en': x.name_en},
                Region.objects.filter(
                    country__show=True, name_en__istartswith=region
                )[:10]
            ))
        }

    return Response(out_vars)


@api_view(['POST'])
def autocomplete_city(request):
    '''
    :param request:
    {
        "country_id": 73,
        "region_id": 485,
        "city": ""
    }
    :return:
    '''
    country = request.data.get('country_id', 0)
    region = request.data.get('region_id', 0)
    city = request.data.get('city', '')

    if type(city) != str:
        return Response({'error': 'Incorrect type city (need str)'}, status=400)
    if country and type(country) != int:
        return Response({'error': 'Incorrect type country_id (need int)'}, status=400)
    if region and type(region) != int:
        return Response({'error': 'Incorrect type region_id (need int)'}, status=400)
    if region:
        out_vars = {
            'cities': list(map(
                lambda x: {'id': x.id, 'name_en': x.name_en},
                City.objects.filter(
                    region__country__show=True, region_id=region, name_en__istartswith=city
                )[:10]
            ))
        }
    elif country:
        out_vars = {
            'cities': list(map(
                lambda x: {'id': x.id, 'name_en': x.name_en},
                City.objects.filter(
                    region__country__show=True, region__country_id=country, name_en__istartswith=city
                )[:10]
            ))
        }
    else:
        out_vars = {
            'cities': list(map(
                lambda x: {'id': x.id, 'name_en': x.name_en},
                City.objects.filter(
                    region__country__show=True, name_en__istartswith=city
                )[:10]
            ))
        }

    return Response(out_vars)

