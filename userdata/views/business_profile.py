# -*- coding: utf-8 -*-
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated

from datetime import datetime

from catalog.tools import sintez_json_from_product
from core.models import CountryNumberphone
from core.permissions import IsBusiness
from core.tools import about_business_upload, avatar_business_upload
from userdata.models import AddressPickUp, AboutBusiness, PickUpWorkTime, PhotoAboutBusiness, FileForProfile

from catalog.models import BestProduct, Product

from rest_framework.status import HTTP_200_OK

from userdata.tools import *


@api_view(['GET'])
@permission_classes((IsAuthenticated, IsBusiness, ))
def dashboard_business(request):
    profile_business = request.user.profile.profilebusiness
    # print(dir(profile_business.avatar))

    if profile_business.avatar and hasattr(profile_business.avatar, 'url'):
        avatar = profile_business.avatar.url
    else:
        avatar = None

    try:
        number_phone = "+%s%s" % (profile_business.code_num_phone.code, profile_business.phone_number)
    except AttributeError:
        number_phone = ''

    out_vars = {
        "id": profile_business.id,
        "type_of_business": profile_business.type_of_business,
        "organization_type": profile_business.organization_type,
        "organization_name": profile_business.organization_name,
        "vat": profile_business.vat,
        "registration_number": profile_business.registration_number,
        "first_name": profile_business.first_name,
        "last_name": profile_business.last_name,
        "middle_name": profile_business.middle_name,
        "position": profile_business.position_in_com,
        "phone_number": profile_business.phone_number,
        "code_number_phone": profile_business.code_num_phone.id if profile_business.code_num_phone else False,
        "code_phone_value": '+%s' % profile_business.code_num_phone.code if profile_business.code_num_phone else '',
        "email": profile_business.email,
        "about_me": profile_business.about_me,
        "about_me_eng": profile_business.about_me_eng,
        "avatar": avatar,
        "addition_receiver": profile_business.addition_receiver,
        "receiver_phonenumber": profile_business.receiver_phonenumber,
    }

    return Response(out_vars)


@api_view(['POST'])
@permission_classes((IsAuthenticated, IsBusiness, ))
def add_product_to_my_best_products(request):
    """
    :param request:
    {
        "product_id": 1
    }
    :return:
    """
    product_id = request.data.get("product_id", 0)

    product = Product.objects.filter(profile_business=request.user.profile.profilebusiness,
                                     id=product_id).first()
    if not product_id:
        return Response({'error': 'Incorrect product id'}, status=400)

    count = BestProduct.objects.filter(seller=request.user.profile.profilebusiness).count()

    if count > 10:
        return Response({"error": "You already have 10 best products"})

    best_prod, created = BestProduct.objects.get_or_create(seller=request.user.profile.profilebusiness,
                                                           product=product)
    if created:
        best_prod.save()

    return Response(HTTP_200_OK)


@api_view(['POST'])
@permission_classes((IsAuthenticated, IsBusiness, ))
def delete_product_from_my_best_products(request):
    """
    :param request:
    {
        "product_id": 1
    }
    :return:
    """
    product_id = request.data.get("product_id", 0)

    best_prod = BestProduct.objects.filter(seller=request.user.profile.profilebusiness, product_id=product_id)

    if best_prod:
        best_prod.delete()
        return Response(HTTP_200_OK)

    return Response({"error": "Incorrect product id"}, status=400)


@api_view(['GET'])
@permission_classes((IsAuthenticated, IsBusiness, ))
def get_all_my_best_products(request):
    best_prods = [sintez_json_from_product(bp.product) for bp in BestProduct.objects.filter(seller=request.user.profile.profilebusiness)]

    return Response(best_prods)


@api_view(['POST'])
def get_farmers_best_products(request):
    """
    :param request:
    {
        "businessprofile_id": 1
    }
    :return:
    """
    businessprofile_id = request.data.get('businessprofile_id', 0)
    best_prods = [sintez_json_from_product(bp.product) for bp in BestProduct.objects.filter(seller=businessprofile_id)]

    return Response(best_prods)


@api_view(['POST'])
@permission_classes((IsAuthenticated, IsBusiness, ))
def add_or_update_about_me(request):
    '''
    :param request:
    {
        "title": "",
        "text": "",
        "video_url": "https://www.google.ru/"
    }
    :return:
    HTTP_200_OK
    '''
    business_profile = request.user.profile.profilebusiness

    title = request.data.get('title')
    text = request.data.get('text')
    video = request.data.get('video_url')

    if not title and not text:
        return Response({'error': 'Empty title or text'}, status=400)

    about, created = AboutBusiness.objects.get_or_create(profile=business_profile)
    about.title = title
    about.text = text
    about.video = video
    about.save()

    return Response({"business_profile": business_profile.id,
                     "title": about.title,
                     "text": about.text,
                     "video": about.video})


@api_view(['GET'])
@permission_classes((IsAuthenticated, IsBusiness, ))
def delete_about_me(request):
    '''
    :param request:
    :return:
    HTTP_200_OK
    '''
    business_profile = request.user.profile.profilebusiness

    about = AboutBusiness.objects.filter(profile=business_profile)
    about.delete()

    return Response(HTTP_200_OK)


