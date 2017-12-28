# -*- coding: utf-8 -*-
import re

from datetime import datetime

from django.core.exceptions import ValidationError
from django.db.models import Q
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.status import HTTP_200_OK

from bank.models import Currency
from catalog.models import (
    SubCategory, TypeInCategory,
    ClassProduct, ProductType,
    Product, ImgProduct,
    TagsForProduct,
    PickUpAddressForProduct,
    MEASURE)
from core.permissions import IsBusiness
from core.tools import product_photo_upload, file_remover
from catalog.tools import sintez_json_from_product
from geodata.models import Country
from userdata.models import ProfileBusiness, AddressPickUp, ClassProductForProfile


@api_view(['POST'])
@permission_classes((IsAuthenticated, IsBusiness, ))
def add_product_by_seller_step_one(request):
    """
    :param request:
    {
        "name": "",
        "description": "",
        "price": 10.15,
        "subcategory": 1,

        "name_en": "",
        "currency": 1,
        "weight_of_pack": 3.5,
        "measure": 2,
        "measure_count": 5,
        "description_en": "",
        "country": 73,
        "region": "",
        "nondurable": "True",
        "expiry_days": 28,
        "photos": [{"photo": "", "avatar": false}],
        "video": "",
        "number_of_packages": 150,
        "discount_price": 9.99,
        "start_of_sales_date": "2017-11-12",
        "end_of_sales_date": "2017-11-30"
    }
    :return:
    """
    profile_business = ProfileBusiness.objects.get(profile__user=request.user)

    name = request.data.get('name')
    description = request.data.get('description')
    price = request.data.get('price')
    subcategory = request.data.get('subcategory', 0)
    currency = request.data.get('currency', 1)

    name_en = request.data.get('name_en')
    weight_of_pack = request.data.get('weight_of_pack', 0)
    measure = request.data.get('measure', 1)
    measure_count = request.data.get('measure_count', 0)
    number_of_packages = request.data.get('number_of_packages', 0)
    discount_price = request.data.get('discount_price', 0)
    description_en = request.data.get('description_en', "")
    made_in = request.data.get('country')
    region = request.data.get('region')
    nondurable = request.data.get('nondurable', False)
    expiry_days = request.data.get('expiry_days', 0)

    start_of_sales_date = request.data.get('start_of_sales_date')
    end_of_sales_date = request.data.get('end_of_sales_date')

    photos = request.data.get('photos', [])
    video = request.data.get('video', '')

    if type(weight_of_pack) == str:
        weight_of_pack = float(weight_of_pack.replace(',', '.'))

    if not name:
        return Response({'error': 'Empty name'}, status=400)

    if not description:
        return Response({'error': 'Empty description'}, status=400)

    if not price:
        return Response({'error': 'Empty price'}, status=400)

    try:
        subcategory = SubCategory.objects.get(id=subcategory)
    except SubCategory.DoesNotExist:
        return Response({'error': 'Incorrect subcategory id'}, status=404)

    try:
        currency = Currency.objects.get(id=currency)
    except Currency.DoesNotExist:
        return Response({'error': 'Incorrect currency id'}, status=404)

    if made_in:
        country = Country.objects.filter(id=made_in).first()
    else:
        country = None

    n = False
    if nondurable:
        n = nondurable.lower() == "true"

    if start_of_sales_date:
        try:
            start_of_sales_date = datetime.strptime(start_of_sales_date, '%Y-%m-%d')
        except ValueError:
            return Response('Incorrect start_of_sales_date format', 400)

    if end_of_sales_date:
        try:
            end_of_sales_date = datetime.strptime(end_of_sales_date, '%Y-%m-%d')
        except ValueError:
            return Response('Incorrect end_of_sales_date format', 400)

    if not discount_price:
        discount_price = 0
    #
    # if not photos:
    #     return Response({'error': 'You should select photo.'.format(Product.IMG_COUNT)}, status=400)

    if len(photos) > Product.IMG_COUNT:
        return Response({'error': 'You can attach only {0} images for product.'.format(Product.IMG_COUNT)}, status=400)

    product = Product(
        profile_business=profile_business,
        category=subcategory,
        currency=currency,
        name=name,
        name_en=name_en,
        description=description,
        description_en=description_en,
        number_of_packages=number_of_packages,
        weight_of_pack=weight_of_pack,
        nondurable=n,
        expiry_days=expiry_days,
        measure=measure,
        measure_count=measure_count,
        price=re.sub(r'\D', '.', str(price)),
        discount_price=re.sub(r'\D', '.', str(discount_price)),
        video=video,
        country=country,
        region=region,
        start_of_sales_date=start_of_sales_date,
        end_of_sales_date=end_of_sales_date,
    )
    product.save()

    if photos:
        a = False
        for ph in photos:
            photo = product_photo_upload(ph.get('photo'), product.id)
            if ph.get('avatar'):
                a = True
            ImgProduct(
                avatar=ph.get('avatar'),
                product=product,
                img=photo
            ).save()

        if not a:
            av = ImgProduct.objects.filter(product=product).first()
            av.avatar = True
            av.save()

    return Response({'product': sintez_json_from_product(product)})


