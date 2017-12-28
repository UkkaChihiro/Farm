# -*- coding: utf-8 -*-
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.status import HTTP_200_OK

from catalog.models import (
    Product, ImgProduct, VideoProduct,
    FavoriteProduct, ListOfFavorites)
from catalog.tools import sintez_json_from_product


@api_view(['POST'])
@permission_classes((IsAuthenticated,))
def add_product_to_favorites(request):
    product_id = request.data.get('product_id', 0)

    try:
        product = Product.objects.get(id=product_id)
    except Product.DoesNotExist:
        return Response({"error": "Product not found"}, status=400)

    fproduct, created = FavoriteProduct.objects.get_or_create(
        user=request.user,
        product=product
    )
    fproduct.save()

    return Response(HTTP_200_OK)


@api_view(['POST'])
@permission_classes((IsAuthenticated,))
def delete_product_from_favorites(request):
    product_id = request.data.get('product_id', 0)

    try:
        product = Product.objects.get(id=product_id)
    except Product.DoesNotExist:
        return Response({"error": "Product not found"}, status=400)

    fproduct = FavoriteProduct.objects.filter(
        user=request.user,
        product=product
    )
    fproduct.delete()

    return Response(HTTP_200_OK)


@api_view(['GET'])
@permission_classes((IsAuthenticated,))
def show_favorites(request):
    fproduct = FavoriteProduct.objects.filter(
        user=request.user
    )

    prod = []
    for i in fproduct:
        try:
            p = Product.objects.get(id=i.product.id)
        except Product.DoesNotExist:
            pass
        else:
            img = ImgProduct.objects.filter(product=p)
            photo = []
            if img.count > 0:
                for j in img:
                    photo.append(
                        {"img": j.img}
                    )

            videopr = VideoProduct.objects.filter(product=p)
            video = []
            if videopr.count > 0:
                for v in videopr:
                    # print('add video')
                    video.append(
                        {"video": v.video}
                    )

            prod.append(p)

    out_vars = {
        'products': list(map(
            sintez_json_from_product, prod
        ))
    }

    return Response(out_vars)


@api_view(['POST'])
@permission_classes((IsAuthenticated,))
def add_favorites_list(request):
    name_fl = request.data.get('name', False)

    if not name_fl:
        return Response({'error': 'Empty name of favorites list'}, status=400)

    flist = FavoriteProduct(
        user=request.user,
        name=name_fl
    )
    flist.save()
    return Response(HTTP_200_OK)


@api_view(['GET'])
@permission_classes((IsAuthenticated,))
def show_favorites_lists(request):
    flist = ListOfFavorites.objects.filter(user=request.user)

    list = []
    for i in flist:
        list.append({
            "id": i.id,
            "name": i.name,
            "user": i.user.username,
            "created": i.created
        })
    out_vars = {
        'flists':list
    }

    return Response(out_vars)


@api_view(['POST'])
@permission_classes((IsAuthenticated,))
def change_favorites_list(request):
    id_fl = request.data.get('id', 0)
    new_name = request.data.get('name', False)

    if not new_name:
        return Response({'error': 'Empty name of favorites list'}, status=400)

    try:
        flist = ListOfFavorites.objects.get(id=id_fl)
    except:
        return Response({'error': 'Incorrect id favorites list'}, status=400)
    flist.name = new_name
    flist.save()
    return Response(HTTP_200_OK)


@api_view(['POST'])
@permission_classes((IsAuthenticated,))
def delete_favorites_list(request):
    id_fl = request.data.get('id', 0)

    flist = FavoriteProduct.objects.filter(
        user=request.user,
        id=id_fl
    )
    if len(flist):
        return Response({"error": "User has not list with such id"})

    flist.delete()

    return Response(HTTP_200_OK)
