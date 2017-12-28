# -*- coding: utf-8 -*-
import re

from django.db import IntegrityError
from rest_framework.permissions import IsAuthenticated
from rest_framework.status import HTTP_200_OK
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response

from catalog.models import Product
from core.permissions import IsBusiness
from geodata.models import Country
from .models import TarifsForCountry, TariffForProduct


@permission_classes((IsAuthenticated,))
def save_tariff(profile, type, mark, weight, name, price, *countries):
    # print(countries)
    for country in countries:
        tariff, created = TarifsForCountry.objects.get_or_create(
            profile=profile,
            country_id=country,
            name=name,
            mark=mark,
            type=type,
            weight=weight,
            price=re.sub(r'\D', '.', str(price))
        )
        # tariff.weight=weight
        # tariff.price=price
        tariff.save()


@api_view(['POST'])
@permission_classes((IsAuthenticated, IsBusiness, ))
def add_tariff_for_country(request):
    '''
    :param request:
    {
        "mark":1,
        "type":1,
        "weight": 30,
        "price": 20,
        "country": 2
    }
    :return:
    '''
    profile_business = request.user.profile.profilebusiness

    name = request.data.get('name')
    mark = request.data.get('mark', 0)
    type = request.data.get('type', 0)
    weight = request.data.get('weight', 0)
    price = request.data.get('price', '0')
    country = request.data.get('country', 0)

    try:
        save_tariff(profile_business, type, mark, weight, name, price, country)
    except IntegrityError:
        return Response({"error": "Product already has this tariff"}, status=404)

    return Response(HTTP_200_OK)


@api_view(['POST'])
@permission_classes((IsAuthenticated, IsBusiness, ))
def add_tariff_for_group(request):
    '''
    :param request:
    {"mark":1, "type":1, "weight": 30, "price": 20, "group": 2, "type":1}
    :return:
    '''
    profile_business = request.user.profile.profilebusiness

    name = request.data.get('name')
    mark = request.data.get('mark', 0)
    weight = request.data.get('weight', 0)
    price = request.data.get('price', '0')
    group = request.data.get('group', 0)
    type = request.data.get('type', 0)

    countries = Country.objects.filter(group=group).values_list('id', flat=True)
    save_tariff(profile_business, type, mark, weight, name, price, *countries)

    return Response(HTTP_200_OK)


@api_view(['POST'])
@permission_classes((IsAuthenticated, IsBusiness, ))
def delete_tariff_for_country(request):
    '''
    :param request:
    {"tariff": id}
    :return:
    HTTP 200 OK
    '''
    tariff = request.data.get('tariff', 0)

    tariff = TarifsForCountry.objects.filter(id=tariff, profile__profile__user=request.user)

    if not tariff:
        return Response({"error": "There is no such tariff"}, status=404)

    tariff.delete()

    return Response(HTTP_200_OK)


@api_view(['POST'])
@permission_classes((IsAuthenticated, IsBusiness, ))
def get_tariff_for_country(request):
    '''
    :param request:
    {"country": int}
    :return:
    {
    "tariffs": [
            {"tariff_id": 1, "type": 1, "country_id": 1, "mark": 1, "weight": 0, "price": "1.0" }
            ]
    }
    '''
    country = request.data.get('country', 0)

    tariffs = []
    country_tariffs = TarifsForCountry.objects.filter(profile__profile__user=request.user, country=country)

    for tariff in country_tariffs:
        tariffs.append(
            {
                "tariff_id": tariff.id,
                "type": tariff.type,
                "country_id": country,
                "mark": tariff.mark,
                "weight": tariff.weight,
                "price": str(tariff.price)
            }
        )
    return Response({"tariffs": tariffs})