@api_view(['POST'])
@permission_classes((IsAuthenticated, IsBusiness, ))
def update_product_by_seller(request):
    """
    :param request:
    {
        "product": 1,
        "name": "",
        "description": "",
        "price": 10.15,
        "subcategory": 1,
        "name_en": "",
        "currency": 1,
        "weight_of_pack": 3.5,
        "measure": 2,
        "measure_count": 5,
        "description_en": "",
        "country": 73,
        "region": "",
        "nondurable": "True",
        "expiry_days": 28,
        "video": "https://www.google.ru/",
        "number_of_packages": 150,
        "discount_price": 9.99,
        "start_of_sales_date": "2017-11-12",
        "end_of_sales_date": "2017-11-30"
    }
    :return:
    HTTP_200_OK
    """
    prod = request.data.get('product')
    name = request.data.get('name')
    name_en = request.data.get('name_en')
    subcategory = request.data.get('subcategory')
    currency = request.data.get('currency')
    description = request.data.get('description')
    description_en = request.data.get('description_en')
    number_of_packages = request.data.get('number_of_packages')
    weight_of_pack = request.data.get('weight_of_pack')
    nondurable = request.data.get('nondurable')
    expiry_days = request.data.get('expiry_days')
    measure = request.data.get('measure')
    measure_count = request.data.get('measure_count')
    price = request.data.get('price')
    discount_price = request.data.get('discount_price')
    country = request.data.get('country')
    region = request.data.get('region')
    video = request.data.get('video')
    start_of_sales_date = request.data.get('start_of_sales_date')
    end_of_sales_date = request.data.get('end_of_sales_date')

    product = Product.objects.filter(id=prod, profile_business__profile__user=request.user).first()
    if not product:
        return Response({"error": "incorrect product"})
    if name:
        product.name = name

    if name_en:
        if name_en == 'delete':
            product.name_en = None
        else:
            product.name_en = name_en

    if subcategory:
        c = SubCategory.objects.filter(id=subcategory).first()
        if c:
            product.category = c
        else:
            return Response({"error": "Incorrect subcategory"})

    if currency:
        c = Currency.objects.filter(id=currency).first()
        if c:
            product.currency = c
        else:
            return Response({"error": "Incorrect currency"})
    if description:
        product.description = description

    if description_en:
        if description_en == 'delete':
            product.description_en = None
        else:
            product.description_en = description_en

    if number_of_packages:
        product.number_of_packages = number_of_packages
    if weight_of_pack:
        product.weight_of_pack = weight_of_pack
    if nondurable:
        product.nondurable = nondurable.lower() == "true"
    if expiry_days:
        product.expiry_days = expiry_days
    a = [i[0] for i in MEASURE]
    if expiry_days:
        product.expiry_days = expiry_days
    if measure in a:
        product.measure = measure
    if measure_count:
        product.measure_count = measure_count
    if price:
        product.price = re.sub(r'\D', '.', str(price))

    if discount_price:
        if discount_price == 'delete':
            product.discount_price = None
        else:
            product.discount_price = re.sub(r'\D', '.', str(discount_price))

    if region:
        if region == 'delete':
            product.region = None
        else:
            product.region = region

    if video:
        if video == 'delete':
            product.video = None
        else:
            product.video = video
    if country:
        if country == 'delete':
            product.country = None
        else:
            c = Country.objects.filter(id=country).first()
            if c:
                product.country = c
            else:
                return Response({"error": "Incorrect country id"})

    if start_of_sales_date:
        if start_of_sales_date == 'delete':
            product.start_of_sales_date = None
        else:
            try:
                start_of_sales_date = datetime.strptime(start_of_sales_date, '%Y-%m-%d')
            except ValueError:
                return Response('Incorrect start_of_sales_date format', 400)
            product.start_of_sales_date = start_of_sales_date

    if end_of_sales_date:
        if end_of_sales_date == 'delete':
            product.end_of_sales_date = None
        else:
            try:
                end_of_sales_date = datetime.strptime(end_of_sales_date, '%Y-%m-%d')
            except ValueError:
                return Response('Incorrect end_of_sales_date format', 400)
            product.end_of_sales_date = end_of_sales_date

    product.save()
    return Response({'product': sintez_json_from_product(product)})


