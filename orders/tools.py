from delivery.models import TarifsForCountry

from userdata.models import AddressLegal
from datetime import datetime
import re
from orders.models import AmountProduct, OrderStatus, Order


def generate_order_number(order, ship_to):
    '''
    номера заказов формируется следующим образом:
    DERU0717999990012345
    DE - страна фермера
    RU - страна покупателя
    07 - месяц продажи
    17 - год продажи
    9999900 - сумма заказа до центов
    123456 - номер заказ по порядку с каждого месяца, не ограниченное число цифр
    '''
    legaladdr = AddressLegal.objects.filter(profile=order.seller).first()
    if not legaladdr:
        pass

    code_seller = legaladdr.city.region.country.code

    code_buyer = ship_to.code
    dt = datetime.now()
    first_number = datetime(year=dt.year, month=dt.month, day=1)
    price = re.sub(r'\D', '', str(order_json_for_buyer(order, ship_to)['total_price']))
    number = Order.objects.filter(date_added__gte=first_number).count()

    return '{0}{1}{2}{3}{4}'.format(code_seller, code_buyer, str(dt.month), str(dt.year)[2:], price, str(number))


def calculate_delivery(product, amount, ship_to, type):
    # t[0]      t[1]      t[2]        t[3]
    # id        1 =       weight      price
    #           2 >
    #           3 ->

    parcel_weight = amount * product.weight_of_pack
    # print('parsel = {0}'.format(parcel_weight))
    tariff = TarifsForCountry.objects.filter(profile=product.profile_business, country=ship_to, type=type)\
                                     .values_list('id', 'mark', 'weight', 'price')
    # print('tariff = {0}'.format(tariff))
    # print('ship_to = {0}'.format(ship_to))

    hit_the_bull_s_eye = [t for t in tariff if t[1] == 1 and t[2] == parcel_weight]                         #1
    if hit_the_bull_s_eye:
        return TarifsForCountry.objects.get(id=hit_the_bull_s_eye[0][0]), float(hit_the_bull_s_eye[0][3])

    more = [t for t in tariff if t[1] == 2 and t[2] <= parcel_weight]                                       #2
    if more:
        more.sort(key=lambda x: x[2])
        return TarifsForCountry.objects.get(id=more[-1][0]), float(more[-1][3]) #*parcel_weight !!!

    step = [t for t in tariff if t[1] == 3]                                                                #3
    if step:
        equally = [t for t in tariff if t[1] == 1 and t[2] < parcel_weight]
        equally.sort(key=lambda x: x[2])                                    #(id,mark,weight,price)
        p = (((parcel_weight - equally[-1][2]) / step[0][2]) * float(step[0][3])) + float(equally[-1][3])
        return TarifsForCountry.objects.get(id=equally[-1][0]), p
                                                                                                            #4
    equally = [t for t in tariff if t[1] == 1 and t[2] < parcel_weight]

    if equally:
        equally.sort(key=lambda x: x[2])                                #(id,mark,weight,price)
        k = equally[-1][2]
        f = equally[-1][3]
        while k < parcel_weight:
            k *= 2
            p = f * 2
        return TarifsForCountry.objects.get(id=equally[-1][0]), p

    else: # если вес посылки меньше всех тарифов берем минимальный с маркой =
        equally = [t for t in tariff]# if t[1] == 1]

        if not equally: # если не найдено ни одного тарифа в эту страну
            return None, 0

        equally.sort(key=lambda x: x[2])
        p = float(equally[0][3])
        return TarifsForCountry.objects.get(id=equally[0][0]), p


def product_short_json(obj):
    return {
        "id": obj.id,
        "name": obj.name,
        "name_en": obj.name_en,
        "nondurable": obj.nondurable,
        "measure": obj.measure,
        "measure_count": obj.measure_count,
        "price": obj.price.amount,
        "discount_price": obj.discount_price.amount,
        "currency_name": obj.price.currency.code,
        "currency_id": obj.price.currency.numeric,
        "active": obj.active,
        "checked": obj.checked,
        "mark_deleted": obj.mark_deleted
    }


