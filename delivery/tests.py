from django.test import TestCase, TransactionTestCase
from django.test import Client
from django.http import QueryDict
import json

from django.contrib.auth.models import User
from rest_framework.authtoken.models import Token
from catalog.models import ImgProduct, VideoProduct
from userdata.models import (
    Profile, ProfileBusiness, FileForProfile, Address
)
from geodata.models import Country, Region, City
from core.models import CountryNumberphone

import base64


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

def convert_bytes_resp_to_dict(x):
    return json.loads(x.decode('utf8').replace("'", '"'))


class ApiViewTests(TransactionTestCase):
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


    def test_add_tariff_mark1_for_country(self):
        client, response = log_out()

        data = {
                    "mark": 1,
                    "type": 1,
                    "weight": 10,
                    "price": 5.0,
                    "country": 73
                }
        response = client.post('/api/add_tariff_for_country/', data)

        self.assertEqual(response.status_code, 401, "user authenticated")
        self.assertEqual(
            response.data,
            {'detail': 'Authentication credentials were not provided.'},
            "user authenticated"
        )
        client, response = log_in_as_root()

        response = client.post('/api/add_tariff_for_country/', data)
        self.assertEqual(response.status_code, 200, response.content)
        #{"mark":1, "type":1, "weight": 30, "price": 20, "country": 2, "type":1}
        # data = {
        #             "mark": 1,
        #             "type": 1,
        #             "weight": 10,
        #             "price": 5,
        #             "group": 2
        #         }
        # response = client.post('/api/add_tariff_for_group/', data)
        # self.assertEqual(response.status_code, 200, response.content)
        #
        data = {
                    "country": 73
                }
        response = client.post('/api/get_tariff_for_country/', data)
        self.assertEqual(response.data.get('tariffs')[0].get('mark'), 1, response.content)
        self.assertEqual(response.data.get('tariffs')[0].get('type'), 1, response.content)
        self.assertEqual(response.data.get('tariffs')[0].get('weight'), 10, response.content)
        self.assertEqual(response.data.get('tariffs')[0].get('price'), '5.00 EUR', response.content)
        self.assertEqual(response.data.get('tariffs')[0].get('country_id'), '73', response.content)
        self.assertEqual(response.data.get('tariffs')[0].get('type'), 1, response.content)

        data = {
                    "country": 14
                }
        response = client.post('/api/get_tariff_for_country/', data)
        self.assertEqual(len(response.data.get('tariffs')), 0, response.content)

        data = {
                    "group": 2
                }
        response = client.post('/api/get_tariff_for_group/', data)
        self.assertEqual(len(response.data.get('tariffs')), 1, response.content)

        data = {
                    "group": 1
                }
        response = client.post('/api/get_tariff_for_group/', data)
        self.assertEqual(len(response.data.get('tariffs')), 0, response.content)


    def test_add_tariff_mark2_for_country(self):
        client, response = log_out()

        data = {
                    "mark": 2,
                    "type": 1,
                    "weight": 10,
                    "price": 5.0,
                    "country": 73
                }
        response = client.post('/api/add_tariff_for_country/', data)

        self.assertEqual(response.status_code, 401, "user authenticated")
        self.assertEqual(
            response.data,
            {'detail': 'Authentication credentials were not provided.'},
            "user authenticated"
        )
        client, response = log_in_as_root()

        response = client.post('/api/add_tariff_for_country/', data)
        self.assertEqual(response.status_code, 200, response.content)

        data = {
                    "country": 73
                }
        response = client.post('/api/get_tariff_for_country/', data)
        self.assertEqual(response.data.get('tariffs')[0].get('mark'), 2, response.content)
        self.assertEqual(response.data.get('tariffs')[0].get('type'), 1, response.content)
        self.assertEqual(response.data.get('tariffs')[0].get('weight'), 10, response.content)
        self.assertEqual(response.data.get('tariffs')[0].get('price'), '5.00 EUR', response.content)
        self.assertEqual(response.data.get('tariffs')[0].get('country_id'), '73', response.content)
        self.assertEqual(response.data.get('tariffs')[0].get('type'), 1, response.content)

        data = {
                    "country": 14
                }
        response = client.post('/api/get_tariff_for_country/', data)
        self.assertEqual(len(response.data.get('tariffs')), 0, response.content)

        data = {
                    "group": 2
                }
        response = client.post('/api/get_tariff_for_group/', data)
        self.assertEqual(len(response.data.get('tariffs')), 1, response.content)

        data = {
                    "group": 1
                }
        response = client.post('/api/get_tariff_for_group/', data)
        self.assertEqual(len(response.data.get('tariffs')), 0, response.content)


    def test_add_tariff_mark3_for_country(self):
        client, response = log_out()

        data = {
                    "mark": 3,
                    "type": 1,
                    "weight": 10,
                    "price": 5.0,
                    "country": 73
                }
        response = client.post('/api/add_tariff_for_country/', data)

        self.assertEqual(response.status_code, 401, "user authenticated")
        self.assertEqual(
            response.data,
            {'detail': 'Authentication credentials were not provided.'},
            "user authenticated"
        )
        client, response = log_in_as_root()

        response = client.post('/api/add_tariff_for_country/', data)
        self.assertEqual(response.status_code, 200, response.content)

        data = {
                    "country": 73
                }
        response = client.post('/api/get_tariff_for_country/', data)
        self.assertEqual(response.data.get('tariffs')[0].get('mark'), 3, response.content)
        self.assertEqual(response.data.get('tariffs')[0].get('type'), 1, response.content)
        self.assertEqual(response.data.get('tariffs')[0].get('weight'), 10, response.content)
        self.assertEqual(response.data.get('tariffs')[0].get('price'), '5.00 EUR', response.content)
        self.assertEqual(response.data.get('tariffs')[0].get('country_id'), '73', response.content)
        self.assertEqual(response.data.get('tariffs')[0].get('type'), 1, response.content)

        data = {
                    "country": 14
                }
        response = client.post('/api/get_tariff_for_country/', data)
        self.assertEqual(len(response.data.get('tariffs')), 0, response.content)

        data = {
                    "group": 2
                }
        response = client.post('/api/get_tariff_for_group/', data)
        self.assertEqual(len(response.data.get('tariffs')), 1, response.content)

        data = {
                    "group": 1
                }
        response = client.post('/api/get_tariff_for_group/', data)
        self.assertEqual(len(response.data.get('tariffs')), 0, response.content)


    def test_add_tariff_allmarks_for_country(self):
        client, response = log_out()

        data = {
                    "mark": 1,
                    "type": 1,
                    "weight": 10,
                    "price": 5.0,
                    "country": 73
                }
        response = client.post('/api/add_tariff_for_country/', data)

        self.assertEqual(response.status_code, 401, "user authenticated")
        self.assertEqual(
            response.data,
            {'detail': 'Authentication credentials were not provided.'},
            "user authenticated"
        )
        client, response = log_in_as_root()

        response = client.post('/api/add_tariff_for_country/', data)
        self.assertEqual(response.status_code, 200, response.content)

        data_country = {
                    "country": 73
                }
        response = client.post('/api/get_tariff_for_country/', data_country)
        self.assertEqual(response.data.get('tariffs')[0].get('mark'), 1, response.content)
        self.assertEqual(response.data.get('tariffs')[0].get('type'), 1, response.content)
        self.assertEqual(response.data.get('tariffs')[0].get('weight'), 10, response.content)
        self.assertEqual(response.data.get('tariffs')[0].get('price'), '5.00 EUR', response.content)
        self.assertEqual(response.data.get('tariffs')[0].get('country_id'), '73', response.content)
        self.assertEqual(response.data.get('tariffs')[0].get('type'), 1, response.content)

        data = {
                    "mark": 2,
                    "type": 1,
                    "weight": 12,
                    "price": 2.0,
                    "country": 73
                }
        response = client.post('/api/add_tariff_for_country/', data)
        response = client.post('/api/get_tariff_for_country/', data_country)
        self.assertEqual(response.data.get('tariffs')[1].get('mark'), 2, response.content)
        self.assertEqual(response.data.get('tariffs')[1].get('type'), 1, response.content)
        self.assertEqual(response.data.get('tariffs')[1].get('weight'), 12, response.content)
        self.assertEqual(response.data.get('tariffs')[1].get('price'), '2.00 EUR', response.content)
        self.assertEqual(response.data.get('tariffs')[1].get('country_id'), '73', response.content)
        self.assertEqual(response.data.get('tariffs')[1].get('type'), 1, response.content)

        data = {
                    "mark": 3,
                    "type": 1,
                    "weight": 13,
                    "price": 3.0,
                    "country": 73
                }
        response = client.post('/api/add_tariff_for_country/', data)
        response = client.post('/api/get_tariff_for_country/', data_country)
        self.assertEqual(response.data.get('tariffs')[2].get('mark'), 3, response.content)
        self.assertEqual(response.data.get('tariffs')[2].get('type'), 1, response.content)
        self.assertEqual(response.data.get('tariffs')[2].get('weight'), 13, response.content)
        self.assertEqual(response.data.get('tariffs')[2].get('price'), '3.00 EUR', response.content)
        self.assertEqual(response.data.get('tariffs')[2].get('country_id'), '73', response.content)
        self.assertEqual(response.data.get('tariffs')[2].get('type'), 1, response.content)

        data_country = {
                    "country": 14
                }
        response = client.post('/api/get_tariff_for_country/', data_country)
        self.assertEqual(len(response.data.get('tariffs')), 0, response.content)

        data_group = {
                    "group": 2
                }
        response = client.post('/api/get_tariff_for_group/', data_group)
        self.assertEqual(len(response.data.get('tariffs')), 3, response.content)

        data_group = {
                    "group": 1
                }
        response = client.post('/api/get_tariff_for_group/', data_group)
        self.assertEqual(len(response.data.get('tariffs')), 0, response.content)


    def test_delete_tariff_for_country(self):
        client, response = log_out()

        data_1 = {
                    "mark": 1,
                    "type": 1,
                    "weight": 10,
                    "price": 5.0,
                    "country": 73
                }
        response = client.post('/api/add_tariff_for_country/', data_1)

        self.assertEqual(response.status_code, 401, "user authenticated")
        self.assertEqual(
            response.data,
            {'detail': 'Authentication credentials were not provided.'},
            "user authenticated"
        )
        client, response = log_in_as_root()

        response = client.post('/api/add_tariff_for_country/', data_1)
        self.assertEqual(response.status_code, 200, response.content)

        data_country = {
                    "country": 73
                }
        response = client.post('/api/get_tariff_for_country/', data_country)

        data_2 = {
                    "mark": 2,
                    "type": 1,
                    "weight": 12,
                    "price": 2.0,
                    "country": 73
                }
        response = client.post('/api/add_tariff_for_country/', data_2)
        response = client.post('/api/get_tariff_for_country/', data_country)

        self.assertEqual(response.data.get('tariffs')[0].get('mark'), 1, response.content)
        self.assertEqual(response.data.get('tariffs')[0].get('type'), 1, response.content)
        self.assertEqual(response.data.get('tariffs')[0].get('weight'), 10, response.content)
        self.assertEqual(response.data.get('tariffs')[0].get('price'), '5.00 EUR', response.content)
        self.assertEqual(response.data.get('tariffs')[0].get('country_id'), '73', response.content)
        self.assertEqual(response.data.get('tariffs')[0].get('type'), 1, response.content)

        self.assertEqual(response.data.get('tariffs')[1].get('mark'), 2, response.content)
        self.assertEqual(response.data.get('tariffs')[1].get('type'), 1, response.content)
        self.assertEqual(response.data.get('tariffs')[1].get('weight'), 12, response.content)
        self.assertEqual(response.data.get('tariffs')[1].get('price'), '2.00 EUR', response.content)
        self.assertEqual(response.data.get('tariffs')[1].get('country_id'), '73', response.content)
        self.assertEqual(response.data.get('tariffs')[1].get('type'), 1, response.content)

        del_id = response.data.get('tariffs')[1].get('tariff_id')

        data_del = {"tariff": del_id}
        response = client.post('/api/delete_tariff_for_country/', data_del)

        response = client.post('/api/get_tariff_for_country/', data_country)
        self.assertEqual(len(response.data.get('tariffs')), 1, response.content)
        self.assertEqual(response.data.get('tariffs')[0].get('mark'), 1, response.content)
        self.assertEqual(response.data.get('tariffs')[0].get('type'), 1, response.content)
        self.assertEqual(response.data.get('tariffs')[0].get('weight'), 10, response.content)
        self.assertEqual(response.data.get('tariffs')[0].get('price'), '5.00 EUR', response.content)
        self.assertEqual(response.data.get('tariffs')[0].get('country_id'), '73', response.content)
        self.assertEqual(response.data.get('tariffs')[0].get('type'), 1, response.content)


    def test_add_tariff_for_group(self):
        client, response = log_out()

        data_1 = {
                    "mark": 1,
                    "type": 1,
                    "weight": 10,
                    "price": 5.0,
                    "group": 2
                }
        response = client.post('/api/add_tariff_for_group/', data_1)

        self.assertEqual(response.status_code, 401, "user authenticated")
        self.assertEqual(
            response.data,
            {'detail': 'Authentication credentials were not provided.'},
            "user authenticated"
        )
        client, response = log_in_as_root()

        response = client.post('/api/add_tariff_for_group/', data_1)
        self.assertEqual(response.status_code, 200, response.content)

        data_country = {
                    "country": 73
                }

        data_2 = {
                    "mark": 2,
                    "type": 1,
                    "weight": 12,
                    "price": 2.0,
                    "country": 73
                }
        response = client.post('/api/add_tariff_for_country/', data_2)
        response = client.post('/api/get_tariff_for_country/', data_country)

        self.assertEqual(response.data.get('tariffs')[0].get('mark'), 1, response.content)
        self.assertEqual(response.data.get('tariffs')[0].get('type'), 1, response.content)
        self.assertEqual(response.data.get('tariffs')[0].get('weight'), 10, response.content)
        self.assertEqual(response.data.get('tariffs')[0].get('price'), '5.00 EUR', response.content)
        self.assertEqual(response.data.get('tariffs')[0].get('country_id'), '73', response.content)
        self.assertEqual(response.data.get('tariffs')[0].get('type'), 1, response.content)

        self.assertEqual(response.data.get('tariffs')[1].get('mark'), 2, response.content)
        self.assertEqual(response.data.get('tariffs')[1].get('type'), 1, response.content)
        self.assertEqual(response.data.get('tariffs')[1].get('weight'), 12, response.content)
        self.assertEqual(response.data.get('tariffs')[1].get('price'), '2.00 EUR', response.content)
        self.assertEqual(response.data.get('tariffs')[1].get('country_id'), '73', response.content)
        self.assertEqual(response.data.get('tariffs')[1].get('type'), 1, response.content)

        data_group = {
            "group": 2
        }
        response = client.post('/api/get_tariff_for_group/', data_group)

        self.assertEqual(len(response.data.get('tariffs')), 6, response.content)
        self.assertEqual(response.data.get('tariffs')[0].get('mark'), 1, response.content)
        self.assertEqual(response.data.get('tariffs')[0].get('type'), 1, response.content)
        self.assertEqual(response.data.get('tariffs')[0].get('weight'), 10, response.content)
        self.assertEqual(response.data.get('tariffs')[0].get('price'), '5.00 EUR', response.content)
        self.assertEqual(response.data.get('tariffs')[0].get('country_id'), 6, response.content)
        self.assertEqual(response.data.get('tariffs')[0].get('type'), 1, response.content)


    def test_add_tariff_for_product(self):
        client, response = log_out()
        client, response = log_in_as_root()

        tarif_1 = {
                    "mark": 1,
                    "type": 1,
                    "weight": 10,
                    "price": 5.0,
                    "country": 73,
                }

        tarif_2 = {
                    "mark": 2,
                    "type": 1,
                    "weight": 12,
                    "price": 2.0,
                    "country": 73,
                }
        tarif_3 = {
                    "mark": 3,
                    "type": 1,
                    "weight": 12,
                    "price": 2.0,
                    "country": 73,
                }
        data_country = {
                    "country": 73
                }

        data_product = {
            "name": "Test product",
            "name_en": "Test product en",
            "subcategory": 1,
            "weight_of_pack": 3,
            "measure": 2,
            "measure_count": 2,
            "number_of_packages": 20,
            "price": 45,
            "discount_price": 40,
            "description": "Some params of product",
            "description_en": "Some params of product en",
            "country": 4,
            "region": "French fields",
            "nondurable": 0,
            "currency": 1,
            "expiration_date": 1,
        }

        response = client.post('/api/add_tariff_for_country/', tarif_1)
        response = client.post('/api/get_tariff_for_country/', data_country)
        tarif1_id = response.data.get('tariffs')[0].get('tariff_id')

        response = client.post('/api/add_tariff_for_country/', tarif_2)
        response = client.post('/api/get_tariff_for_country/', data_country)
        tarif2_id = response.data.get('tariffs')[1].get('tariff_id')

        response = client.post('/api/add_tariff_for_country/', tarif_3)
        response = client.post('/api/get_tariff_for_country/', data_country)
        tarif3_id = response.data.get('tariffs')[2].get('tariff_id')

        response = client.post('/api/get_tariff_for_country/', data_country)
        self.assertEqual(len(response.data.get('tariffs')), 3, response.content)

        response = client.post('/api/add_product_by_seller_step_one/', data_product)
        prod_id = response.data.get('product').get('id')
        self.assertEqual(response.status_code, 200, response.content)

        response = client.get('/api/get_my_products/')

        self.assertEqual(len(response.data.get('products')), 1, response.content)

        data_tarif1_for_prod = {
            "product": prod_id,
            "tariff": tarif1_id
        }
        response = client.post('/api/add_tariff_for_product/', data_tarif1_for_prod)
        self.assertEqual(response.status_code, 200, response.content)


        data_tarif2_for_prod = {
            "product": prod_id,
            "tariff": tarif2_id
        }
        response = client.post('/api/add_tariff_for_product/', data_tarif2_for_prod)
        self.assertEqual(response.status_code, 200, response.content)


        data_tarif3_for_prod = {
            "product": prod_id,
            "tariff": tarif3_id
        }
        response = client.post('/api/add_tariff_for_product/', data_tarif3_for_prod)
        self.assertEqual(response.status_code, 200, response.content)




