@api_view(['POST'])
@permission_classes((IsAuthenticated, IsBusiness, ))
def delete_products(request):
    """
    :param request:
    {"products": [1, 2]}
    :return:
    """
    products = request.data.get('products', [])

    correct_ids = []
    wrong_ids = []
    for pr in products:
        try:
            prod = Product.objects.get(profile_business__profile__user=request.user, id=pr)
        except Product.DoesNotExist:
            wrong_ids.append(pr)
        else:
            correct_ids.append(pr)
            prod.mark_deleted = True
            prod.save()
    msg = ''

    if len(wrong_ids) > 0:
        msg = 'Products - {0} - not found'.format(wrong_ids)

    return Response({'answer': 'Marked as deleted: {0}. {1}'.format(correct_ids, msg)})


@api_view(['POST'])
@permission_classes((IsAuthenticated, IsBusiness, ))
def delete_product(request):
    """
    :param request:
    {
        "product_id": 1
    }
    :return:
    """
    product_id = request.data.get('product_id', 0)

    product = Product.objects.filter(profile_business__profile__user=request.user, id=product_id).first()

    if not product:
        return Response({"error": "Product not found"}, status=404)

    product.mark_deleted = True
    product.save()

    return Response(HTTP_200_OK)


@api_view(['POST'])
def get_product(request):
    """
    :param request:
    {
        "product_id": 0
    }
    :return:
    """
    product_id = request.data.get('product_id', 0)

    product = Product.objects.filter(id=product_id).first()
    if not product:
        return Response({"error": "Product not found"}, status=400)

    return Response({'product': sintez_json_from_product(product)})


@api_view(['POST'])
@permission_classes((IsAuthenticated, IsBusiness, ))
def add_class_for_product(request):
    """
    :param request:
    {
        "product": 1, "class":[1, 2, 3]
    }
    :return:
    """
    product = request.data.get('product')
    class_prod = request.data.get('class')

    all_class = [i[0] for i in ClassProductForProfile.CLASS_PROD]

    prod = Product.objects.filter(id=product, profile_business__profile__user=request.user).first()
    if not prod:
        return Response({"error": "Product not found"}, status=404)

    for cl in class_prod:
        if cl in all_class:
            cl_prod, create = ClassProduct.objects.get_or_create(
                name=cl,
                product_id=product
            )
            cl_prod.save()

    return Response(HTTP_200_OK)


