# -*- coding: utf-8 -*-

from django.contrib.contenttypes.models import ContentType

from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated

from core.models import CountryNumberphone
from core.permissions import IsBusiness
from userdata.models import (
    ProfileBusiness, AddressDeliveryBusiness, AddressDeliveryDocs, AddressDeliveryProfile,
    AddressLegal, AddressPickUp, AddressPayment, PickUpWorkTime)

from datetime import datetime

from farm.models import AddressFarm
from geodata.models import City, NotExistCity, Region, NotExistRegion
from rest_framework.status import HTTP_200_OK

from userdata.tools import *


def address_add(country_id, region_id, city_id, address, postal_code, base, obj, city_name=False,
                region_name=False, address_name=False, default_address=False):
    try:
        reg = Region.objects.get(id=region_id, country=country_id)
        # print('есть регион в этой стране')
        try:
            city = City.objects.get(id=city_id, region=reg)
            # print('есть город в этом регионе')
            if default_address:
                base.objects.filter(profile=obj).update(default=False)

            a_u, addr_created = base.objects.get_or_create(
                object_id=city.id,
                address=address,
                postal_code=postal_code,
                profile_id=obj,
                default=default_address,
                name=address_name
            )
            a_u.save()

        except City.DoesNotExist:
            # print('Нет города в этом регионе')
            city, ne_city_created = NotExistCity.objects.get_or_create(
                object_id=reg.id,
                name_en=city_name
            )
            city.save()

            if default_address:
                base.objects.filter(profile=obj).update(default=False)
            a_u, addr_created = base.objects.get_or_create(
                content_type=ContentType.objects.get_for_model(NotExistCity),
                object_id=city.id,
                address=address,
                postal_code=postal_code,
                profile_id=obj,
                default=default_address,
                name=address_name
            )
            a_u.save()

    except Region.DoesNotExist:
        # print('Нет региона в этой стране')
        region, ne_reg_created = NotExistRegion.objects.get_or_create(
            country_id=country_id,
            name_en=region_name,
        )
        region.save()

        city, ne_city_created = NotExistCity.objects.get_or_create(
            content_type=ContentType.objects.get_for_model(NotExistRegion),
            object_id=region.id,
            name_en=city_name
        )
        city.save()

        if default_address:
            base.objects.filter(profile=obj).update(default=False)
        a_u, addr_created = base.objects.get_or_create(
            content_type=ContentType.objects.get_for_model(NotExistCity),
            object_id=city.id,
            address=address,
            postal_code=postal_code,
            profile_id=obj
        )
        a_u.name = address_name
        a_u.default = default_address
        a_u.save()
    return a_u


def address_change(address_id, country_id, region_id, city_id, address, postal_code, base, obj, city_name=False,
                region_name=False, address_name=False, address_default=False):

    addr = base.objects.filter(id=address_id).first()

    if not addr:
        return None

    # чистка базы несуществующих городой и регионов
    # if type(addr.city.region) == NotExistRegion:
    #     old_reg = NotExistRegion.objects.filter(id=addr.city.region.id)
    #     # old_reg.delete()
    #
    # if type(addr.city) == NotExistCity:
    #     old_city = NotExistCity.objects.filter(id=addr.city.id)
    #     # old_city.delete()

    try:
        reg = Region.objects.get(id=region_id, country=country_id)
        # print('Есть регион в этой стране')
        try:
            city = City.objects.get(id=city_id, region=reg)
            # print('Есть город в этом регионе')
            if address_default:
                base.objects.filter(profile=obj).update(default=False)

            addr.content_type = ContentType.objects.get_for_model(City)
            addr.object_id = city.id
            addr.address = address
            addr.postal_code = postal_code
            addr.profile_id = obj
            addr.default = address_default
            addr.name = address_name
            addr.save()

        except City.DoesNotExist:
            # print('Нет города в этом регионе')

            # if type(addr.city) == NotExistCity:
            #     old_city = NotExistCity.objects.filter(
            #         id=addr.city.id
            #     )

            city, ne_city_created = NotExistCity.objects.get_or_create(
                object_id=reg.id,
                name_en=city_name
            )
            city.save()

            # if ne_city_created and old_city:
            #     old_city.delete()
            #     print("Удалили старый город")

            if address_default:
                base.objects.filter(profile=obj).update(default=False)

            addr.content_type = ContentType.objects.get_for_model(NotExistCity)
            addr.object_id = city.id
            addr.address = address
            addr.postal_code = postal_code
            addr.profile_id = obj
            addr.default = address_default
            addr.name = address_name
            addr.save()

    except Region.DoesNotExist:
        # print('Нет региона в этой стране')
        region, reg_created = NotExistRegion.objects.get_or_create(
            country_id=country_id,
            name_en=region_name,
        )
        region.save()

        # if reg_created and old_reg:
        #     old_reg.delete()
        #     print("Удалили старый регион")

        city, city_created = NotExistCity.objects.get_or_create(
            content_type=ContentType.objects.get_for_model(NotExistRegion),
            object_id=region.id,
            name_en=city_name
        )
        city.save()

        # if city_created and old_city:
        #     old_city.delete()
        #     print("Удалили старый город")

        if address_default:
            base.objects.filter(profile=obj).update(default=False)

        addr.content_type = ContentType.objects.get_for_model(NotExistCity)
        addr.object_id = city.id
        addr.address = address
        addr.postal_code = postal_code
        addr.profile_id = obj
        addr.default = address_default
        addr.name = address_name
        addr.save()

    return addr