def position_in_order_json(position, ship_to):
    # генерирует json для отдельной позиции в заказе, считает стоимость товара и доставки
    prods = product_short_json(position.product)

    prods["amount"] = position.amount
    price = position.product.discount_price if position.product.discount_price else position.product.price

    price = price.amount
    prods["cost"] = price*position.amount

    prods["delivery_type"] = position.order.delivery_type
    tarif, deliv = calculate_delivery(position.product, position.amount, ship_to, position.order.delivery_type)
    prods["delivery_price"] = deliv
    prods["tarif_name"] = tarif.name if tarif else ''
    prods["tarif_id"] = tarif.id if tarif else 0

    return prods


def order_json_for_buyer(order, ship_to=None):
    # генерирует json для заказа со всеми позициями
    if not ship_to:
        ship_to = order.shipping_address.city.region.country if order.shipping_address else None

    products = [position_in_order_json(position, ship_to) for position in AmountProduct.objects.filter(order=order)]

    subtotal_price = sum(float(p['cost']) for p in products)
    delivery_price = sum(float(p['delivery_price']) for p in products)
    total_price = subtotal_price + delivery_price

    order_status = OrderStatus.objects.filter(order=order).order_by('-id').first()

    return {
        "order_id": order.id,
        "order_status": order_status.status,
        "seller_id": order.seller.id,
        "seller": order.seller.id,
        "buyer": order.profile.id,
        "delivery_type": order.delivery_type,
        "ship_to": order.ship_to.id,
        "number": order.number,
        "payment_method": order.payment_method,
        "note": order.note,
        "payment_status": order.payment_status,
        "payment_address": order.payment_address.id if order.payment_address else None,
        "shipping_address": order.shipping_address.id if order.payment_address else None,
        "date_added": order.date_added.strftime('%H:%M:%S %Y-%m-%d'),
        "products": products,

        "subtotal_price": subtotal_price,
        "delivery_price": delivery_price,
        "total_price": total_price,
    }


def order_json_for_seller(order, ship_to):
    # генерирует json для заказа со всеми позициями
    products = [position_in_order_json(position, ship_to) for position in AmountProduct.objects.filter(order=order)]

    subtotal_price = sum(float(p['cost']) for p in products)
    delivery_price = sum(float(p['delivery_price']) for p in products)
    total_price = subtotal_price + delivery_price

    order_status = OrderStatus.objects.filter(order=order).order_by('-id').first()

    return {
        "order_id": order.id,
        "order_status": order_status.status,
        "seller_id": order.seller.id,
        "seller": order.seller.id,
        "buyer": order.profile.id,
        "delivery_type": order.delivery_type,
        "ship_to": order.ship_to.id,
        "number": order.number,
        "payment_method": order.payment_method,
        "note": order.note,
        "payment_status": order.payment_status,
        "payment_address": order.payment_address.id if order.payment_address else None,
        "shipping_address": order.shipping_address.id if order.payment_address else None,
        "date_added": order.date_added.strftime('%H:%M:%S %Y-%m-%d'),
        "products": products,

        "subtotal_price": subtotal_price,
        "delivery_price": delivery_price,
        "total_price": total_price
    }


def cart_json(order, ship_to):
    # генерирует json для заказа со всеми позициями
    positions = AmountProduct.objects.filter(order=order)
    products = [position_in_order_json(position, ship_to) for position in positions]

    subtotal_price = sum(float(p['cost']) for p in products)
    delivery_price = sum(float(p['delivery_price']) for p in products)
    total_price = subtotal_price + delivery_price

    return {
        "order_id": order.id,
        "seller_id": order.seller.id,
        "seller": order.seller.id,
        "buyer": order.profile.id,
        "delivery_type": order.delivery_type,
        "ship_to": order.ship_to.id,
        "number": order.number,
        "date_added": order.date_added.strftime('%H:%M:%S %Y-%m-%d'),
        "products": products,

        "subtotal_price": subtotal_price,
        "delivery_price": delivery_price,
        "total_price": total_price
    }

