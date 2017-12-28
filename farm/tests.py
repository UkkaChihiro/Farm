from django.test import TestCase
from django.test import Client
import json
from core.models import CountryNumberphone
from userdata.models import Profile, ProfileBusiness


client = Client()


def log_out():
    response = client.get("/api/sign_out/")

    return client, response


def log_in_as_testuser():
    log_out()
    client, response = log_in("testuser", "123qwe123")

    return client, response


def log_in_as_root():
    log_out()
    client, response = log_in("root", "123qwe123")

    return client, response


def log_in(username, password):

    data = {
        "username": username,
        "password": password
    }
    response = client.post("/api/sign_in/", data=json.dumps(data), content_type='application/json')

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


class FarmTests(TestCase):
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


    def test_add_farm(self):
        farm = {
            "name": "Test Farm1",
            "groups": [1, ]
        }
        log_in_as_testuser()
        response = client.post('/api/add_farm/', farm)
        self.assertEqual(response.status_code, 401, "FARM WAS CREATED BY BUYER")

        log_in_as_root()
        response = client.post('/api/add_farm/', farm)
        self.assertEqual(response.status_code, 200, "FARM NOT CREATED")
        self.assertEqual(response.data.get('farm').get('id'), 1, "FARM ID NOT FOUND")
        self.assertEqual(response.data.get('farm').get('business_profile'), 1, "FARM OWNER NOT FOUND")
        self.assertEqual(response.data.get('farm').get('name'), "Test Farm1", "FARM OWNER NOT FOUND")
        self.assertEqual(response.data.get('groups'), [1, ], "FARM OWNER NOT FOUND")


    def test_update_farm(self):
        farm = {
            "name": "Test Farm1",
            "groups": [1, ]
        }
        log_in_as_testuser()
        response = client.post('/api/update_farm/', farm)
        self.assertEqual(response.status_code, 401, "FARM WAS UPDATED BY BUYER")

        log_in_as_root()
        response = client.post('/api/add_farm/', farm)
        self.assertEqual(response.status_code, 200, "FARM NOT CREATED")

        updated_farm = {
            "farm_id": 1,
            "name": "Updated Farm",
            "groups": [2, ]
        }
        response = client.post('/api/update_farm/', updated_farm)
        self.assertEqual(response.data.get('farm').get('id'), 1, "FARM ID NOT FOUND")
        self.assertEqual(response.data.get('farm').get('business_profile'), 1, "FARM OWNER NOT FOUND")
        self.assertEqual(response.data.get('farm').get('name'), "Updated Farm", "FARM OWNER NOT FOUND")
        self.assertEqual(response.data.get('groups'), [2, ], "FARM OWNER NOT FOUND")


    def test_get_all_my_farms(self):
        farm1 = {
            "name": "Test Farm1",
            "groups": [1, ]
        }
        farm2 = {
            "name": "Test Farm2",
            "groups": [2, ]
        }

        log_in_as_root()
        response = client.post('/api/add_farm/', farm1)
        self.assertEqual(response.status_code, 200, "FARM NOT CREATED")
        response = client.post('/api/add_farm/', farm2)
        self.assertEqual(response.status_code, 200, "FARM NOT CREATED")

        response = client.get('/api/get_all_my_farms/')
        self.assertEqual(len(response.data.get('farms')), 2, "FARMS NOT CREATED")


    def test_get_farm(self):
        farm1 = {
            "name": "Test Farm1",
            "groups": [1, ]
        }
        farm2 = {
            "name": "Test Farm2",
            "groups": [2, ]
        }

        log_in_as_root()
        response = client.post('/api/add_farm/', farm1)
        self.assertEqual(response.status_code, 200, "FARM NOT CREATED")
        response = client.post('/api/add_farm/', farm2)
        self.assertEqual(response.status_code, 200, "FARM NOT CREATED")

        response = client.post('/api/get_farm/', {"farm_id": 1})
        self.assertEqual(response.data.get("id"), 1, "FARMS NOT CREATED")
        self.assertNotEqual(response.data.get("id"), 2, "FARMS NOT CREATED")


    def test_delete_farm(self):
        farm1 = {
            "name": "Test Farm1",
            "groups": [1, ]
        }
        farm2 = {
            "name": "Test Farm2",
            "groups": [2, ]
        }

        log_in_as_root()
        response = client.post('/api/add_farm/', farm1)
        self.assertEqual(response.status_code, 200, "FARM NOT CREATED")
        response = client.post('/api/add_farm/', farm2)
        self.assertEqual(response.status_code, 200, "FARM NOT CREATED")

        response = client.post('/api/get_farm/', {"farm_id": 1})
        self.assertEqual(response.status_code, 200, "FARM NOT CREATED")
        response = client.post('/api/get_farm/', {"farm_id": 2})
        self.assertEqual(response.status_code, 200, "FARM NOT CREATED")

        response = client.post('/api/delete_farm/', {"farm_id": 1})
        self.assertEqual(response.status_code, 200, "FARM NOT DELETED")

        response = client.get('/api/get_all_my_farms/')
        self.assertEqual(len(response.data.get('farms')), 1, "FARMS NOT DELETED")

        response = client.post('/api/get_farm/', {"farm_id": 1})
        self.assertEqual(response.data, {}, "FARMS NOT DELETED")
        response = client.post('/api/get_farm/', {"farm_id": 2})
        self.assertEqual(response.data.get("id"), 2, "FARMS NOT DELETED")