@api_view(['POST'])
@permission_classes((IsAuthenticated, IsBusiness, ))
def del_class_for_product(request):
    """
    :param request:
    {
        "product": 1, "class":[1,2,3]
    }
    :return:
    """
    product = request.data.get('product', 0)
    class_prod = request.data.get('class', [0])

    all_class = [i[0] for i in ClassProductForProfile.CLASS_PROD]

    prod = Product.objects.filter(id=product, profile_business__profile__user=request.user).first()
    if not prod:
        return Response({"error": "Product not found"}, status=404)

    for cl in class_prod:
        if cl in all_class:
            class_for_prod = ClassProduct.objects.filter(name=cl, product_id=product).first()
            if class_for_prod:
                class_for_prod.delete()

    return Response(HTTP_200_OK)


@api_view(['POST'])
@permission_classes((IsAuthenticated, IsBusiness, ))
def get_product_class(request):
    """
    :param request:
    {
        "product": 1
    }
    :return:

    """
    product = request.data.get('product', 0)
    if not product:
        return Response({"error": "Empty product id"}, status=400)
    prod = Product.objects.filter(id=product).first()
    if not prod:
        return Response({"error": "Product not found"}, status=404)

    prod_class =[{"id": c.id, "name": c.name} for c in ClassProduct.objects.filter(product_id=product)]

    return Response(prod_class)


@api_view(['POST'])
@permission_classes((IsAuthenticated, IsBusiness, ))
def add_type_for_product(request):
    """
    :param request:
    {
        "product":1,
        "type":[1,]
    }
    :return:
    """
    product = request.data.get('product', 0)
    types = request.data.get('type', [0])

    prod = Product.objects.filter(id=product, profile_business__profile__user=request.user).first()
    if not prod:
        return Response({"error": "Product not found"}, status=404)

    correct_ids = []
    wrong_ids = []

    for t_id in types:
        pr_type = TypeInCategory.objects.filter(id=t_id).first()
        if not pr_type:
            wrong_ids.append(t_id)
        else:
            correct_ids.append(t_id)
            type_for_prod, create = ProductType.objects.get_or_create(
                type=pr_type,
                product=prod
            )
            type_for_prod.save()

    msg = ''
    if len(wrong_ids) > 0:
        msg = 'Types - {0} - not found'.format(wrong_ids)

    return Response({'answer': 'Types added for product: {0}. {1}'.format(correct_ids, msg)})


@api_view(['POST'])
@permission_classes((IsAuthenticated, IsBusiness, ))
def del_type_for_product(request):
    """
    :param request:
    {
        "product": 1,
        "type":[1]
    }
    :return:
    """
    product = request.data.get('product', 0)
    types = request.data.get('type', [0])

    for t_id in types:
        type_for_prod = ProductType.objects.filter(
            product__profile_business__profile__user=request.user,
            type=t_id,
            product=product
        )
        type_for_prod.delete()

    return Response(HTTP_200_OK)


@api_view(['POST'])
@permission_classes((IsAuthenticated, IsBusiness, ))
def add_tags_for_product(request):
    """
    :param request:
    {
        "product": 1,
        "tag": "какой-нибудь тэг"
    }
    :return:
    """
    product_id = request.data.get('product', 0)
    tags = request.data.get('tags', 0)

    product = Product.objects.filter(id=product_id, profile_business__profile__user=request.user).first()
    if not product:
        return Response({"error": "Product not found"}, status=404)

    tag = TagsForProduct.objects.create(
        product=product,
        name=tags
    )
    tag.save()

    return Response({"tag_id": tag.id})


@api_view(['POST'])
@permission_classes((IsAuthenticated, IsBusiness, ))
def del_tags_from_product(request):
    """
    :param request:
    {
        "product": 1,
        "tags": [1, 2]
    }
    :return:
    """
    product_id = request.data.get('product', 0)
    tag_ids = request.data.get('tags', [0])

    product = Product.objects.filter(id=product_id, profile_business__profile__user=request.user).first()
    if not product:
        return Response({"error": "Product not found"}, status=404)

    wrong_ids = []
    correct_ids = []
    for t in tag_ids:
        tag = TagsForProduct.objects.filter(product=product, id=t).first()

        if tag:
            tag.delete()
            correct_ids.append(t)
        else:
            wrong_ids.append(t)

    if len(wrong_ids) > 0:
        msg = 'Tags not found: {0}.'.format(wrong_ids)
    return Response({'answer': 'Tags deleted from product: {0}. {1}'.format(correct_ids, msg)})