@api_view(['POST'])
@permission_classes((IsAuthenticated, IsBusiness, ))
def get_tariff_for_group(request):
    '''
    :param request:
     {"group": int}
    :return:
    {
    "tariffs": [
        {"tariff_id": 3, "type": 1, "country_id": 2, "mark": 1, "weight": 0, "price": "1.0"},
        {"tariff_id": "","type": "", "country": 10, "mark": "", "weight": "", "price": ""},
        ]
        }
    '''
    group = request.data.get('group', 0)

    countries = Country.objects.filter(group=group)
    tariffs = []

    for country in countries:
        country_tariffs = TarifsForCountry.objects.filter(profile__profile__user=request.user, country=country)
        for tariff in country_tariffs:
            tariffs.append(
                {
                    "tariff_id": tariff.id,
                    "type": tariff.type,
                    "country_id": country.id,
                    "mark": tariff.mark,
                    "weight": tariff.weight,
                    "price": str(tariff.price)
                }
    )
    return Response({"tariffs": tariffs})


@api_view(['POST'])
# @permission_classes((IsAuthenticated,))
def get_group_of_countries(request):
    '''
    :param request:
    {"group": int}
    :return:
    {"countries": [ {"id": 2, "name": "Austria"},
                    {"id": 10, "name": "Belgium"},
                ]
    }
    '''
    group = request.data.get("group", 0)

    if group:
        countries = Country.objects.filter(group=group)
        out_vars = [{"id": country.id, "name": country.name_en} for country in countries]
    else:
        out_vars = []

    return Response({"countries": out_vars})


@api_view(['POST'])
@permission_classes((IsAuthenticated, IsBusiness, ))
def add_tariff_for_product(request):
    '''
    :param request:
    {"product": int, "tariff": int}
    :return:
    status 200
    '''
    product = request.data.get('product', 0)
    tariff = request.data.get('tariff', 0)

    p = Product.objects.filter(profile_business__profile__user=request.user, id=product).first()
    t = TarifsForCountry.objects.filter(profile__profile__user=request.user, id=tariff).first()
    if p and t:
        if t.mark == 3:
            tariff_for_product = TariffForProduct.objects.filter(product=p, tariff__mark=3,
                                                                 tariff__country=t.country).count()
            if tariff_for_product:
                return Response({"error": "For one country, you can add only one tariff with mark '->' for the product"},
                                status=400)

        TariffForProduct.objects.create(product=p, tariff=t)
    else:
        return Response(status=404)

    return Response(HTTP_200_OK)


@api_view(['POST'])
@permission_classes((IsAuthenticated, IsBusiness, ))
def get_tariff_for_product(request):
    '''
    :param request:
    {"product": int}
    :return:
    '''
    product = request.data.get('product')
    p = Product.objects.filter(profile_business__profile__user=request.user, id=product).first()
    if p:
        tariffs = TariffForProduct.objects.filter(product=p)
    else:
        return Response(status=404)
    list_tariffs = [
        {
            "id": t.id,
            "name": t.tariff.name,
            "country": t.tariff.country.name_en,
            "mark": t.tariff.mark,
            "weight": t.tariff.weight,
            "delivery_time_from": t.tariff.delivery_time_from,
            "delivery_time_to": t.tariff.delivery_time_to,
            "price": t.tariff.price,
            "type": t.tariff.type
        }
        for t in tariffs]

    return Response(list_tariffs)


@api_view(['POST'])
@permission_classes((IsAuthenticated, IsBusiness, ))
def dell_tariff_for_product(request):
    '''
    :param request:
    {"product": int, "tariff": int}
    :return:
    status 200
    '''
    product = request.data.get('product', 0)
    tariff = request.data.get('tariff', 0)

    p = Product.objects.filter(profile_business__profile__user=request.user, id=product).first()
    t = TarifsForCountry.objects.filter(profile__profile__user=request.user, id=tariff).first()

    if p and t:
        try:
            tariff_for_product = TariffForProduct.objects.get(product=p, tariff=t)
            tariff_for_product.delete()
        except TariffForProduct.DoesNotExist:
            return Response({'error': "Product does not have such a tariff"}, status=404)
    else:
        return Response(status=404)

    return Response(HTTP_200_OK)


