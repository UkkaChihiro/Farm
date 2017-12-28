# -*- coding: utf-8 -*-
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import api_view, permission_classes
from rest_framework.status import HTTP_200_OK

from core.permissions import IsBusiness

from orders.tools import *


@api_view(['POST'])
@permission_classes((IsAuthenticated, IsBusiness))
def update_order_status(request):
    '''
        (1, 'new'),
        (2, 'paid for'),
        (3, 'ready to ship'),
        (4, 'canceled'),
        (5, 'shipped'),
        (6, 'delivered'),
        (7, 'failed')
    :param request:
    {
        "order_id": 1,
        "status": 3,
        "notify_cust": true,
        "tracking_num": "",
        "comment": ""
    }
    :return:
    '''
    order_id = request.data.get('order_id', 0)
    new_status = request.data.get('status', 0)
    notify_cust = request.data.get('notify_customer', False)
    tracking_num = request.data.get('tracking_num', None)
    comment = request.data.get('comment', "")

    available_statuses = [num for (num, name) in OrderStatus.ORDER_STATUS][2:]
    if new_status not in available_statuses:
        return Response({"error": "Incorrect status"}, status=400)

    if new_status == 5:
        if not tracking_num:
            return Response({"error": "Empty tracking number"}, status=400)

    order_status = OrderStatus.objects.filter(order=order_id).order_by('-id').first()
    if order_status.status == 1:
        return Response({"error": "Order still not paid for"}, status=400)

    order = Order.objects.filter(id=order_id, seller__profile__user=request.user).first()
    if not order:
        return Response({"error": "Incorrect order id"}, status=404)

    order_status = OrderStatus(
        order=order,
        status=new_status,
        tracking_number=tracking_num,
        customer_notificated=notify_cust,
        comment=comment
    )
    order_status.save()

    return Response(HTTP_200_OK)


@api_view(['POST'])
@permission_classes((IsAuthenticated, IsBusiness,))
def get_my_sales(request):
    '''
    None, 2, 3, 4, 5, 6, 7
    :param request:
    {
        "status": 2
    }
    :return:
    '''
    status = request.data.get('status')

    actual_statuses = [OrderStatus.objects.filter(order=o).order_by('-id').first()
                       for o in Order.objects.filter(seller__profile__user=request.user)]

    if status:
        orders = [s.order for s in actual_statuses if s.status == status]
    else:
        orders = [s.order for s in actual_statuses if s.status != 1]

    return Response([order_json_for_buyer(o) for o in orders])


@api_view(['POST'])
@permission_classes((IsAuthenticated, IsBusiness,))
def get_order_status_history(request):
    '''
    :param request:
    {
        "order_id": 2
    }
    :return:
    '''

    order_id = request.data.get('order_id')
    order = Order.objects.filter(seller__profile__user=request.user, id=order_id).first()
    status_list = OrderStatus.objects.filter(order=order).order_by('-id')

    out_vars = [{
                "order_id": s.order.id,
                "status": s.status,
                "comment": s.comment,
                "customer_notification": s.customer_notificated,
                "tracking_number": s.tracking_number,
                "date_added": s.date_added.strftime('%H:%M:%S %Y-%m-%d')
                } for s in status_list if s.status != 1] # исключаем неоплаченные заказы(корзины)

    return Response(out_vars)
