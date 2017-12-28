# -*- coding: utf-8 -*-
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from catalog.models import (
    Group, Category, SubCategory, TypeInCategory,
    )
from core.permissions import IsBusiness


@api_view(['GET'])
def get_all_groups(request):
    '''
    :param request: {}
    :return: {'all_groups': {'id': id, 'name': str}}
    '''
    all_groups = [{"id": group.id, "name": group.name} for group in Group.objects.all()]

    return Response({"all_groups": all_groups})


@api_view(['GET'])
def get_all_categories(request):
    '''
    :param request: {}
    :return:
    {
    'all_categories': [ {
            "category_id": id,
            "category_name": str,
            "group_name": str,
            "group_id": id
            }
        ]
    }
    '''
    all_categories = [
        {
            "category_id": category.id,
            "category_name": category.name,

            "group_id": category.parent.id,
            "group_name": category.parent.name
        }
        for category in Category.objects.all()]

    return Response({"all_categories": all_categories})


@api_view(['GET'])
def get_all_subcategories(request):
    '''
    :param request: {}
    :return: {'all_groups': {'id': id, 'name': str}}
    '''
    all_groups = [
        {
            "subcategory_id": subcat.id,
            "subcategory_name": subcat.name,

            "category_id": subcat.parent.id,
            "category_name": subcat.parent.name,

            "group_id": subcat.parent.parent.id,
            "group_name": subcat.parent.parent.name
        }
        for subcat in SubCategory.objects.all()]

    return Response({"all_groups": all_groups})


@api_view(['POST'])
def get_all_categories_for_group(request):
    '''
    :param request:
    {
        "group_id": id
    }
    :return:
    {
        'categories': [
            {
                'category_id': id,
                'category_name': str,
                'group_id': id,
                'group_name': str
            }
            ]
    }
    '''
    group_id = request.data.get("group_id", 0)

    all_categories = [
        {
            "category_id": category.id,
            "category_name": category.name,

            "group_id": category.parent.id,
            "group_name": category.parent.name
        }
        for category in Category.objects.filter(parent=group_id)]

    return Response({"categories": all_categories})


@api_view(['POST'])
def get_all_subcategories_for_category(request):
    '''
    :param request:
    {
        "category_id": id
    }
    :return:
    {
        'subcategories':
            {
                'subcategory_id': id,
                'subcategory_name': str,

                'category_id': id,
                'category_name': str,

                'group_id': id,
                'group_name': str
            }
    }
    '''
    category_id = request.data.get("category_id", 0)
    subcategories = [
        {
            "subcategory_id": subcategory.id,
            "subcategory_name": subcategory.name,

            "category_id": subcategory.parent.id,
            "category_name": subcategory.parent.name,

            "group_id": subcategory.parent.parent.id,
            "group_name": subcategory.parent.parent.name

        }
        for subcategory in SubCategory.objects.filter(parent=category_id)]

    return Response({"subcategories": subcategories})


@api_view(['POST'])
def find_subcategory_by_name(request):
    '''
    :param request:
        {
            "name": "",
            "category_id": id
        }
    :return:
        {
            "subcategories": [{"subcategory_name": str, "subcategory_id": id}]
        }
    '''
    name = request.data.get('name', '')
    category_id = request.data.get('category_id', 0)
    out_vars = {
        'subcategories': [{"subcategory_name": s.name, "subcategory_id": s.id}
        for s in SubCategory.objects.filter(name__icontains=name, parent=category_id)]
    }

    return Response(out_vars)


@api_view(['POST'])
def get_path_for_subcategory(request):
    '''
    :param request:
    {"subcategory_id": id}
    :return:
    {
        'subcategory_id': id,
        'subcategory_name': str,

        'category_id': id,
        'category_name': str,

        'group_id': id,
        'group_name': str
    }
    '''
    subcategory_id = request.data.get("subcategory_id", 0)
    subcategory = SubCategory.objects.filter(id=subcategory_id).first()

    if subcategory:
        path = {
            "subcategory_id": subcategory.id,
            "subcategory_name": subcategory.name,
            "category_id": subcategory.parent.id,
            "category_name": subcategory.parent.name,
            "group_id": subcategory.parent.parent.id,
            "group_name": subcategory.parent.parent.name
        }
    else:
        path = {}

    return Response(path)


@api_view(['POST'])
def get_all_types_in_category(request):
    '''
    :param request:
    {
        "category_id": id
    }
    :return:
    {
        'types': [
            {
                'type_id': id,
                'type_name': str,

                'category_id': id,
                'category_name': str
            }
            ]
    '''
    category_id = request.data.get('category_id', 0)

    types = [
        {
            "type_id": type.id,
            "type_name": type.name,

            "category_id": type.category.id,
            "category_name": type.category.name
         }
        for type in TypeInCategory.objects.filter(category_id=category_id)]

    return Response({"types": types})


@api_view(['POST'])
@permission_classes((IsAuthenticated, IsBusiness, ))
def create_new_types_for_categories(request):
    '''
    :param request:
    {
        "types_list": [
        {
            "type_name": str,
            "category_id": id
        },
        ]
    }
    :return:
        [
        {
            "id": id,
            "name": str
        }
        ]
    '''
    types_list = request.data.get('types_list', [])
    out_vars = []
    exists = []
    for t in types_list:
        name = t.get('type_name', '')
        category_id = t.get('category_id', 0)

        try:
            category = Category.objects.get(id=category_id)
        except Category.DoesNotExist:
            return Response({"error": "Category not found"}, status=404)

        type, created = TypeInCategory.objects.get_or_create(
            name=name,
            category=category
        )
        type.save()

        if not created:
            exists.append(name)

        out_vars.append(
            {
                "id": type.id,
                "name": type.name
            }
        )

    if len(exists) > 0:
        return Response({"message": "Category {0} already has such types: {1}".format(category.name, exists)})

    return Response({"types_list": out_vars})


@api_view(['GET'])
def get_catalog_tree(request):
    '''
    :param request:
    :return:
    [
        {
            'group_id': id,
            'group_name': str

            'category_id': id,
            'category_name': str,

            'subcategory_id': id,
            'subcategory_name': str,

            'type_id': id,
            'type_name': str,
        }
    ]
    '''

    groups = Group.objects.all()
    categories = Category.objects.all()
    subcategories = SubCategory.objects.all()
    types_in_cat = TypeInCategory.objects.all()

    cats = lambda g_id: categories.filter(parent_id=g_id)
    subcats = lambda c_id: subcategories.filter(parent_id=c_id)
    types = lambda c_id: types_in_cat.filter(category_id=c_id)

    tree = [{"group_id": group.id,
           "group_name": group.name,
           "categories": [{"category_id": category.id,
                           "category_name": category.name,
                           "types": [
                               {"type_id": t.id,
                                "type_name": t.name}
                               for t in types(category.id)
                                ],
                           "subcategories": [
                               {"subcategory_id": subcategory.id,
                                "subcategory_name": subcategory.name
                                }
                                for subcategory in subcats(category.id)
                                ]
                           } for category in cats(group.id)]
        } for group in groups]

    return Response(tree)





