@api_view(['POST'])
def get_about_business(request):
    '''
    :param request:
    {
        "business_profile": 1
    }
    :return:
    HTTP_200_OK
    '''
    business_profile = request.data.get('business_profile')

    about = AboutBusiness.objects.filter(profile=business_profile).first()

    if about:
        out_var = {"business_profile": business_profile,
                     "title": about.title,
                     "text": about.text,
                     "video_url": about.video}
    else:
        out_var = {}

    return Response(out_var)


@api_view(['POST'])
@permission_classes((IsAuthenticated, IsBusiness, ))
def add_photo_for_about_business(request):
    '''
    :param request:
    {
        "photos": []
    }
    :return:
    HTTP_200_OK
    '''
    business_profile = request.user.profile.profilebusiness
    photos = request.data.get('photos')

    about = AboutBusiness.objects.filter(profile=business_profile).first()

    if not about:
        return Response({'error': 'Business profile nas no about_me'}, status=400)

    out_vars = []
    for p in photos:
        if PhotoAboutBusiness.objects.filter(about_business__profile=business_profile).count() == 10:
            return Response({"error": "Can only save 10 pictures"})
        pic = PhotoAboutBusiness(about_business=about, photo=about_business_upload(p, business_profile.id))
        pic.save()
        out_vars.append({pic.id: pic.photo.url})

    return Response(out_vars)


@api_view(['POST'])
@permission_classes((IsAuthenticated, IsBusiness, ))
def delete_photo_from_about_business(request):
    '''
    :param request:
    {
        "photo_ids": []
    }
    :return:
    HTTP_200_OK
    '''
    business_profile = request.user.profile.profilebusiness
    photos = request.data.get('photo_ids')

    about = AboutBusiness.objects.filter(profile=business_profile).first()

    if not about:
        return Response({'error': 'Business profile nas no about_me'}, status=400)

    for p in photos:
        pic = PhotoAboutBusiness.objects.filter(about_business=about, id=p)
        pic.delete()

    return Response(HTTP_200_OK)


@api_view(['POST'])
def get_photos_about_business(request):
    '''
    :param request:
    {
        "business_profile": 1
    }
    :return:
    HTTP_200_OK
    '''
    business_profile = request.data.get('business_profile')

    photos = PhotoAboutBusiness.objects.filter(about_business__profile=business_profile,)
    out_vars = [{"id": p.id, "url": p.photo.url} for p in photos]

    return Response(out_vars)


@api_view(['POST'])
@permission_classes((IsAuthenticated, IsBusiness, ))
def add_or_update_about_me(request):
    """
    :param request:
    {
        "title": "",
        "text": "",
        "video_url": "https://www.google.ru/"
    }
    :return:
    HTTP_200_OK
    """
    business_profile = request.user.profile.profilebusiness

    title = request.data.get('title')
    text = request.data.get('text')
    video = request.data.get('video_url')

    if not title and not text:
        return Response({'error': 'Empty title or text'}, status=400)

    about, created = AboutBusiness.objects.get_or_create(profile=business_profile)
    about.title = title
    about.text = text
    about.video = video
    about.save()

    return Response({"business_profile": business_profile.id,
                     "title": about.title,
                     "text": about.text,
                     "video": about.video})


@api_view(['GET'])
@permission_classes((IsAuthenticated, IsBusiness, ))
def delete_about_me(request):
    """
    :param request:
    :return:
    HTTP_200_OK
    """
    business_profile = request.user.profile.profilebusiness

    about = AboutBusiness.objects.filter(profile=business_profile)
    about.delete()

    return Response(HTTP_200_OK)


@api_view(['POST'])
def get_about_business(request):
    """
    :param request:
    {
        "business_profile": 1
    }
    :return:
    HTTP_200_OK
    """
    business_profile = request.data.get('business_profile')

    about = AboutBusiness.objects.filter(profile=business_profile).first()

    if about:
        out_var = {"business_profile": business_profile,
                     "title": about.title,
                     "text": about.text,
                     "video_url": about.video}
    else:
        out_var = {}

    return Response(out_var)


@api_view(['POST'])
@permission_classes((IsAuthenticated, IsBusiness, ))
def add_photo_for_about_business(request):
    """
    :param request:
    {
        "photos": []
    }
    :return:
    HTTP_200_OK
    """
    business_profile = request.user.profile.profilebusiness
    photos = request.data.get('photos')

    about = AboutBusiness.objects.filter(profile=business_profile).first()

    if not about:
        return Response({'error': 'Business profile has no about_me'}, status=400)

    out_vars = []
    for p in photos:
        if PhotoAboutBusiness.objects.filter(about_business__profile=business_profile).count() == 10:
            return Response({"error": "Can only save 10 pictures"})
        pic = PhotoAboutBusiness(about_business=about, photo=about_business_upload(p, business_profile.id))
        pic.save()
        out_vars.append({'id': pic.id, 'url': pic.photo.url})

    return Response(out_vars)


