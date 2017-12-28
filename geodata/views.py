# -*- coding: utf-8 -*-
from rest_framework.decorators import api_view
from .models import City, Region, Country
from rest_framework.response import Response


@api_view(['GET'])
def get_country(request):
    out_var = [{'id': c.id, 'name': c.name_en} for c in Country.objects.all()]
    return Response({"countries": out_var})


@api_view(['POST'])
def get_region(request):
    country_id = request.data.get("country_id", 0)
    country_id = int(country_id)

    regions = Region.objects.filter(country=country_id)

    if not regions:
        return Response({'error': 'Region is not exist'}, status=400)

    out_var = [{'id': r.id, 'name': r.name_en} for r in regions]
    return Response({"regions": out_var})


@api_view(['POST'])
def get_city(request):
    region_id = request.data.get("region_id", 0)

    cities = City.objects.filter(region=region_id)

    if not cities:
        return Response({'error': 'City is not exist'}, status=400)

    out_var = [{'id': c.id, 'name': c.name_en} for c in cities]
    return Response({"cities": out_var})



