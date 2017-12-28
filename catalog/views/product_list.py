# -*- coding: utf-8 -*-
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from catalog.models import Product, Group, Category, SubCategory
from core.permissions import IsBusiness
from catalog.tools import *
from userdata.models import ProfileBusiness


def sort_products(prod_list, sorted_key, ascending):
    rev = False if ascending == 1 else True
    sorted_list = sorted(prod_list, key=sorted_key, reverse=rev)
    return sorted_list


@api_view(['GET'])
@permission_classes((IsAuthenticated, IsBusiness,))
def get_my_products(request):
    out_vars = {
        'products': list(map(
            sintez_json_from_product, Product.objects.filter(profile_business__profile__user=request.user)
        ))
    }
    return Response(out_vars)


@api_view(['POST'])
@permission_classes((IsAuthenticated, IsBusiness,))
def find_product_by_name_for_seller(request):
    '''
    :param request:
        {
            "name": ""
        }
    :return:
        {
            "products": [{}]
        }
    '''
    name = request.data.get('name', '')

    out_vars = {
        'products': list(map(
            sintez_json_from_product, Product.objects.filter(
                profile_business__profile=request.user.profile, name__icontains=name
            )
        ))
    }

    return Response(out_vars)


@api_view(['POST'])
def farmer_product_list(request):
    '''
    :param request:
    {
        "business_profile": 0
    }
    :return:
    '''
    seller_id = request.data.get('business_profile', 0)

    seller = ProfileBusiness.objects.filter(id=seller_id).first()
    if not seller:
        return Response({"error": "Seller not found"}, status=404)

    products = Product.objects.filter(profile_business=seller, mark_deleted=False)

    prod_list = {pr.id: sintez_json_from_product(pr) for pr in products}

    return Response(prod_list)


@api_view(['POST'])
def get_ten_random_products(request):
    '''
    :param request:
    {
        "business_profile": 0
    }
    :return:
    '''
    seller_id = request.data.get('business_profile', 0)

    seller = ProfileBusiness.objects.filter(id=seller_id).first()
    if not seller:
        return Response({"error": "Seller not found"}, status=404)

    products = Product.objects.filter(profile_business=seller, mark_deleted=False).order_by('?')[:10]

    prod_list = list(sintez_json_from_product(pr) for pr in products)

    return Response(prod_list)


@api_view(['POST'])
@permission_classes((IsAuthenticated,))
def available_product_list(request):
    '''
    :param request:
    {
        "ship_to": 1,
        "page": 1,
        "num": 10,

        "sort_by_price": 1 # 1, -1
        or
        "sort_by_name": 1 # 1, -1
    }
    :return:
    '''
    ship_to = request.data.get("ship_to", 0)
    page = request.data.get("page", 1)
    num = request.data.get("num", 10)
    sort_by_price = request.data.get("sort_by_price")   # 1, -1
    sort_by_name = request.data.get("sort_by_name")     # 1, -1

    sorted_list = []
    if sort_by_price in (1, -1):
        sorted_list = sort_products(Product.for_buyer(user=request.user.profile, ship_to=ship_to), lambda p: p.price, sort_by_price)

    if sort_by_name in (1, -1):
        sorted_list = sort_products(Product.for_buyer(user=request.user.profile, ship_to=ship_to), lambda p: p.name.lower(), sort_by_name)

    if not sorted_list:
        sorted_list = sort_products(Product.for_buyer(user=request.user.profile, ship_to=ship_to), lambda p: p.id, 1)

    prod_list = [short_prod(p) for p in sorted_list[page * num - num:page * num]]

    return Response(prod_list)


