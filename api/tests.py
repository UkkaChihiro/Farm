# -*- coding: utf-8 -*-
from django.test import TestCase, TransactionTestCase
from django.test import Client

import json

from django.contrib.auth.models import User

from geodata.models import Country
from core.models import CountryNumberphone




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


def convert_bytes_resp_to_dict(x):
    return json.loads(x.decode('utf8').replace("'", '"'))


class ApiViewTests(TransactionTestCase):
    fixtures = [
                'userdata/fixtures/for_test/users.json',
                # 'userdata/fixtures/for_test/business_profiles.json',
                'userdata/fixtures/for_test/classproduct.json',
                'geodata/fixtures/countries.json',
                'core/fixtures/languages.json',
                ]

    def qtest_alex_dashboard_personal(self):
        client = Client()

        response = client.post('/api/dashboard_personal/')

        self.assertEqual(response.status_code, 401, "user authenticated")
        self.assertEqual(
            response.data,
            {'detail': 'Authentication credentials were not provided.'},
            "user authenticated"
        )

        client, response = log_in("root", "123qwe123")

        response = client.post('/api/dashboard_personal/')

        self.assertEqual(response.status_code, 405, "post allowed")
        self.assertEqual(response.data, {'detail': 'Method "POST" not allowed.'}, "post allowed")

        response = client.get('/api/dashboard_personal/')

        u = User.objects.get(username='root')

        c = Country(
            name_en='VVf',
            show=True
        )
        c.save()

        cn = CountryNumberphone(
            code=123,
            country=c
        )
        cn.save()

        self.assertEqual(response.status_code, 200, "fail")
        self.assertEqual(response.data.get('user_id'), u.id, "fail")
        self.assertEqual(response.data.get('first_name'), u.first_name, "fail")
        self.assertEqual(response.data.get('last_name'), u.last_name, "fail")
        self.assertEqual(response.data.get('middle_name'), u.profile.middle_name, "fail")
        self.assertEqual(response.data.get('gender'), u.profile.gender, "fail")
        self.assertEqual(response.data.get('language'), u.profile.language.id, "fail")
        self.assertEqual(response.data.get('email'), u.email, "fail")
        self.assertEqual(response.data.get('confirmed_email'), u.profile.confirmed_email, "fail")
        self.assertEqual(response.data.get('number_phone'), u.profile.number_phone, "fail")

        u.first_name = 'hahaha'
        u.save()

        response = client.get('/api/dashboard_personal/')

        self.assertEqual(response.data.get('first_name'), u.first_name, "fail")


    def test_login(self):
        cl, response = log_in_as_testuser()
        self.assertEqual(response.status_code, 200, "Login failed")


    def test_dashboard_personal(self):
        cl, response = log_in_as_testuser()
        response = cl.get("/api/dashboard_personal/")

        self.assertEqual(response.status_code, 200, response.content)
        self.assertEqual(response.data.get("confirmed_email"), False, "confirmed_email incorrect")
        self.assertEqual(response.data.get("email"), "testuser@mail.ru", "email incorrect")
        self.assertEqual(response.data.get("birthday"), False, "birthday incorrect")
        self.assertEqual(response.data.get("gender"), 1, "gender incorrect")
        self.assertEqual(response.data.get("number_phone"), None, "number_phone incorrect")
        self.assertEqual(response.data.get("first_name"), '', "first_name incorrect")
        self.assertEqual(response.data.get("last_name"), '', "last_name incorrect")
        self.assertEqual(response.data.get("middle_name"), None, "last_name incorrect")



    def test_update_personal_profile(self):
        response = client.get("/api/dashboard_personal/")
        self.assertEqual(response.status_code, 401, response.content)

        cl, response = log_in_as_testuser()
        response = cl.get("/api/dashboard_personal/")
        old_prof = json.loads(str(response.content, encoding='utf8'))

        new_prof = {
            "first_name": "NewName",
            "last_name": "NewLastName",
            "middle_name": "NewMiddleName",
            "gender": 2,
            "birthday": ""
        }

        response = cl.post("/api/update_personal_profile/", new_prof)
        resp_dict = json.loads(str(response.content, encoding='utf8'))

        self.assertEqual(response.status_code, 200, response.content)
        self.assertDictEqual(resp_dict, new_prof, "Profile incorrect")

        empty_prof = {}

        response = cl.post("/api/update_personal_profile/", empty_prof)
        self.assertEqual(response.status_code, 400, "Empty prof")

        incorrect_fn = {"first_name": "", "last_name": "CorrectLN", "middle_name": "CorrectMN", "gender": 3, "birthday": "22.12.1990"}

        response = cl.post("/api/update_personal_profile/", incorrect_fn)
        self.assertEqual(response.status_code, 400, "Incorrect prof")


        incorrect_fn = {"first_name": "CorrectFN", "last_name": "", "middle_name": "CorrectMN", "gender": 3, "birthday": "22.12.1990"}

        response = cl.post("/api/update_personal_profile/", incorrect_fn)
        self.assertEqual(response.status_code, 400, "Incorrect prof")


        incorrect_fn = { "last_name": "CorrectLN", "middle_name": "CorrectMN", "gender": 3, "birthday": "22.12.1990"}

        response = cl.post("/api/update_personal_profile/", incorrect_fn)
        self.assertEqual(response.status_code, 400, "Incorrect prof")


        incorrect_fn = {"first_name": "CorrectFN", "middle_name": "CorrectMN", "gender": 3, "birthday": "22.12.1990"}

        response = cl.post("/api/update_personal_profile/", incorrect_fn)
        self.assertEqual(response.status_code, 400, "Incorrect prof")


        incorrect_fn = {"first_name": "CorrectFN", "middle_name": "CorrectMN"}

        response = cl.post("/api/update_personal_profile/", incorrect_fn)
        self.assertEqual(response.status_code, 400, "Incorrect prof")


    def test_get_personal_settings(self):
        response = client.get("/api/get_personal_settings/")
        self.assertEqual(response.status_code, 401, response.content)

        cl, response = log_in_as_testuser()

        settings = {"language": {"id": 1, "name": "English"},"class_product":[]}

        response = cl.get("/api/get_personal_settings/")

        self.assertEqual(response.status_code, 200, response.content)

        l = response.data.get("language")
        self.assertEqual(l.get("id"), 1, "incorrect id")
        self.assertEqual(l.get("name"), "English", "incorrect name")


    def test_update_personal_filter(self):
        cl, response = log_in_as_testuser()
        filter = {"class_product": [1]}

        response = cl.post("/api/update_personal_filter/", data=json.dumps(filter),content_type='application/json')
        self.assertEqual(response.status_code, 200)

        filter = {"class_product": []}

        response = cl.post("/api/update_personal_filter/", data=json.dumps(filter),content_type='application/json')
        self.assertEqual(response.status_code, 200)

        filter = {"class_product": [2]}

        response = cl.post("/api/update_personal_filter/", data=json.dumps(filter),content_type='application/json')
        self.assertEqual(response.status_code, 400)

        self.assertJSONEqual(str(response.content, encoding='utf8'), filter)


    def test_update_personal_language(self):
        language = {"language": 1}
        response = client.post("/api/update_personal_language/", data=json.dumps(language), content_type='application/json')
        self.assertEqual(response.status_code, 401, response.content)

        cl, response = log_in_as_testuser()
        language = {"language": 1}

        response = cl.post("/api/update_personal_language/", data=json.dumps(language), content_type='application/json')
        self.assertEqual(response.status_code, 200, response.content)

        language = {"language": ""}

        response = cl.post("/api/update_personal_language/", data=json.dumps(language), content_type='application/json')
        self.assertEqual(response.status_code, 400, response.content)

        language = {"language": 222}

        response = cl.post("/api/update_personal_language/", data=json.dumps(language), content_type='application/json')
        self.assertEqual(response.status_code, 400, response.content)

        self.assertJSONEqual(str(response.content, encoding='utf8'), filter)


    # def test_get_form_update_profile(self):
    #     response = client.get("/api/get_form_update_profile/")
    #     self.assertEqual(response.status_code, 401, response.content)
    # 
    #     cl, response = log_in_as_testuser()
    # 
    #     response = cl.get("/api/get_form_update_profile/")
    #     self.assertEqual(response.status_code, 400, response.content)
    # 
    #     cl.get("/api/sign_out/")
    #     cl, response = log_in("businesuser", "123qwe123")
    # 
    #     response = cl.get("/api/get_form_update_profile/")
    #     self.assertEqual(response.status_code, 200, response.content)
    # 
    # 
    # def test_update_business_avatar(self):
    #     with open('barrrrrr.jpg') as avatar:
    #         response = client.post("/api/update_business_avatar/", {"avatar": {"attachment": avatar}})
    # 
    #     self.assertEqual(response.status_code, 401, response.content)
    # 
    #     cl, response = log_in_as_root()
    # 
    #     with open('barrrrrr.jpg') as avatar:
    #         response = cl.post("/api/update_business_avatar/", {"avatar": {"attachment": avatar}})
    #     self.assertEqual(response.status_code, 400, response.content)
    # 
    #     cl.get("/api/sign_out/")
    #     # cl, response = log_in("businessuser", "123qwe123")
    #     cl, response = log_in_as_root()
    # 
    #     # f = open('/home/julia/efarm/barrrrrr.jpg', 'w')
    #     with open('barrrrrr.jpg', 'rb') as a:
    #         aa = a.read()
    #         # encoded_string = base64.b64encode(a).decode()
    #         print(aa.encode("base64"))
    #         response = cl.post("/api/update_personal_avatar/", {"avatar": a.encode("base64")})
    # 
    #     print(response.content)
    #     self.assertEqual(response.status_code, 200, response.content)
    #     #
    #     # response = cl.post("/api/update_personal_avatar/", {"avatar": ""})
    #     # self.assertEqual(response.status_code, 200, response.content)
    #     #
    #     # response = cl.post("/api/update_personal_avatar/", {})
    #     # self.assertEqual(response.status_code, 200, response.content)
    # 
    # 
    # def test_update_business_about_me(self):
    #     data = {"about_me":"Text"}
    #     response = client.post("/api/update_business_avatar/", data)
    # 
    #     self.assertEqual(response.status_code, 401, response.content)
    # 
    #     cl, response = log_in_as_testuser()
    # 
    #     response = cl.post("/api/update_business_avatar/", data)
    #     self.assertEqual(response.status_code, 400, response.content)
    # 
    #     cl.get("/api/sign_out/")
    #     cl, response = log_in("businessuser", "123qwe123")
    # 
    #     response = cl.post("/api/update_business_avatar/", data)
    #     self.assertEqual(response.status_code, 200, response.content)
    # 
    # 
    # def test_send_msg_reset_password(self):
    #     correct_email = {"email": "testuser@mail.ru"}
    #     response = client.post("/api/send_msg_reset_password/", correct_email)
    #     self.assertEqual(response.status_code, 200, response.content)
    # 
    #     incorrect_email = {"email": "johnsnow@winterfell.zz"}
    #     response = client.post("/api/send_msg_reset_password/", incorrect_email)
    #     self.assertEqual(response.status_code, 400, response.content)
    # 
    #     incorrect_email = {"email": ""}
    #     response = client.post("/api/send_msg_reset_password/", incorrect_email)
    #     self.assertEqual(response.status_code, 400, response.content)
    # 
    #     incorrect_email = {}
    #     response = client.post("/api/send_msg_reset_password/", incorrect_email)
    #     self.assertEqual(response.status_code, 400, response.content)
    #      #check mail
    #     #check db
    # 
    # 
    # def inwork_test_upgrade_profile_to_business(self):
    #     cl, response = log_in_as_testuser()
    #     photo = open('barrrrrr.jpg')
    # 
    #     data = {
    #     "terms_of_use": True,
    #     "type_of_business": 1,
    #     "organization_type": 1,
    #     "organization_name": "KJBKJBkjbkb scc",
    #     "vat": "131232414",
    #     "registration_number": "892GGv2",
    #     "first_name": "JHbbk",
    #     "last_name": "Mmslxm",
    #     "position": "M2bn",
    #     "legal_address": {
    #         "city": 1,
    #         "address": "jfbvb 23124",
    #         "postal_code" :"12312"
    #     },
    #     "delivery_address":{
    #         "city": 1,
    #         "address": "FGG 3",
    #         "postal_code" :"543"
    #     },
    #     "phone_number": "444444",
    #     "email": "kbkvv@kbkjbkjbjkb.rl",
    #     "photos": {"attachment": photo}
    #     }
    #     with open('barrrrrr.jpg') as photo:
    #         response = cl.post("/api/upgrade_profile_to_business/", data=json.dumps(data), content_type='application/json')
    #     self.assertEqual(response.status_code, 200, response.content)
    # 
    # 
    # 
    #     # self.assertJSONEqual(str(response.content, encoding='utf8'), filter)
    # 
    # 
    # 
    # 
    # 
    # 
    # 
    # 
    # 
    # 
    # 
    # 
    # 
    # 
    # 
    # 
    # 
    # 
    # 
    # 
    # 
    # 
    # 
    # 
    # 
    # 
    # 
    # 
    # 
    # 
    # 
    # 
    # 
    # 
    # 
    # 
    # 
    # 
    # 
    # # def test_check_auth(self):
    # #     # client, response = log_in("root", "123qwe123")
    # #
    # #     response = client.get("/api/check_auth/")
    # #     self.assertEqual(response.status_code, 200, "User not authenticated")
    # #
    # #
    # # def test_sign_out(self):
    # #     cl, response = client.get("/api/sign_out/")
    # #     self.assertEqual(response.status_code, 200, response.content)
    # 
    # #
    # # def test_send_msg_reset_password(self):
    # #     pass
    # #
    # # def test_create_user(self):
    # #     client = Client()
    # #
    # #     data = {
    # #             "email": "11",
    # #             "password": {
    # #                 "first": "123qwe123qwe",
    # #                 "second": "123qwe123qwe"
    # #             },
    # #             "first_name": "U",
    # #             "last_name": "Uuk",
    # #             "num_phone": "555555",
    # #             "check": True
    # #             }
    # #
    # #     response = client.post("/api/create_account/", data=json.dumps(data), content_type='application/json')
    # #     self.assertEqual(response.status_code, 400, "User with wrong email created")
    # #
    # #     data = {
    # #             "email": "test2@tt.tt",
    # #             "password": {
    # #                 "first": "1",
    # #                 "second": "123qwe123qwe"
    # #             },
    # #             "first_name": "U",
    # #             "last_name": "Uuk",
    # #             "num_phone": "555555",
    # #             "check": True
    # #             }
    # #
    # #     response = client.post("/api/create_account/", data=json.dumps(data), content_type='application/json')
    # #     self.assertEqual(response.status_code, 400, "User with wrong password created")
    # #
    # #     empty_data = {
    # #             "email": "",
    # #             "password": {
    # #                 "first": "",
    # #                 "second": ""
    # #             },
    # #             "first_name": "",
    # #             "last_name": "",
    # #             "num_phone": "",
    # #             "check": ''
    # #             }
    # #
    # #     response = client.post("/api/create_account/", data=json.dumps(empty_data), content_type='application/json')
    # #     self.assertEqual(response.status_code, 400, "User with empty fields created")
    # #
    # #     correct_data = {
    # #         "email": "test@email.ru",
    # #         "password": {
    # #             "first": "123qwe123qwe",
    # #             "second": "123qwe123qwe"
    # #         },
    # #         "first_name": "U",
    # #         "last_name": "Uuk",
    # #         "num_phone": "555555",
    # #         "check": True
    # #     }
    # #
    # #     response = client.post("/api/create_account/", data=json.dumps(correct_data), content_type='application/json')
    # #     self.assertEqual(response.status_code, 200, "User not created")
    # 
    # #
    # # def test_change_acc(self):
    # #     client, response = log_in("TestUser", "123qwe123qwe")
    # #
    # #     correct_data = {
    # #         "email": "change_email@mylo.ru",
    # #         "password": {
    # #             "first": "qwerty12345",
    # #             "second": "qwerty12345"
    # #         },
    # #         "num_phone": "111"
    # #     }
    # #
    # #     response = client.post("/api/change_account/", data=json.dumps(correct_data), content_type='application/json')
    # #     self.assertEqual(response.status_code, 200, response.content)#, "User with correct data was not changed")
    # #
    # #     changed_user = User.objects.filter(username="TestUser", email="change_email@mylo.ru").count()
    # #     self.assertTrue(changed_user != 0, "Changed user not found in DB!")
    # #
    # #
    # # # def test_add_prod(self):
    # # #     client, response = log_in("TestUser", "123qwe123qwe")
    # # #
    # # #     data = {
    # # #         "name": "test prod",
    # # #         "description": "trampampam",
    # # #         "weight": "100",
    # # #         "measure": "g",
    # # #         "expiration_date": "",
    # # #         "coast": "123",
    # # #         "class_product": 1,
    # # #         "photos": False,
    # # #         "video": False
    # # #     }
    # # #     response = client.post("/api/add_product/", data=json.dumps(data), content_type='application/json')
    # # #     self.assertEqual(response.status_code, 200, "Product was not created")
    # #
    # #
    # # def test_dashboard_personal(self):
    # #     client, response = log_in("TestUser", "123qwe123qwe")
    # #     response = client.get("/api/dashboard_personal/")
    # #
    # #     self.assertEqual(response.status_code, 200, response.content)
    # #     ex_list = (
    # #         "last_name",
    # #         # "about_me_eng",
    # #         # "confirmed_phone",
    # #         "birthday",
    # #         # "about_me",
    # #         "first_name",
    # #         "middle_name",
    # #         # "language",
    # #         "gender",
    # #         # "confirmed_email",
    # #         "number_phone",
    # #         "avatar",
    # #         "email",
    # #         "password_updated"
    # #        )
    # #     for i in ex_list:
    # #         self.assertContains(response, i)
    # #
    # # # def test_upgrade_profile_to_business(self):
    # # #     pass
    # # #
    # # # def test_dashboard_business(self):
    # # #     pass
    # # #
    # # # def test_add_product(self):
    # # #     pass
    # # #
    # # # def test_update_business_avatar(self):
    # # #     pass
    # # #
    # # # def test_update_business_about_me(self):
    # # #     pass
    # #
    # # def test_change_password(self):
    # #     client, response = log_in("TestUser", "123qwe123qwe")
    # #     data = {
    # #             "old_password":"123qwe123qwe",
    # #             "new_password":{"first":"newPASSWORD123", "second":"newPASSWORD123"}
    # #             }
    # #
    # #     response = client.post("/api/change_password/", data=json.dumps(data), content_type='application/json')
    # #     self.assertEqual(response.status_code, 200, "Password was not changed")
    # #
    # #     user = User.objects.get(username='TestUser')
    # #     self.assertTrue(user.check_password("newPASSWORD123"), "Password didn't saved in db")
    # #
    # # def test_update_personal_profile(self):
    # #     client, response = log_in("TestUser", "123qwe123qwe")
    # #     data = {
    # #         "first_name":"Avraam",
    # #          "last_name":"Linkoln",
    # #         "middle_name":"Petrovich",
    # #         "gender":3,
    # #         "birthday":"2003-02-01"
    # #         }
    # #
    # #     response = client.post("/api/update_personal_profile/", data=json.dumps(data), content_type='application/json')
    # #     self.assertEqual(response.status_code, 200, "Personal profile was not changed")
    # #
    # # def test_get_address_book(self):
    # #     client, response = log_in("TestUser", "123qwe123qwe")
    # #     response = client.get("/api/get_address_book/")
    # #     self.assertEqual(response.status_code, 200, response.content)
    # #     adr_keys = (
    # #         "city",
    # #         "address",
    # #         "postal_code",
    # #         "delivery_personal",
    # #         "delivery_business",
    # #         "legal",
    # #         "pick_up",
    # #         "delivery_docs"
    # #     )
    # #     for i in adr_keys:
    # #         self.assertContains(response, i)
    # #
    # # def test_add_delivery_address(self):
    # #     client, response = log_in("TestUser", "123qwe123qwe")
    # #     correct_data = {
    # #         "delivery_address":{
    # #             "city":"1",
    # #             "address":"New address",
    # #             "postal_code":"123456"
    # #         }
    # #     }
    # #
    # #     response = client.post("/api/add_delivery_address/", data=json.dumps(correct_data), content_type='application/json')
    # #     self.assertEqual(response.status_code, 200, response.content)
    # #
    # #     user = User.objects.get(username = "TestUser")
    # #     addr = Address.objects.filter(user=user, city="1", address="New address", postal_code="123456")
    # #     self.assertTrue(addr[0], "Address was not saved in db")
    # #
    # # def test_change_delivery_address(self):
    # #     client, response = log_in("TestUser", "123qwe123qwe")
    # #     user = User.objects.get(username="TestUser")
    # #     city = City.objects.get(name="Tomsk")
    # #     addr = Address.objects.filter(user=user)
    # #     addr_id = addr[0].id
    # #     data = {"old_delivery_address_id":addr_id,
    # #             "new_delivery_address":{
    # #                 "city":city.id,
    # #                 "address":"Changed address",
    # #                 "postal_code":"123456"
    # #             }}
    # #
    # #     response = client.post("/api/change_delivery_address/", data=json.dumps(data), content_type='application/json')
    # #     self.assertEqual(response.status_code, 200, response.content)
    # #
    # #     old_addr = Address.objects.filter(user=user, city="1", address="Lenina 8", postal_code="654321").count()
    # #     self.assertTrue(old_addr==0, "Old address was found in db")
    # #
    # #     new_addr = Address.objects.filter(user=user, city=city.id, address="Changed address", postal_code="123456").count()
    # #     self.assertFalse(new_addr==0, "Changed address was not saved in db")
    # #
    # # def test_delete_delivery_address(self):
    # #     client, response = log_in("TestUser", "123qwe123qwe")
    # #     user = User.objects.get(username="TestUser")
    # #
    # #     addr = Address.objects.filter(user=user)
    # #     addr_id = addr[0].id
    # #     data = {"address_id":addr_id}
    # #
    # #     response = client.post("/api/delete_delivery_address/", data=json.dumps(data), content_type='application/json')
    # #     self.assertEqual(response.status_code, 200, response.content)
    # #
    # #     old_addr = Address.objects.filter(user=user, id=addr_id).count()
    # #     self.assertTrue(old_addr==0, "Deleted address was found in db")
    # #
    # # # def test_add_product(self):
    # #
    # 













