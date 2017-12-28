# -*- coding: utf-8 -*-
from django.test import TestCase, TransactionTestCase
from django.test import Client

import json

from bank.models import Currency
from catalog.models import Product, SubCategory
from core.models import CountryNumberphone
from delivery.models import TarifsForCountry, TariffForProduct
from userdata.models import Profile, ProfileBusiness

client = Client()

def log_in_as_testuser():
    client, response = log_in("testuser", "123qwe123")

    return client, response

def log_in_as_root():
    client, response = log_in("root", "123qwe123")

    return client, response

def log_in(username, password):

    data = {
        "username": username,
        "password": password
    }
    response = client.post("/api/sign_in/", data=json.dumps(data), content_type='application/json')

    return client, response

def log_out():
    response = client.get("/api/sign_out/")

    return client, response


def upd_root_to_business():
    pr = Profile.objects.get(user__username="root")
    code = CountryNumberphone.objects.get(id=1)
    prof, created = ProfileBusiness.objects.get_or_create(
        profile=pr,
    )
    prof.terms_of_use=True
    prof.type_of_business=1
    prof.organization_type=1
    prof.organization_name="dvvdv"
    prof.vat="123214"
    prof.registration_number="234"
    prof.first_name="JHKJJ"
    prof.middle_name="NNN"
    prof.last_name="Dcff"
    prof.position_in_com="KKkk"
    prof.code_num_phone=code
    prof.phone_number="123132"
    prof.email="kbk@lm.ry"
    prof.addition_receiver="Kjhdjvb"
    prof.receiver_phonenumber="18263634"
    prof.save()


def create_products():
    # prod1 = {
    # "name":"Product 1", "subcategory": 1, "description": "Test product number one",
    # "currency":1, "price": 10.5,
    #
    # "name_en": "",  "weight_of_pack": 4,
    # "measure": 1, "measure_count": 12,
    # "number_of_packages": 35, "discount_price": 0,
    # "description_en":"",
    # "country": 0, "region":"", "nondurable": 0,
    # "expiry_days": 25,
    # "photos": [], "video": "url"
    # }
    seller = ProfileBusiness.objects.get(id=1)
    subcat1 = SubCategory.objects.get(id=1)
    subcat2 = SubCategory.objects.get(id=2)
    currency = Currency.objects.get(id=1)

    pr1 = Product(
        profile_business=seller,
        active=True,
        category=subcat1,
        currency=currency,
        name="Product 1",
        description="Test product number one",
        price=10.5,
        name_en="",
        description_en="",
        number_of_packages=100,
        weight_of_pack=12,
        nondurable=False,
        expiry_days=180,
        measure=1,
        measure_count=0,
        discount_price=None,
        video="",
        country=None,
        region=None
    )
    pr1.save()

    pr2 = Product(
        profile_business=seller,
        active=True,
        category=subcat2,
        currency=currency,
        name="Product 2",
        description="Test product number two",
        price=1.3,
        name_en="",
        description_en="",
        number_of_packages=150,
        weight_of_pack=3.2,
        nondurable=False,
        expiry_days=35,
        measure=1,
        measure_count=0,
        discount_price=None,
        video="",
        country=None,
        region=None
    )
    pr2.save()

    pr3 = Product(
        profile_business=seller,
        active=True,
        category=subcat2,
        currency=currency,
        name="Product 3",
        description="Test product number three",
        price=13,
        name_en="",
        description_en="",
        number_of_packages=47,
        weight_of_pack=32,
        nondurable=False,
        expiry_days=135,
        measure=1,
        measure_count=0,
        discount_price=9.99,
        video="",
        country=None,
        region=None
    )
    pr3.save()

    tarif = TarifsForCountry.objects.create(
        profile=seller,
        country_id=73,
        name="Tarif 1",
        mark=1,
        type=1,
        weight=1,
        price=1.2
    )
    tarif.save()

    tarif2 = TarifsForCountry.objects.create(
        profile=seller,
        country_id=73,
        name="Tarif 2",
        mark=1,
        type=1,
        weight=35,
        price=2.6
    )
    tarif2.save()

    tarif3 = TarifsForCountry.objects.create(
        profile=seller,
        country_id=73,
        name="Tarif 3",
        mark=3,
        type=1,
        weight=3,
        price=9
    )
    tarif3.save()

    tp1 = TariffForProduct.objects.create(product=pr1, tariff=tarif)
    tp1.save()
    tp2 = TariffForProduct.objects.create(product=pr1, tariff=tarif2)
    tp2.save()
    tp3 = TariffForProduct.objects.create(product=pr1, tariff=tarif3)
    tp3.save()


def convert_bytes_resp_to_dict(x):
    return json.loads(x.decode('utf8').replace("'", '"'))


