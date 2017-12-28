from django.test import TestCase, TransactionTestCase
from django.test import Client

import json


def log_in(username, password):
    client = Client()
    data = {
        "username": username,
        "password": password
    }
    response = client.post("/api/sign_in/", data=json.dumps(data), content_type='application/json')

    return client, response

def log_in_as_testuser():
    client, response = log_in("testuser", "123qwe123")

    return client, response

def log_in_as_root():
    client, response = log_in("root", "123qwe123")

    return client, response

class UserdataTests(TestCase):
    fixtures = [
        'userdata/fixtures/users.json',
        'core/fixtures/country_codes.json',
    ]

    def test_get_country_num_code(self):
        client = Client()

        response = client.get('/api/get_country_num_code/')

        self.assertEqual(response.status_code, 200, "post allowed")
        first = response.data.get('codes').get(1)
        second = response.data.get('codes').get(54)
        self.assertEqual(first, {'name': 'Afghanistan', 'code': 93, 'max_digits': None}, response.content)
        self.assertEqual(second, {'name': 'Dominican Republic', 'code': 1849, 'max_digits': None}, "fail")

        client, response = log_in('root', '123qwe123')

        response = client.get('/api/get_country_num_code/')

        self.assertEqual(response.status_code, 200, "post allowed")
        first = response.data.get('codes').get(1)
        second = response.data.get('codes').get(54)
        self.assertEqual(first, {'name': 'Afghanistan', 'code': 93, 'max_digits': None}, "fail")
        self.assertEqual(second, {'name': 'Dominican Republic', 'code': 1849, 'max_digits': None}, "fail")


    def test_personal_address_book(self):
        client, response = log_in_as_root()
        self.assertEqual(response.status_code, 200, response.content)

        response = client.get('/api/get_personal_address_book/')
        self.assertEqual(response.data.get("book"), [], response.content)

        addr = {"city_id": "0",
                "address":"Lenina 1",
                "postal_code":"123456",
                "country_id": "7",
                "region_id": "0",
                "region_name": "Tomskaya oblast",
                "city_name": "Tomsk",
                "personal_delivery": True}
        print(addr)
        response = client.post('/api/add_or_change_address/', addr)

        self.assertEqual(response.status_code, 200, response.content)
        self.assertNotEqual(response.data.get("address_id"), None, response.content)
        addr_id = response.data.get("address_id")

        response = client.get('/api/get_personal_address_book/')


        # self.assertEqual(response.data.get("book"), [], response.content)




























