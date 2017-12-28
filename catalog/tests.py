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
        mark=2,
        type=1,
        weight=2,
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


class CatalogTests(TestCase):
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
        # create_products()

    def test_add_product_by_seller_step_one(self):
        correct_prod = {
            "name": "prod3", "name_en": "",
            "subcategory": 1,
            "description": "Some useful information", "description_en": "",

            "currency": 1, "price": 10.21, "discount_price": "1,96",
            "weight_of_pack": 12.32, "measure": 1, "measure_count": 87,
            "number_of_packages": 358,

            "country": 73, "region": "",
            "nondurable": True, "expiry_days": 36,
            "photos": [], "video": "url"
        }
        log_in_as_root()
        response = client.post('/api/add_product_by_seller_step_one/', correct_prod)
        self.assertEqual(response.status_code, 200, "PRODUCT NOT CREATED")
        self.assertEqual(response.data.get('product').get('id'), 1, "PRODUCT ID NOT FOUND")
        self.assertEqual(response.data.get('product').get('price'), "10.21", "PRODUCT ID NOT FOUND")
        self.assertEqual(response.data.get('product').get('discount_price'), "1.96", "PRODUCT ID NOT FOUND")

    def test_add_product_min_fields(self):
        correct_prod = {
            "name": "prod3",
            "subcategory": 1,
            "description": "Some useful information",

            "price": 10.21,
            # "weight_of_pack": 12.32, "measure": 1, "measure_count": 87,
            # "number_of_packages": 358,

            # "country": 73, "region": "",
            # "nondurable": True, "expiry_days": 36,
            # "photos": [], "video": "url"
        }
        log_in_as_root()
        response = client.post('/api/add_product_by_seller_step_one/', correct_prod)
        self.assertEqual(response.status_code, 200, "PRODUCT NOT CREATED")
        self.assertEqual(response.data.get('product').get('id'), 1, "PRODUCT ID NOT FOUND")
        self.assertEqual(response.data.get('product').get('price'), "10.21", "PRODUCT ID NOT FOUND")

    def test_update_product_by_seller(self):
        create_products()
        correct_prod = {
            "product": 1,
            "name": "",
            "subcategory": 1,
            "currency": 1,
            "description": "",
            "description_en": "",
            "number_of_packages": 5,
            "weight_of_pack": 10,
            "nondurable": True,
            "expiry_days": 31,
            "measure": 1,
            "price": 25,
            "discount_price": 19.94,
            "country": 73,
            "region_name": "Tambov"
        }

        log_in_as_root()
        response = client.post('/api/update_product_by_seller/', correct_prod)
        self.assertEqual(response.status_code, 200, "PRODUCT NOT CREATED")
        self.assertEqual(response.data.get('product').get('id'), 1, "PRODUCT ID NOT FOUND")
        self.assertEqual(response.data.get('product').get('price'), "25", "PRODUCT ID NOT FOUND")
        self.assertEqual(response.data.get('product').get('discount_price'), "19.94", "PRODUCT ID NOT FOUND")
        self.assertEqual(response.data.get('product').get('expiry_days'), "31", "PRODUCT ID NOT FOUND")
        self.assertEqual(response.data.get('product').get('weight_of_pack'), "10", "PRODUCT ID NOT FOUND")
        self.assertEqual(response.data.get('product').get('country'), "Russia", "PRODUCT ID NOT FOUND")
        # self.assertEqual(response.data.get('product').get('region'), "Tambov", "PRODUCT ID NOT FOUND")


    def test_get_product(self):
        create_products()
        prod_id = {
            "product_id": 1
        }

        response = client.post('/api/get_product/', prod_id)
        self.assertEqual(response.status_code, 200, "PRODUCT NOT CREATED")
        self.assertEqual(response.data.get('product').get('id'), 1, "PRODUCT ID NOT FOUND")
        self.assertEqual(response.data.get('product').get('profile_business'), 1, "PRODUCT ID NOT FOUND")
        self.assertEqual(response.data.get('product').get('currency_id'), 1, "PRODUCT ID NOT FOUND")
        self.assertEqual(response.data.get('product').get('name'), "Product 1", "PRODUCT ID NOT FOUND")
        self.assertEqual(response.data.get('product').get('description'), "Test product number one", "PRODUCT ID NOT FOUND")
        self.assertEqual(response.data.get('product').get('price'), "10.50", "PRODUCT ID NOT FOUND")
        self.assertEqual(response.data.get('product').get('discount_price'), '0', "PRODUCT ID NOT FOUND")
        self.assertEqual(response.data.get('product').get('expiry_days'), 180, "PRODUCT ID NOT FOUND")
        self.assertEqual(response.data.get('product').get('weight_of_pack'), 12.0, "PRODUCT ID NOT FOUND")
        self.assertEqual(response.data.get('product').get('country'), '', "PRODUCT ID NOT FOUND")
        self.assertEqual(response.data.get('product').get('region'), None, "PRODUCT ID NOT FOUND")
        self.assertEqual(response.data.get('product').get('classes'), [], "PRODUCT ID NOT FOUND")

    def test_add_class_for_product(self):
        create_products()
        prod = {
            "product": 1, "class": [1, 2]
        }

        log_in_as_root()
        response = client.post('/api/add_class_for_product/', prod)
        self.assertEqual(response.status_code, 200, "PRODUCT NOT CREATED")
















