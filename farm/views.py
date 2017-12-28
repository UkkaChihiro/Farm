# -*- coding: utf-8 -*-
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated

from catalog.models import Group
from core.permissions import IsBusiness
from farm.models import Farm, FarmGroupMap, AddressFarm
from userdata.models import ProfileBusiness
from .tools import *


@api_view(['POST'])
@permission_classes((IsAuthenticated, IsBusiness, ))
def add_farm(request):
    '''
    :param request:
    {
        "name": "Name",
        "groups": [1,2,3]
    }
    :return:
    {
        "groups": [1,2,3],
        "farm": {
            "name": "Name",
            "id": id,
            "business_profile": id
        }
    }
    '''
    name = request.data.get('name', '')
    groups = request.data.get('groups', [])

    wrong_gr_ids = []
    correct_gr = []
    for g in groups:
        try:
            group = Group.objects.get(id=g)
        except Group.DoesNotExist:
            wrong_gr_ids.append(g)
        else:
            correct_gr.append(group)

    if not correct_gr:
        # ферма должна быть привязана хотя бы к одной группе категорий
        return Response({'error': 'Groups with such ids not found: {0}'.format(wrong_gr_ids)}, status=400)

    business_profile = ProfileBusiness.objects.filter(profile__user=request.user).first()
    farm = Farm(
        profile=business_profile,
        name=name,
    )
    farm.save()

    for gr in correct_gr:
        farm_group = FarmGroupMap(
            farm=farm,
            group=gr,
        )
        farm_group.save()

    out_vars = {
        "farm": {
            "id": farm.id,
            "name": farm.name,
            "business_profile": farm.profile_id
        },
        "groups": [gr.id for gr in correct_gr]
    }

    return Response(out_vars)


@api_view(['POST'])
@permission_classes((IsAuthenticated, IsBusiness, ))
def update_farm(request):
    '''
    :param request:
    {
        "farm_id": 6,
        "name": "Farm 765",
        "groups": [1,2,3]
    }
    :return:
    {
        "groups": [
            1,
            2
        ],
        "farm": {
            "name": "Farm 765",
            "id": 6,
            "business_profile": 1
        }
    }
    '''
    farm_id = request.data.get('farm_id', 0)
    name = request.data.get('name', '')
    groups = request.data.get('groups', [])

    try:
        farm = Farm.objects.get(id=farm_id, profile__profile__user=request.user, mark_deleted=False)
    except Farm.DoesNotExist:
        return Response({'error': 'Farm not found'}, status=400)

    wrong_gr_ids = []
    correct_gr = []
    for g in groups:
        try:
            group = Group.objects.get(id=g)
        except Group.DoesNotExist:
            wrong_gr_ids.append(g)
        else:
            correct_gr.append(group)

    farm.name = name
    farm.save()

    FarmGroupMap.objects.filter(farm=farm).delete()
    for gr in correct_gr:
        farm_group = FarmGroupMap(
            farm=farm,
            group=gr,
        )
        farm_group.save()

    out_vars = {
        "farm": {
            "id": farm.id,
            "name": farm.name,
            "business_profile": farm.profile_id
        },
        "groups": [gr.id for gr in correct_gr]
    }

    return Response(out_vars)


@api_view(['GET'])
@permission_classes((IsAuthenticated, IsBusiness, ))
def get_all_my_farms(request):
    '''
    :param request:
    :return:
    {
    "farms": [
            {
                "address": [],
                "name": "FARM 1",
                "groups": [
                    1,
                    2
                ],
                "business_profile": 1,
                "id": 1
            }
        ]
    }
    '''
    profilebusiness = request.user.profile.profilebusiness
    out_farms = []

    farms = Farm.objects.filter(profile=profilebusiness, mark_deleted=False)

    for farm in farms:
        addr = AddressFarm.objects.filter(profile=farm).first()
        if addr:
            addr = {
                'id': addr.id,
                'city': addr.city.name_en,
                'region': addr.city.region.name_en,
                'country': addr.city.region.country.name_en,
                'address': addr.address,
                'postal_code': addr.postal_code,
                "city_id": addr.city.id if addr.city else None,#if addr.content_type.model != 'notexistcity' else '',
                "region_id": addr.city.region.id if addr.city else None,#if addr.content_type.model != 'notexistcity' else '',
                "country_id": addr.city.region.country.id if addr.city else None,
            }
        out_farms.append({
            'id': farm.id,
            'name': farm.name,
            'business_profile': farm.profile.id,
            'groups': [fg.group.id for fg in FarmGroupMap.objects.filter(farm=farm)],
            'address': addr,
            'mark_deleted': farm.mark_deleted,
        })

    out_vars = {
        'business_profile': profilebusiness.id,
        'farms': out_farms
    }

    return Response(out_vars)


@api_view(['POST'])
def get_farm(request):
    '''
    :param request:
    {
        "farm_id": id
    }
    :return:
    '''
    farm_id = request.data.get('farm_id', 0)

    farm = Farm.objects.filter(id=farm_id, mark_deleted=False).first()

    return Response(json_farm(farm))


@api_view(['POST'])
def get_farm_list(request):
    '''
    :param request:
    {
        "business_profile": id
    }
    :return:
    '''
    business_profile = request.data.get('business_profile', 0)
    bp = ProfileBusiness.objects.filter(id=business_profile).first()

    out_vars = {"farmer_name": "{0} {1}".format(bp.profile.user.last_name,
                                                    bp.profile.user.first_name),
                "business_profile": bp.id,
                "farm_list": list(json_farm(f) for f in Farm.objects.filter(profile=business_profile, mark_deleted=False))}

    return Response(out_vars)


@api_view(['POST'])
@permission_classes((IsAuthenticated, IsBusiness, ))
def delete_farm(request):
    '''
    :param request:
    {
        "farm_id": 6
    }
    :return:
    {
        "answer": "Farm {0} was marked as deleted"
    }
    '''
    farm_id = request.data.get('farm_id', 0)

    farm = Farm.objects.filter(id=farm_id, profile__profile__user=request.user, mark_deleted=False).first()
    if not farm:
        return Response({'error': 'Farm not found'}, status=400)

    farm.mark_deleted = True
    farm.save()

    return Response({"answer": "Farm {0} was marked as deleted".format(farm.id)})