@api_view(['POST'])
@permission_classes((IsAuthenticated, IsBusiness, ))
def get_tags_for_product(request):
    """
    :param request:
    {
        "product": 1
    }
    :return:
    """
    product_id = request.data.get('product', 0)

    product = Product.objects.filter(id=product_id, profile_business__profile__user=request.user).filter()
    if not product:
        return Response({"error": "Product not found"}, status=404)

    all_tags = [{"id": t.id, "name": t.name} for t in TagsForProduct.objects.filter(product=product)]

    return Response(all_tags)


@api_view(['POST'])
@permission_classes((IsAuthenticated, IsBusiness, ))
def add_pickup_address_for_product(request):
    """
    :param request:
    {
        "product_id": id, "pickup_address_id": id
    }
    :return:
    """
    product_id = request.data.get("product_id", 0)
    pickup_address_id = request.data.get("pickup_address_id", 0)

    product = Product.objects.filter(id=product_id, profile_business__profile__user=request.user).first()
    pickup_address = AddressPickUp.objects.filter(id=pickup_address_id, profile__profile__user=request.user).first()

    if product and pickup_address:
        pu_addr, created = PickUpAddressForProduct.objects.get_or_create(
            product=product,
            address=pickup_address
        )

        if not created:
            return Response({"message": "Product {0} already has such pickup address".format(product_id)})
        else:
            pu_addr.save()

        return Response(HTTP_200_OK)
    else:
        return Response({"error": "Product_id or pickup_address_id is incorrect"}, status=400)


@api_view(['POST'])
@permission_classes((IsAuthenticated, IsBusiness, ))
def delete_pickup_address_from_product(request):
    """
    :param request:
        {
            "product_id": 1,
            "pickup_address_id": 1
        }
    :return: HTTP 200 OK
    """
    user = request.user
    product_id = request.data.get("product_id", 0)
    pickup_address_id = request.data.get("pickup_address_id", 0)
    addr = PickUpAddressForProduct.objects.filter(
        product__profile_business__profile__user=user,
        product_id=product_id,
        address_id=pickup_address_id
    )

    if not addr:
        return Response({"message": "Address not found"})

    addr.delete()
    return Response(HTTP_200_OK)


@api_view(['POST'])
@permission_classes((IsAuthenticated, IsBusiness, ))
def add_product_image(request):
    """
    :param request:
    {
        "product_id": 1,
        "avatar": false,
        "photo": ""
    }
    :return:
    """
    product_id = request.data.get('product_id', 0)
    photo = request.data.get('photo', '')
    avatar = request.data.get('avatar', False)

    product = Product.objects.filter(id=product_id, profile_business__profile__user=request.user).first()
    if not product:
        return Response({'error': 'Product not found'}, status=404)

    if ImgProduct.objects.filter(product=product).count() == Product.IMG_COUNT:
        return Response({'error': 'Product already has {0} images'.format(Product.IMG_COUNT)}, status=400)

    image = product_photo_upload(photo, product.id)
    product_img = ImgProduct(
        product=product,
        img=image
    )

    if avatar:
        ImgProduct.objects.filter(product__profile_business__profile__user=request.user).update(avatar=False)
        product_img.avatar = True

    try:
        product_img.save()
    except ValidationError:
        return Response({'error': 'You can attach only {0} pictures to the product!'.format(Product.IMG_COUNT)}, status=404)

    return Response({"id": product_img.id,
                     "url": product_img.img.url,
                     "created": product_img.created.strftime('%H:%M:%S %Y-%m-%d'),
                     "avatar": product_img.avatar})