@api_view(['POST'])
def filter_products(request, group=0, category=0, subcategory=0):
    '''
    :param request:
    {
        "ship_to": 1,
        "page": 1,
        "num": 10,

        "sorted_by": "name",
        "sorted_by": "price",
        "sorted_by": "popularity",

        "sorted_order": "asc",
        "sorted_order": "desc",

        "filter_by": "type",
        "types": [1,2],

        "filter_by": "price",
        "price_min": 5.00,
        "price_max": 15.00

        "group_id": 1,
        "category_id": 1,
        "subcategory_id": 1
    }
    :return:
    '''
    ship_to = request.data.get("ship_to", 0)
    page = request.data.get("page", 1)
    num = request.data.get("num", 10)
    sorted_by = request.data.get("sorted_by")

    sorted_order = request.data.get("sorted_order")
    price_min = request.data.get("price_min")
    price_max = request.data.get("price_max")
    types = request.data.get("types", [])

    if not group:
        group_id = request.data.get("group_id")
        groups = Group.objects.filter(id=group_id)

        category_id = request.data.get("category_id")
        categories = Category.objects.filter(id=category_id)

        subcategory_id = request.data.get("subcategory_id")
        subcategories = Category.objects.filter(id=subcategory_id)

    if group and category and subcategory:
        groups = Group.objects.filter(slug=group)
        if not groups:
            return Response({"error": "Incorrect group"}, status=404)

        categories = Category.objects.filter(slug=category, parent__in=groups)
        if not categories:
            return Response({"error": "Incorrect category"}, status=404)

        subcategories = SubCategory.objects.filter(slug=subcategory, parent__in=categories)
        if not subcategories:
            return Response({"error": "Incorrect subcategory"}, status=404)
    else:
        if group and category:
            groups = Group.objects.filter(slug=group)
            if not groups:
                return Response({"error": "Incorrect group"}, status=404)

            categories = Category.objects.filter(slug=category, parent__in=groups)
            if not categories:
                return Response({"error": "Incorrect category"}, status=404)

            subcategories = SubCategory.objects.filter(parent__in=categories)
        else:
            if group:
                groups = Group.objects.filter(slug=group)
                if not groups:
                    return Response({"error": "Incorrect group"}, status=404)
                categories = Category.objects.filter(parent__in=groups)
                subcategories = SubCategory.objects.filter(parent__in=categories)


    print(groups)
    print(categories)
    print(subcategories)
    # group = Group.objects.filter(slug=group).first()
    # if not group:
    #     return Response({"error": "Incorrect group"}, status=404)
    #
    # category = Category.objects.filter(slug=category).first()
    # if not category:
    #     return Response({"error": "Incorrect category"}, status=404)
    #
    # subcategory = SubCategory.objects.filter(slug=subcategory).first()
    # if not subcategory:
    #     return Response({"error": "Incorrect subcategory"}, status=404)

    if sorted_by:
        if sorted_by not in ("class", "name", "price", "popularity"):
            return Response({"error": "Incorrect sorted method"}, status=400)

    if sorted_order:
        if sorted_order not in ("asc", "desc"):
            return Response({"error": "Incorrect sorted order"}, status=400)

    s_o = 1 if sorted_order == "asc" else -1

    sorted_key = lambda p: p.id

    if sorted_by == "name":
        print("name")
        sorted_key = lambda p: p.name or ""

    if sorted_by == "price":
        sorted_key = lambda p: p.discount_price or p.price

    if sorted_by == "popularity":
        sorted_key = lambda p: p.id #!!!!!

    if sorted_by == "class":
        sorted_key = lambda p: p.classproduct_set.first().name if p.classproduct_set.first() else 0

    sorted_list = sort_products(Product.product_list(user=request.user.profile,
                                                     ship_to=ship_to,
                                                     price_min=price_min,
                                                     price_max=price_max,
                                                     prod_types=types,
                                                     group=groups,
                                                     category=categories,
                                                     subcategory=subcategories), sorted_key, s_o)

    prod_list = list(short_prod(p) for p in sorted_list[page * num - num:page * num])

    return Response(prod_list)


@api_view(['POST'])
def product_list(request, group=0, category=0, subcategory=0):
    '''
    :param request:
    {
        "ship_to": 1,
        "page": 1,
        "num": 10,

        "sort_by_price": 1
        or
        "sort_by_name": 1
    }
    :return:
    '''
    print(group, category, subcategory)
    ship_to = request.data.get("ship_to", 0)
    page = request.data.get("page", 1)
    num = request.data.get("num", 10)
    sort_by_price = request.data.get("sort_by_price")
    sort_by_name = request.data.get("sort_by_name")

    sorted_list = []
    if sort_by_price:
        sorted_list = sort_products(Product.for_buyer(user=None, ship_to=ship_to, category__category=category), lambda prod: prod.price, sort_by_price)

    if sort_by_name:
        sorted_list = sort_products(Product.for_buyer(user=None, ship_to=ship_to), lambda prod: prod.name, sort_by_name)

    if not sorted_list:
        sorted_list = sort_products(Product.product_list(user=None,
                                                         ship_to=ship_to,
                                                         group=group,
                                                         category=category,
                                                         subcategory=subcategory), lambda prod: prod.id, 1)

    prod_list = [short_prod(pr) for pr in sorted_list][page * num - num:page * num]

    return Response(prod_list)








