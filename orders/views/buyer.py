# -*- coding: utf-8 -*-
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import api_view, permission_classes

from orders.models import *
from catalog.models import Product
from geodata.models import Country
from orders.tools import *


@api_view(['POST'])
@permission_classes((IsAuthenticated,))
def add_product_to_cart(request):
    '''
    :param request:
    {
        "product": 1,
        "delivery_type": 1,
        "amount": 2,
        "ship_to": 1
    }
    :return:
    '''
    profile = request.user.profile
    product_id = request.data.get('product')
    delivery_type = request.data.get('delivery_type', 1)
    amount = request.data.get('amount', 0)
    ship_to = request.data.get('ship_to', 0)

    product = Product.objects.filter(id=product_id).first()
    if not product:
        return Response({"error": "Incorrect product id"}, status=404)

    seller = product.profile_business
    country = Country.objects.filter(id=ship_to).first()
    if not country:
        return Response({"error": "Invalid country id"}, status=404)

    all_orders = Order.objects.filter(profile=profile,
                                 seller=seller,
                                 delivery_type=delivery_type,
                                 ship_to=ship_to)
    order = None
    for o in all_orders:
        #ищем подходящий заказ с последним статусом == 1 (корзина)
        order_status = OrderStatus.objects.filter(order=o).order_by('-id').first()
        if order_status.status == 1:
            order = o

    if not order:
        order = Order.objects.create(
            profile=profile,
            seller=seller,
            delivery_type=delivery_type,
            ship_to=country,
        )

    prod, create = AmountProduct.objects.get_or_create(
        product=product,
        order=order
    )
    am = prod.amount + int(amount)

    if am > prod.product.number_of_packages:
        return Response({"error": "Trying to order more then owher has"}, status=400)

    prod.amount = am
    # prod.delivery_price = calculate_delivery(product, prod.amount, delivery_type)
    prod.save()

    return Response(cart_json(order, ship_to))


@api_view(['POST'])
@permission_classes((IsAuthenticated,))
def delete_product_from_cart(request):
    '''
    :param request:
    {
        "order_id": 1,
        "product_id": 1,
        "ship_to": 1
    }
    :return:
    '''
    order_id = request.data.get('order_id')
    product_id = request.data.get('product_id')
    ship_to = request.data.get('ship_to')

    if not order_id:
        return Response({"error": "Empty order_id"}, status=400)
    if not product_id:
        return Response({"error": "Empty product_id"}, status=400)

    order_status = OrderStatus.objects.filter(order=order_id,
                                              order__profile__user=request.user).order_by('-id').first()
    if not order_status.status == 1:
        return Response({"error": "Order already paid"}, status=400)

    try:
        product_in_order = AmountProduct.objects.get(order=order_id,
                                                     order__profile=request.user.profile,
                                                     product=product_id)
    except AmountProduct.DoesNotExist:
        return Response({"error": "Incorrect order id or product id"})

    product_in_order.delete()

    order_exists = AmountProduct.objects.filter(order=order_id,
                                                order__profile=request.user.profile).exists()
    if not order_exists:
        Order.objects.filter(id=order_id).delete()
        return Response({"message": "Order was deleted"})

    # check_cart(product_in_order.cart.id)

    return Response(cart_json(Order.objects.get(id=order_id), ship_to))


@api_view(['POST'])
@permission_classes((IsAuthenticated,))
def update_count_of_products_in_cart(request):
    '''
    :param request:
    {
        "order_id":1,
        "product_id": 1,
        "amount": 23,
        "ship_to": 1
    }
    :return:
    '''
    order_id = request.data.get('order_id')
    product_id = request.data.get('product_id')
    amount = request.data.get('amount', 0)
    ship_to = request.data.get('ship_to', 0)

    if not order_id:
        return Response({"error": "Empty order_id"}, status=400)
    if not product_id:
        return Response({"error": "Empty product_id"}, status=400)

    country = Country.objects.filter(id=ship_to).first()
    if not country:
        return Response({"error": "Incorrect country id (ship_to)"}, status=404)

    order_status = OrderStatus.objects.filter(order=order_id,
                                              order__profile__user=request.user).order_by('-id').first()
    if not order_status:
        return Response({"error": "Incorrect order id"}, status=404)

    if not order_status.status == 1:
        return Response({"error": "Order already paid. You can not change order."}, status=400)

    amount = int(amount)
    try:
        product = AmountProduct.objects.get(order=order_id, order__profile__user=request.user, product=product_id)
    except AmountProduct.DoesNotExist:
        return Response({"error": "User has not cart with such id and such product"})

    if amount == 0:
        product.delete()
    else:
        if product.amount > product.product.number_of_packages:
            return Response({"error": "Trying to order more than owner has"}, status=400)
        product.amount = amount
        product.save()

    order_exists = AmountProduct.objects.filter(order=order_id, order__profile=request.user.profile).exists()
    if not order_exists:
        Order.objects.filter(id=order_id).delete()
        return Response({"message": "Order was deleted"})

    return Response(cart_json(Order.objects.get(id=order_id), ship_to))