@api_view(['POST'])
@permission_classes((IsAuthenticated, IsBusiness, ))
def update_product_image(request):
    """
    :param request:
    {
        "product_id": 1,
        "photo_id": 1,
        "avatar": false,
        "new_photo": ""
    }
    :return:
    """
    product_id = request.data.get('product_id', 0)
    photo_id = request.data.get('photo_id', 0)
    new_photo = request.data.get('new_photo')
    avatar = request.data.get('avatar', False)

    product = Product.objects.filter(id=product_id, profile_business__profile__user=request.user).first()
    if not product:
        return Response({'error': 'Product not found'}, status=404)

    prod_image = ImgProduct.objects.filter(id=photo_id, product__profile_business__profile__user=request.user).first()

    if not prod_image:
        return Response({'error': 'Image not found'}, status=404)

    file_remover(prod_image.img.url)
    if new_photo:
        image = product_photo_upload(new_photo, product.id)
        prod_image.image = image

    if avatar:
        ImgProduct.objects.filter(product__profile_business__profile__user=request.user).update(avatar=False)
        prod_image.avatar = True

    prod_image.save()

    return Response({"id": prod_image.id,
                     "url": prod_image.img.url,
                     "created": prod_image.created.strftime('%H:%M:%S %Y-%m-%d'),
                     "avatar": prod_image.avatar})


@api_view(['POST'])
@permission_classes((IsAuthenticated, IsBusiness, ))
def delete_product_image(request):
    """
    :param request:
    {
        "product_id": 1,
        "photo_id": 1
    }
    :return:
    """
    product_id = request.data.get('product_id', 0)
    photo_id = request.data.get('photo_id', 0)

    product = Product.objects.filter(id=product_id, profile_business__profile__user=request.user).first()
    if not product:
        return Response({'error': 'Product not found'}, status=404)

    prod_images = ImgProduct.objects.filter(product__profile_business__profile__user=request.user)

    prod_image = prod_images.filter(id=photo_id).first()

    if not prod_image:
        return Response({'error': 'Image not found'}, status=404)

    if prod_image.avatar:
        prod_images.update(avatar=False)
        avatar_image = prod_images.filter(~Q(id=prod_image.id)).first()
        avatar_image.avatar = True
        avatar_image.save()

    file_remover(prod_image.img.url)
    prod_image.delete()

    return Response(HTTP_200_OK)


@api_view(['POST'])
@permission_classes((IsAuthenticated, IsBusiness, ))
def add_types_for_product(request):
    """
    :param request:
    {"product_id": id, "types": [id,]}
    :return:
    """
    product_id = request.data.get('product_id', 0)
    types = request.data.get('types', [])

    try:
        product = Product.objects.get(id=product_id)
    except Product.DoesNotExist:
        return Response({"error": "Product {0} not found".format(product_id)}, status=404)

    correct_list = []
    incorrect_list = []
    for t in types:
        pr_type = TypeInCategory.objects.filter(id=t).first()
        if not pr_type:
            incorrect_list.append(t)
        else:
            prod_type, created = ProductType.objects.get_or_create(
                product=product,
                type=pr_type
            )
            prod_type.save()
            correct_list.append(prod_type.type.name)

    return Response(HTTP_200_OK)


@api_view(['POST'])
@permission_classes((IsAuthenticated, IsBusiness, ))
def delete_types_from_product(request):
    """
    :param request:
        {
            "product_id": id,
            "types": [id,]
        }
    :return:
        {
            "message": "0 types were deleted: [int]"
        }
    """
    user = request.user
    product_id = request.data.get('product_id', 0)
    types = request.data.get('types', [])

    deleted_types = []
    for t in types:
        prod_type = ProductType.objects.filter(
            product__profile_business__profile__user=user,
            product_id=product_id,
            type_id=t
        )
        if len(prod_type) > 0:
            deleted_types.append(t)

        prod_type.delete()

    return Response({"message": "{0} types were deleted: {1}".format(len(deleted_types), deleted_types)})