@api_view(['GET'])
def get_country_num_code(request):
    out_vars = {
        'codes': {x.id: {'name': x.country.name_en, 'code': x.code, 'max_digits': x.max_digits}
                  for x in CountryNumberphone.objects.all()}
    }
    return Response(out_vars)


@api_view(['GET'])
@permission_classes((IsAuthenticated,))
def get_personal_address_book(request):
    address_book = AddressDeliveryProfile.objects.filter(profile__user=request.user)

    return Response([json_address(addr) for addr in address_book])


@api_view(['GET'])
@permission_classes((IsAuthenticated, IsBusiness, ))
def get_business_address_book(request):
    address_book = AddressPickUp.objects.filter(profile=request.user.profile.profilebusiness)

    return Response([json_address(addr) for addr in address_book])


@api_view(['GET'])
@permission_classes((IsAuthenticated, IsBusiness, ))
def get_business_legal_address(request):
    legal_address = AddressLegal.objects.filter(profile=request.user.profile.profilebusiness).first()

    if not legal_address:
        return Response({'error': 'Business profile has not legal address'}, status=400)

    return Response(json_address(legal_address))


@api_view(['POST'])
@permission_classes((IsAuthenticated,))
def add_address(request):
    """
    :param request:
    {
        "address_name": "",
        "default_address": false,

        "legal": true,
        "delivery_profile": true,
        "payment": true,
        "delivery_business": true,
        "delivery_docs": true,
        "pick_up": true,
        "farm": true,

        "country_id": 0,
        "region_id": 0,
        "city_id": 0,
        "region_name": "",
        "city_name": "",
        "address": "",
        "postal_code": ""
    }
    :return:
    """
    user = request.user
    address_type = False
    address_name = request.data.get("address_name", "")
    default_address = bool(request.data.get("default_address", False))

    delivery_address_profile = request.data.get("delivery_profile", False)
    address_payment = request.data.get("payment", False)
    legal = request.data.get("legal", False)
    delivery_business = request.data.get("delivery_business", False)
    delivery_docs = request.data.get("delivery_docs", False)
    pick_up = request.data.get("pick_up", False)
    farm_addr = request.data.get("farm", False)
    farm_id = request.data.get("farm_id", 0)

    country_id = request.data.get("country_id", 0)
    region_id = request.data.get("region_id", 0)
    city_id = request.data.get("city_id", 0)
    region_name = request.data.get("region_name", "")
    city_name = request.data.get("city_name", "")
    address = request.data.get("address", "")
    postal_code = request.data.get("postal_code", "")

    if not country_id:
        return Response({'error': 'Empty country id'}, status=400)

    if not address or not postal_code:
        return Response({'error': 'Empty part of address'}, status=400)

    if not address_payment and not legal and not delivery_address_profile and not delivery_business and not delivery_docs and not pick_up and not farm_addr:
        return Response({"error": "You should select type of address"}, status=400)

    if delivery_address_profile:
        address_type = 2
        addr_class = AddressDeliveryProfile
        obj = user.profile.id

    elif address_payment:
        address_type = 7
        addr_class = AddressPayment
        obj = user.profile.id

    else:
        try:
            profile_business = ProfileBusiness.objects.get(profile__user=user)
        except ProfileBusiness.DoesNotExist:
            return Response({"error": "User has no business profile"}, status=400)

        if delivery_business:
            address_type = 3
            addr_class = AddressDeliveryBusiness
            obj = profile_business.id

        if delivery_docs:
            address_type = 4
            addr_class = AddressDeliveryDocs
            obj = profile_business.id

        if pick_up:
            address_type = 5
            addr_class = AddressPickUp
            obj = profile_business.id

        if legal:
            addr_exists = AddressLegal.objects.filter(profile=profile_business).exists()
            if addr_exists:
                return Response({"error": "User already has legal address"}, status=400)

            address_type = 1
            addr_class = AddressLegal
            obj = profile_business.id

        if farm_addr:
            addr = AddressFarm.objects.filter(profile__profile=profile_business, id=farm_id).exists()
            if addr:
                return Response({"error": "Farm already has address"}, status=400)

            address_type = 6
            addr_class = AddressFarm
            obj = farm_id

    new_address = address_add(country_id, region_id, city_id, address, postal_code,
                              addr_class, obj, city_name,
                              region_name, address_name, default_address)

    out_vars = json_address(new_address)
    out_vars["address_type"] = address_type

    return Response(out_vars)