class OrderViewTests(TestCase):
    fixtures = [
                'geodata/fixtures/countries.json',
                'bank/fixtures/currency.json',
                'core/fixtures/languages.json',
                'userdata/fixtures/users.json',
                'core/fixtures/country_codes.json',
                'catalog/fixtures/group.json',
                'catalog/fixtures/category.json',
                'catalog/fixtures/subcategory.json',
                # 'userdata/fixtures/business_profiles.json'
                ]

    def setUp(self):
        upd_root_to_business()
        create_products()

    def test_add_product_to_cart(self):
        data1 = {
            "product": 1,
            "delivery_type": 1,
            "amount": 10,
            "ship_to": 1
        }
        log_in_as_root()
        response = client.post('/api/add_product_to_cart/', data1)
        self.assertEqual(response.status_code, 200, "PRODUCT NOT ADDED TO CART")
        self.assertEqual(response.data.get('order_id'), 1, "CART ID NOT FOUND")
        self.assertEqual(response.data.get('products').get("1").get('id'), 1, "PRODUCT ID NOT FOUND")
        self.assertEqual(response.data.get('products').get("1").get('amount'), 10, "WRONG AMOUNT OF PRODUCT")

        response = client.post('/api/add_product_to_cart/', data1)
        self.assertEqual(response.status_code, 200, "PRODUCT NOT ADDED TO CART")
        self.assertEqual(response.data.get('order_id'), 1, "CART ID NOT FOUND")
        self.assertEqual(response.data.get('products').get("1").get('id'), 1, "PRODUCT ID NOT FOUND")
        self.assertEqual(response.data.get('products').get("1").get('amount'), 20, "WRONG AMOUNT OF PRODUCT")

        data2 = {
            "product": 2,
            "delivery_type": 1,
            "amount": 13,
            "ship_to": 1
        }

        response = client.post('/api/add_product_to_cart/', data2)
        self.assertEqual(response.status_code, 200, "PRODUCT NOT ADDED TO CART")
        self.assertEqual(response.data.get('order_id'), 1, "CART ID NOT FOUND")
        self.assertEqual(response.data.get('products').get("2").get('id'), 2, "PRODUCT ID NOT FOUND")
        self.assertEqual(response.data.get('products').get("2").get('amount'), 13, "WRONG AMOUNT OF PRODUCT")
        self.assertEqual(response.data.get('products').get("1").get('id'), 1, "PRODUCT ID NOT FOUND")
        self.assertEqual(response.data.get('products').get("1").get('amount'), 20, "WRONG AMOUNT OF PRODUCT")

    def test_delete_product_from_cart(self):
        add1 = {
            "product": 1,
            "delivery_type": 1,
            "amount": 10,
            "ship_to": 1
        }
        add2 = {
            "product": 2,
            "delivery_type": 1,
            "amount": 13,
            "ship_to": 1
        }
        del1 = {
            "order_id": 1,
            "product_id": 1,
            "ship_to": 1
        }
        del2 = {
            "order_id": 1,
            "product_id": 2,
            "ship_to": 1
        }
        log_in_as_root()

        response = client.post('/api/add_product_to_cart/', add1)
        self.assertEqual(response.status_code, 200, "PRODUCT NOT ADDED TO CART")
        response = client.post('/api/add_product_to_cart/', add2)
        self.assertEqual(response.status_code, 200, "PRODUCT NOT ADDED TO CART")

        response = client.post('/api/delete_product_from_cart/', del1)
        self.assertEqual(response.status_code, 200, "PRODUCT NOT DELETED FROM CART")
        self.assertEqual(response.data.get('order_id'), 1, "CART ID NOT FOUND")
        self.assertNotEqual(response.data.get('products').get("1").get('id'), 1, "DELETED PRODUCT FOUND")
        self.assertEqual(response.data.get('products').get("1").get('id'), 2, "PRODUCT ID NOT FOUND")

        response = client.post('/api/delete_product_from_cart/', del2)
        self.assertEqual(response.status_code, 200, "PRODUCT NOT DELETED FROM CART")
        self.assertNotEqual(response.data.get('order_id'), 1, "CART SHOULD BE DELETED")

    def test_update_count_of_products_in_cart(self):
        add1 = {
            "product": 1,
            "delivery_type": 1,
            "amount": 10,
            "ship_to": 1
        }
        add2 = {
            "product": 2,
            "delivery_type": 1,
            "amount": 13,
            "ship_to": 1
        }
        upd1 = {
            "order_id": 1,
            "product_id": 1,
            "amount": 3
        }
        upd2 = {
            "order_id": 1,
            "product_id": 2,
            "ship_to": 0
        }
        upd3 = {
            "order_id": 1,
            "product_id": 1,
            "ship_to": 0
        }
        log_in_as_root()

        response = client.post('/api/add_product_to_cart/', add1)
        self.assertEqual(response.status_code, 200, "PRODUCT NOT ADDED TO CART")
        response = client.post('/api/add_product_to_cart/', add2)
        self.assertEqual(response.status_code, 200, "PRODUCT NOT ADDED TO CART")
        self.assertEqual(response.data.get('products').get("1").get('id'), 1, "PRODUCT ID NOT FOUND")
        self.assertEqual(response.data.get('products').get("1").get('amount'), 10, "WRONG AMOUNT OF PRODUCT")
        self.assertEqual(response.data.get('products').get("2").get('id'), 2, "PRODUCT ID NOT FOUND")
        self.assertEqual(response.data.get('products').get("2").get('amount'), 13, "WRONG AMOUNT OF PRODUCT")

        response = client.post('/api/update_count_of_products_in_cart/', upd1)
        self.assertEqual(response.status_code, 200, "CART NOT UPDATED")
        self.assertEqual(response.data.get('order_id'), 1, "CART ID NOT FOUND")
        self.assertEqual(response.data.get('products').get("1").get('id'), 1, "PRODUCT ID NOT FOUND")
        self.assertEqual(response.data.get('products').get("1").get('amount'), 3, "WRONG AMOUNT OF PRODUCT")
        self.assertEqual(response.data.get('products').get("2").get('id'), 2, "PRODUCT ID NOT FOUND")
        self.assertEqual(response.data.get('products').get("2").get('amount'), 13, "WRONG AMOUNT OF PRODUCT")

        response = client.post('/api/update_count_of_products_in_cart/', upd2)
        self.assertEqual(response.status_code, 200, "CART NOT UPDATED")
        self.assertEqual(response.data.get('products').get("1").get('id'), 1, "PRODUCT ID NOT FOUND")
        self.assertEqual(response.data.get('products').get("1").get('amount'), 3, "WRONG AMOUNT OF PRODUCT")
        self.assertNotEqual(response.data.get('products').get("1").get('id'), 2, "DELETED PRODUCT FOUND")
        self.assertEqual(len(response.data.get('products')), 1, "WRONG AMOUNT OF POSITIONS IN ORDER")

        response = client.post('/api/update_count_of_products_in_cart/', upd3)
        self.assertEqual(response.status_code, 200, "CART NOT UPDATED")
        self.assertEqual(response.data.get('message'), "Order was deleted", "CART NOT DELETED")

    def test_get_my_carts(self):
        add1 = {
            "product": 1,
            "delivery_type": 1,
            "amount": 10,
            "ship_to": 1
        }
        add2 = {
            "product": 2,
            "delivery_type": 2,
            "amount": 13,
            "ship_to": 1
        }
        log_in_as_root()

        response = client.post('/api/add_product_to_cart/', add1)
        self.assertEqual(response.status_code, 200, "PRODUCT NOT ADDED TO CART")
        response = client.post('/api/add_product_to_cart/', add2)
        self.assertEqual(response.status_code, 200, "PRODUCT NOT ADDED TO CART")
        self.assertEqual(response.data.get('products').get("1").get('id'), 1, "PRODUCT ID NOT FOUND")
        self.assertEqual(response.data.get('products').get("1").get('amount'), 10, "WRONG AMOUNT OF PRODUCT")
        self.assertEqual(response.data.get('products').get("2").get('id'), 2, "PRODUCT ID NOT FOUND")
        self.assertEqual(response.data.get('products').get("2").get('amount'), 13, "WRONG AMOUNT OF PRODUCT")


    def test_get_cart(self):
        add1 = {
            "product": 1,
            "delivery_type": 1,
            "order_id": 10,
            "ship_to": 1
        }
        order1 = {
            "order_id": 1,
            "ship_to": 1
        }
        log_in_as_root()

        response = client.post('/api/add_product_to_cart/', add1)
        self.assertEqual(response.status_code, 200, "PRODUCT NOT ADDED TO CART")
        self.assertEqual(response.data.get('products').get("1").get('id'), 1, "PRODUCT ID NOT FOUND")
        self.assertEqual(response.data.get('products').get("1").get('amount'), 10, "WRONG AMOUNT OF PRODUCT")

        response = client.post('/api/get_cart/', order1)
        self.assertEqual(response.status_code, 200, "CART NOT CREATED")


    def test_order_status_paid_for(self):
        add1 = {
            "product": 1,
            "delivery_type": 1,
            "order_id": 10,
            "ship_to": 1
        }
        order1 = {
            "order_id": 1,
            "payment_method": 1,
            "delivery_addr_id": 1,
            "payment_address_id": 1
        }
        log_in_as_root()

        response = client.post('/api/add_product_to_cart/', add1)
        self.assertEqual(response.status_code, 200, "PRODUCT NOT ADDED TO CART")
        self.assertEqual(response.data.get('products').get("1").get('id'), 1, "PRODUCT ID NOT FOUND")
        self.assertEqual(response.data.get('products').get("1").get('amount'), 10, "WRONG AMOUNT OF PRODUCT")

        response = client.post('/api/order_status_paid_for/', order1)
        self.assertEqual(response.status_code, 200, "CART NOT CREATED")





