@api_view(['POST'])
@permission_classes((IsAuthenticated, IsBusiness, ))
def delete_photo_from_about_business(request):
    """
    :param request:
    {
        "photo_ids": []
    }
    :return:
    HTTP_200_OK
    """
    business_profile = request.user.profile.profilebusiness
    photos = request.data.get('photo_ids')

    about = AboutBusiness.objects.filter(profile=business_profile).first()

    if not about:
        return Response({'error': 'Business profile nas no about_me'}, status=400)

    for p in photos:
        pic = PhotoAboutBusiness.objects.filter(about_business=about, id=p)
        pic.delete()

    return Response(HTTP_200_OK)


@api_view(['POST'])
def get_photos_about_business(request):
    """
    :param request:
    {
        "business_profile": 1
    }
    :return:
    HTTP_200_OK
    """
    business_profile = request.data.get('business_profile')

    photos = PhotoAboutBusiness.objects.filter(about_business__profile=business_profile,)
    out_vars = [{"id": p.id, "url": p.photo.url} for p in photos]

    return Response(out_vars)


@api_view(['GET'])
@permission_classes((IsAuthenticated, IsBusiness, ))
def get_form_update_business_profile(request):
    prof = request.user.profile.profilebusiness

    out_vars = {
        'type_of_business': prof.type_of_business,
        'organization_type': prof.organization_type,
        'organization_name': prof.organization_name,
        'vat': prof.vat,
        'registration_number': prof.registration_number,
        'first_name': prof.first_name,
        'middle_name': prof.middle_name,
        'last_name': prof.last_name,
        'position': prof.position_in_com,
        'code_number_phone': prof.code_num_phone.id if prof.code_num_phone else False,
        'phone_number': prof.phone_number,
        'email': prof.email,
        'photos': list(map(lambda x: x.img.url, FileForProfile.objects.filter(user=request.user, type_profile=2))),
        "addition_receiver": prof.addition_receiver,
        "receiver_phonenumber": prof.receiver_phonenumber
    }

    return Response(out_vars)


@api_view(['POST'])
@permission_classes((IsAuthenticated, IsBusiness, ))
def update_business_profile(request):
    """
    :param request:
    {
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
    """
    prof = request.user.profile.profilebusiness

    type_of_business = request.data.get("type_of_business")
    organization_type = request.data.get("organization_type")
    organization_name = request.data.get("organization_name")
    vat = request.data.get("vat")
    registration_number = request.data.get("registration_number")
    first_name = request.data.get("first_name")
    middle_name = request.data.get("middle_name", "")
    last_name = request.data.get("last_name")
    position_in_com = request.data.get("position")
    code_number_phone = request.data.get("code_number_phone")
    phone_number = request.data.get("phone_number")
    email = request.data.get("email")
    addition_receiver = request.data.get("addition_receiver")
    receiver_phonenumber = request.data.get("receiver_phonenumber")

    if not type_of_business:
        return Response({'error': 'Empty type of business'}, status=400)
    if not organization_type:
        return Response({'error': 'Empty organization type'}, status=400)
    if not organization_name:
        return Response({'error': 'Empty organization name'}, status=400)
    if not vat:
        return Response({'error': 'Empty vat'}, status=400)
    if not registration_number:
        return Response({'error': 'Empty registration number'}, status=400)
    if not first_name:
        return Response({'error': 'Empty first name'}, status=400)
    if not last_name:
        return Response({'error': 'Empty last name'}, status=400)
    if not position_in_com:
        return Response({'error': 'Empty position'}, status=400)
    if not code_number_phone or not phone_number:
        return Response({'error': 'Empty phonenumber'}, status=400)
    if not email:
        return Response({'error': 'Empty email'}, status=400)

    try:
        num_code = CountryNumberphone.objects.get(id=code_number_phone)
    except CountryNumberphone.DoesNotExist:
        return Response({'error': 'Incorrect id of country code'}, status=400)

    prof.type_of_business = type_of_business
    prof.organization_type = organization_type
    prof.organization_name = organization_name
    prof.vat = vat
    prof.registration_number = registration_number
    prof.first_name = first_name
    prof.middle_name = middle_name
    prof.last_name = last_name
    prof.position_in_com = position_in_com
    prof.code_num_phone = num_code
    prof.phone_number = phone_number
    prof.email = email
    prof.addition_receiver = addition_receiver
    prof.receiver_phonenumber = receiver_phonenumber

    prof.save()
    return Response(HTTP_200_OK)


@api_view(['POST'])
@permission_classes((IsAuthenticated, IsBusiness, ))
def update_business_avatar(request):
    """
    :param request:
    {
        "avatar": ""
    }
    :return:
    """
    profilebusiness = request.user.profile.profilebusiness
    avatar = request.data.get('avatar', False)
    profilebusiness.avatar.delete(False)

    if avatar:
        avatar = avatar_business_upload(avatar, profilebusiness.id)
        profilebusiness.avatar = avatar

    profilebusiness.save()

    try:
        avatar = profilebusiness.avatar.url
    except ValueError:
        avatar = False

    out_vars = {
        'avatar': avatar
    }

    return Response(out_vars)