@api_view(['POST'])
@permission_classes((IsAuthenticated,))
def change_address(request):
    """
    :param request:
    {
        "address_name": "",
        "default_address": false,
        "address_id": 0,

        "legal": true,
        "delivery_profile": true,
        "payment": true,
        "delivery_business": true,
        "delivery_docs": true,
        "pick_up": true,
        "farm": true,

        "country_id": 0,
        "region_id": 0,
        "city_id": 0,
        "region_name": "",
        "city_name": "",
        "address": "",
        "postal_code": ""
    }
    :return:
    """
    user = request.user
    address_type = False
    address_name = request.data.get("address_name", "")
    address_id = request.data.get("address_id", 0)
    default_address = bool(request.data.get("default_address", False))

    delivery_profile = request.data.get("delivery_profile", False)
    payment = request.data.get("payment", False)
    legal = request.data.get("legal", False)
    delivery_business = request.data.get("delivery_business", False)
    delivery_docs = request.data.get("delivery_docs", False)
    pick_up = request.data.get("pick_up", False)
    farm = request.data.get("farm", False)

    farm_id = request.data.get("farm_id", 0)
    country_id = request.data.get("country_id", 0)
    region_id = request.data.get("region_id", 0)
    region_name = request.data.get("region_name", "")
    city_id = request.data.get("city_id", 0)
    city_name = request.data.get("city_name", "")
    address = request.data.get("address", "")
    postal_code = request.data.get("postal_code", "")

    if not country_id:
        return Response({'error': 'Incorrect country id'}, status=400)

    if not address or not postal_code:
        return Response({'error': 'Empty address or postal_code'}, status=400)

    if not payment and not legal and not delivery_profile and not delivery_business and not delivery_docs and not pick_up and not farm:
        return Response({"error": "You should select type of address"}, status=400)

    if delivery_profile:
        address_type = 2
        addr_class = AddressDeliveryProfile
        obj = user.profile.id

    elif payment:
        address_type = 7
        addr_class = AddressPayment
        obj = user.profile.id

    else:
        profile_business = ProfileBusiness.objects.filter(profile__user=user).first()
        if not profile_business:
            return Response({"error": "User has no business profile"}, status=400)

        if legal:
            address_type = 1
            addr_class = AddressLegal
            obj = profile_business.id

        if delivery_business:
            address_type = 3
            addr_class = AddressDeliveryBusiness
            obj = profile_business.id

        if delivery_docs:
            address_type = 4
            addr_class = AddressDeliveryDocs
            obj = profile_business.id

        if pick_up:
            address_type = 5
            addr_class = AddressPickUp
            obj = profile_business.id

        if farm:
            addr_exists = AddressFarm.objects.filter(profile__profile=profile_business, id=farm_id).exists()
            if addr_exists:
                return Response({"error": "Farm already has address"}, status=400)

            address_type = 6
            addr_class = AddressFarm
            obj = farm_id

    changing_addr = address_change(address_id, country_id, region_id, city_id, address, postal_code,
                                     addr_class, obj, city_name,
                                     region_name, address_name, default_address)

    if not changing_addr:
        return Response({"error": "Incorrect address id"}, status=404)

    out_vars = json_address(changing_addr)
    out_vars["address_type"] = address_type

    return Response(out_vars)