@api_view(['POST'])
@permission_classes((IsAuthenticated,))
def get_my_carts(request):
    '''
    :param request:
    {
        "ship_to": 1
    }
    :return:
    '''
    ship_to = request.data.get('ship_to')

    if not ship_to:
        return Response({"error": "Empty ship_to"}, status=400)

    actual_statuses = [OrderStatus.objects.filter(order=o).order_by('-id').first()
                       for o in Order.objects.filter(profile__user=request.user)]
    carts = [s.order for s in actual_statuses if s.status == 1]

    return Response([cart_json(c, ship_to) for c in carts])


@api_view(['POST'])
@permission_classes((IsAuthenticated,))
def get_cart(request):
    '''
    :param request:
    {
        "ship_to": 1,
        "order_id": 1
    }
    :return:
    '''
    ship_to = request.data.get("ship_to", 0)
    order_id = request.data.get("order_id", 0)

    if not ship_to:
        return Response({"error": "Empty ship_to"}, status=400)

    order_status = OrderStatus.objects.filter(order=order_id,
                                              order__profile__user=request.user).order_by('-id').first()
    if not order_status:
        return Response({"error": "Incorrect order_id"}, status=404)

    if not order_status.status == 1:
        return Response({"error": "Order already paid"}, status=400)

    cart = Order.objects.filter(id=order_id).first()

    return Response(cart_json(cart, ship_to))


@api_view(['POST'])
@permission_classes((IsAuthenticated,))
def checkout(request):
    '''
    :param request:
    {
        "order_id": 1,
        "payment_method": 1,
        "delivery_addr_id": 1,
        "payment_address_id": 1
    }
    :return:
    '''
    order_id = request.data.get('order_id', 0)
    payment_method = request.data.get('payment_method')
    delivery_addr_id = request.data.get('delivery_addr_id', 0)
    payment_address_id = request.data.get('payment_address_id', 0)
    # +детали оплаты

    # if payment_method not in Order.PAYMENT_METHOD_NAME:
    #     return Response({"error": "Incorrect payment method, should be in: {0}".format(Order.PAYMENT_METHOD_NAME)}, status=404)

    cart = Order.objects.filter(id=order_id, profile__user=request.user).first()
    if not cart:
        return Response({"error": "User does not have cart with such id"}, status=404)

    order_status = OrderStatus.objects.filter(order=cart).order_by('-id').first()

    if not order_status.status == 1:
        return Response({"error": "Order already paid"}, status=404)

    ship_to = AddressDeliveryProfile.objects.filter(id=delivery_addr_id).first()
    if not ship_to:
        return Response({"error": "Incorrect delivery address"}, status=404)

    payment_address = AddressPayment.objects.filter(id=payment_address_id).first()
    if not payment_address:
        return Response({"error": "Incorrect payment address"}, status=404)

    cart.ship_to = ship_to.city.region.country
    cart.number = generate_order_number(cart, ship_to.city.region.country)
    cart.payment_method = payment_method
    cart.payment_status = True
    cart.payment_address = payment_address
    cart.shipping_address = ship_to
    cart.save()

    OrderStatus(order=cart, status=2).save()

    return Response(order_json_for_buyer(cart, ship_to.city.region.country))


@api_view(['GET'])
@permission_classes((IsAuthenticated,))
def get_my_orders(request):
    actual_statuses = [OrderStatus.objects.filter(order=o).order_by('-id').first()
                       for o in Order.objects.filter(profile__user=request.user)]

    orders = [s.order for s in actual_statuses if s.status != 1]

    return Response([order_json_for_buyer(o) for o in orders])