@api_view(['POST'])
@permission_classes((IsAuthenticated,))
def mark_address_as_default(request):
    """
    :param request:
    {
        "address_id": 0,

        "delivery_profile": true
        "payment": true
        "delivery_business": true
        "delivery_docs": true
        "pick_up": true
    }
    :return:
    """
    address_id = request.data.get('address_id', 0)

    delivery_profile = request.data.get('delivery_profile', False)
    payment = request.data.get('payment', False)
    delivery_docs = request.data.get('delivery_docs', False)
    pick_up = request.data.get('pick_up', False)
    delivery_business = request.data.get('delivery_business', False)

    addresses = False
    if delivery_profile:
        addresses = AddressDeliveryProfile.objects.filter(profile__user=request.user)

    if payment:
        addresses = AddressPayment.objects.filter(profile__user=request.user)

    if delivery_docs:
        addresses = AddressDeliveryDocs.objects.filter(profile__user=request.user)

    if pick_up:
        addresses = AddressPickUp.objects.filter(profile__user=request.user)

    if delivery_business:
        addresses = AddressDeliveryBusiness.objects.filter(profile__user=request.user)

    if not addresses:
        return Response({"error": "Address not found"}, status=404)

    addr = addresses.filter(id=address_id).first()

    if not addr:
        return Response({"error": "Address not found"}, status=404)

    addresses.update(default=False)
    addr.default = True
    addr.save()

    return Response(HTTP_200_OK)


@api_view(['POST'])
@permission_classes((IsAuthenticated,))
def delete_address(request):
    """
    :param request:
    {
        "address_id": id,

        "legal_address": true
        "address_delivery_profile": true
        "address_delivery_business": true
        "address_delivery_docs": true
        "address_pick_up": true
        "address_farm": true
    }
    :return:
    """
    profile = request.user.profile
    address_id = request.data.get("address_id", False)

    legal_address = request.data.get("legal_address", False)
    address_delivery_profile = request.data.get("address_delivery_profile", False)
    address_delivery_business = request.data.get("address_delivery_business", False)
    address_delivery_docs = request.data.get("address_delivery_docs", False)
    address_pick_up = request.data.get("address_pick_up", False)
    address_farm = request.data.get("address_farm", False)

    if not (legal_address or address_delivery_profile or address_delivery_business or address_delivery_docs or address_pick_up or address_farm):
        return Response({"error": "Empty address type"}, status=400)

    if address_delivery_profile:
        try:
            d_addr = AddressDeliveryProfile.objects.get(profile=profile, id=address_id)
        except AddressDeliveryProfile.DoesNotExist:
            return Response({"error": "No such address"}, status=400)
        else:
            d_addr.delete()
            return Response(HTTP_200_OK)

    try:
        business_profile = ProfileBusiness.objects.get(profile=profile)
    except ProfileBusiness.DoesNotExist:
        return Response({"error": "User has no business account"}, status=400)

    if legal_address:
        try:
            d_addr = AddressLegal.objects.get(profile=business_profile, id=address_id)
        except AddressLegal.DoesNotExist:
            return Response({"error": "User has no such legal address"}, status=400)
        else:
            d_addr.delete()

    if address_delivery_business:
        try:
            d_addr = AddressDeliveryBusiness.objects.get(profile=business_profile, id=address_id)
        except AddressDeliveryBusiness.DoesNotExist:
            return Response({"error": "User has no such delivery business address"}, status=400)
        else:
            d_addr.delete()

    if address_delivery_docs:
        try:
            d_addr = AddressDeliveryDocs.objects.get(profile=business_profile, id=address_id)
        except AddressDeliveryDocs.DoesNotExist:
            return Response({"error": "User has no such delivery address for documents"}, status=400)
        else:
            d_addr.delete()

    if address_pick_up:
        try:
            d_addr = AddressPickUp.objects.get(profile=business_profile, id=address_id)
        except AddressPickUp.DoesNotExist:
            return Response({"error": "User has no such pick_up address"}, status=400)
        else:
            d_addr.delete()

    if address_farm:
        try:
            d_addr = AddressFarm.objects.get(farm__profile=business_profile, id=address_id)
        except AddressFarm.DoesNotExist:
            return Response({"error": "User has no such farm address"}, status=400)
        else:
            d_addr.delete()

    return Response(HTTP_200_OK)


@api_view(['POST'])
@permission_classes((IsAuthenticated, IsBusiness))
def add_or_change_pickup_workday(request):
    """
    :param request:
    {
        "pickup_address": 1,
        "day": 1,
        "open": "09:00",
        "close": "17:30",
        "break_start": "12:00",
        "break_stop": "13:00"
    }
    :return:
    """
    pickup_address_id = request.data.get('pickup_address', 0)
    day = request.data.get('day', 0)
    open_t = request.data.get('open')
    close_t = request.data.get('close')
    break_start = request.data.get('break_start')
    break_stop = request.data.get('break_stop')

    pickup_address = AddressPickUp.objects.filter(profile__profile__user=request.user, id=pickup_address_id).first()

    if not pickup_address:
        return Response({"error": "Address not found"}, status=404)

    if day not in [num for (num, name) in PickUpWorkTime.DAY_OF_WEEK]:
        return Response({"error": "Incorrect day"}, status=400)

    if not open_t:
        return Response({"error": "Empty open time"}, status=400)
    if not close_t:
        return Response({"error": "Empty close time"}, status=400)

    try:
        open_time = datetime.strptime(open_t, '%H:%M')
    except ValueError:
        return Response({"error": "Incorrect open time"}, status=400)

    try:
        close_time = datetime.strptime(close_t, '%H:%M')
    except ValueError:
        return Response({"error": "Incorrect close time"}, status=400)

    if close_time < open_time:
        return Response({"error": "Incorrect time - should be open_time < close_time"}, status=400)

    if break_start and break_stop:
        try:
            break_start = datetime.strptime(break_start, '%H:%M')
        except ValueError:
            return Response({"error": "Incorrect start break time"}, status=400)

        try:
            break_stop = datetime.strptime(break_stop, '%H:%M')
        except ValueError:
            return Response({"error": "Incorrect stop break time"}, status=400)

        if not open_time < break_start < break_stop < close_time:
            return Response({"error": "Incorrect work time - should be open_time < break_start < break_stop < close_time"}, status=400)

    work_time, created = PickUpWorkTime.objects.get_or_create(
        pickup=pickup_address,
        day=day
    )
    work_time.open = open_time
    work_time.close = close_time

    if break_start and break_stop:
        work_time.break_start = break_start
        work_time.break_stop = break_stop
    else:
        work_time.break_start = None
        work_time.break_stop = None

    work_time.save()

    return Response(json_work_time(work_time))


@api_view(['POST'])
@permission_classes((IsAuthenticated, IsBusiness))
def delete_pickup_workday(request):
    """
    :param request:
    {
        "pickup_address": 1,
        "day": 1
    }
    :return:
    """
    pickup_address_id = request.data.get('pickup_address', 0)
    day = request.data.get('day', 0)

    pickup_address = AddressPickUp.objects.filter(profile__profile__user=request.user, id=pickup_address_id).first()

    if not pickup_address:
        return Response({"error": "Address not found"}, status=404)

    if day not in [num for (num, name) in PickUpWorkTime.DAY_OF_WEEK]:
        return Response({"error": "Incorrect day"}, status=400)

    work_day = PickUpWorkTime.objects.filter(pickup=pickup_address, day=day)
    work_day.delete()

    return Response(HTTP_200_OK)


@api_view(['POST'])
def get_pickup_workdays(request):
    """
    :param request:
    {
        "pickup_address": 1
    }
    :return:
    """
    pickup_address_id = request.data.get('pickup_address', 0)

    pickup_address = AddressPickUp.objects.filter(id=pickup_address_id).first()

    if not pickup_address:
        return Response({"error": "Address not found"}, status=404)

    work_days = PickUpWorkTime.objects.filter(pickup=pickup_address)

    return Response([json_work_time(wd) for wd in work_days])

