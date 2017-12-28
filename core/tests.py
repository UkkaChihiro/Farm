from django.test import TestCase, TransactionTestCase
from django.test import Client

from django.core.cache import cache
from django.contrib.auth.models import User

from rest_framework.authtoken.models import Token

import json

from userdata.models import ProfileBusiness, Confirmation
from core.models import ResetPassword, CountryNumberphone
from geodata.models import Country




def log_in(username, password):
    client = Client()
    data = {
        "username": username,
        "password": password
    }
    response = client.post("/api/sign_in/", data=json.dumps(data), content_type='application/json')

    return client, response


class CoreViewTests(TestCase):
    fixtures = [
        'userdata/fixtures/users.json',
        'geodata/fixtures/countries.json',
        'core/fixtures/country_codes.json',
    ]

    def test_sign_in(self):
        client, response = log_in("root", "123qwe123wdf")

        self.assertEqual(response.status_code, 400, "Login with Incorrect password")
        self.assertEqual(response.data, {'error': 'incorrect data'}, "Login with Incorrect data")

        client, response = log_in("root", "123qwe123")

        u = User.objects.get(username="root")
        t = Token.objects.get(user=u)

        self.assertEqual(response.status_code, 200, "Login failed")
        self.assertEqual(response.data, {"token": t.key}, "return Incorrect token")


    def test_sign_out(self):
        client = Client()
        response = client.get("/api/sign_out/")

        self.assertEqual(response.status_code, 200, "Logout fail to unlogin")
        self.assertEqual(response.data, {"status": "ok"}, "Logout fail to unlogin")

        client, response = log_in("root", "123qwe123")

        response = client.get("/api/sign_out/")

        self.assertEqual(response.status_code, 200, "Logout fail to login")
        self.assertEqual(response.data, {"status": "ok"}, "Logout fail to unlogin")

        response = client.post("/api/sign_out/")

        self.assertEqual(response.status_code, 405, "post allowed")
        self.assertEqual(response.data, {'detail': 'Method "POST" not allowed.'}, "post allowed")


    def test_check_auth(self):
        client = Client()
        response = client.get("/api/check_auth/")

        self.assertEqual(response.status_code, 401, "user authenticated")
        self.assertEqual(response.data, {"error": "not authenticated"}, "user authenticated")

        client, response = log_in("root", "123qwe123")

        cache.delete('1')

        response = client.get("/api/check_auth/")

        self.assertEqual(response.status_code, 200, "Logout fail to login")
        # self.assertEqual(response.data, {'is_business': False, 'profile': 'personal'}, "Logout fail to login")

        u = User.objects.get(username="root")
        ProfileBusiness(profile=u.profile).save()

        response = client.get("/api/check_auth/")

        self.assertEqual(response.status_code, 200, "Logout fail to login")
        self.assertEqual(response.data, {'business_confirmed': False, 'is_business': True, 'profile': 'personal'}, "Logout fail to login")

        response = client.get('/api/change_profile/')
        print(response.content)
        response = client.get("/api/check_auth/")

        self.assertEqual(response.status_code, 200, "Logout fail to login")
        self.assertEqual(response.data, {'business_confirmed': False, 'is_business': True, 'profile': 'business'}, "Logout fail to login")

        response = client.post("/api/check_auth/")

        self.assertEqual(response.status_code, 405, "post allowed")
        self.assertEqual(response.data, {'detail': 'Method "POST" not allowed.'}, "post allowed")


    def test_logout_from_all_devices(self):
        client = Client()
        response = client.get('/api/logout_from_all_devices/')

        self.assertEqual(response.status_code, 401, "already login")
        self.assertEqual(
            response.data,
            {'detail': 'Authentication credentials were not provided.'},
            "already login"
        )

        client, response = log_in("root", "123qwe123")
        response = client.get('/api/logout_from_all_devices/')

        u = User.objects.get(username="root")
        t = Token.objects.get(user=u)

        self.assertEqual(response.status_code, 200, "already login")
        self.assertEqual(response.data, {"token": t.key}, "return Incorrect token")

        client, response = log_in("root", "123qwe123")
        response = client.post('/api/logout_from_all_devices/')

        self.assertEqual(response.status_code, 405, "post allowed")
        self.assertEqual(response.data, {'detail': 'Method "POST" not allowed.'}, "post allowed")


    def test_change_profile(self):
        client = Client()
        response = client.get('/api/change_profile/')

        self.assertEqual(response.status_code, 401, "already login")
        self.assertEqual(
            response.data,
            {'detail': 'Authentication credentials were not provided.'},
            "already login"
        )

        client, response = log_in("root", "123qwe123")

        cache.delete('1')

        response = client.get('/api/change_profile/')

        self.assertEqual(response.status_code, 200, "fail")
        self.assertEqual(response.data, {'use_profile': 'personal'},"fail")

        response = client.get('/api/change_profile/')

        self.assertEqual(response.status_code, 200, "fail")
        self.assertEqual(response.data, {'use_profile': 'personal'}, "have business profile")

        u = User.objects.get(username="root")
        ProfileBusiness(profile=u.profile).save()

        response = client.get('/api/change_profile/')

        self.assertEqual(response.status_code, 200, "fail")
        self.assertEqual(response.data, {'use_profile': 'business'}, "fail")

        response = client.post('/api/change_profile/')

        self.assertEqual(response.status_code, 405, "post allowed")
        self.assertEqual(response.data, {'detail': 'Method "POST" not allowed.'}, "post allowed")


    def test_gen_email_confirmation(self):
        client = Client()
        response = client.post('/api/gen_email_confirmation/')

        self.assertEqual(response.status_code, 401, "already login")
        self.assertEqual(
            response.data,
            {'detail': 'Authentication credentials were not provided.'},
            "already login"
        )

        client, response = log_in("root", "123qwe123")

        response = client.get('/api/gen_email_confirmation/')

        self.assertEqual(response.status_code, 405, "method get no allowed")
        self.assertEqual(response.data, {'detail': 'Method "GET" not allowed.'}, "method get no allowed")

        u = User.objects.get(username="root")
        u.profile.confirmed_email = True
        u.profile.save()

        response = client.post('/api/gen_email_confirmation/')

        self.assertEqual(response.status_code, 400, "fail")
        self.assertEqual(response.data, {'error': 'email already confirmed'}, "fail")

        response = client.post('/api/gen_email_confirmation/', {'email':'root@mail.ru'})

        self.assertEqual(response.status_code, 400, "fail")
        self.assertEqual(response.data, {'error': 'email already confirmed'}, "fail")

        response = client.post('/api/gen_email_confirmation/', data={'email': 'rootggggg@m'})

        self.assertEqual(response.status_code, 400, "fail")
        self.assertEqual(response.data, {'error': 'incorrect email'}, "fail")

        tuser = User.objects.create_user('test', 'test@test.ru', '123qwe123')
        tuser.save()

        response = client.post('/api/gen_email_confirmation/', {'email': 'test@test.ru'})

        self.assertEqual(response.status_code, 400, "fail")
        self.assertEqual(response.data, {'error': 'this email already exist'}, "fail")

        u.profile.confirmed_email = False
        u.profile.save()

        conf_first = Confirmation.objects.filter(user=u).exists()

        response = client.post('/api/gen_email_confirmation/')

        self.assertEqual(response.status_code, 200, "fail")
        self.assertEqual(response.data, {'status': 'ok'}, "fail")

        conf_second = Confirmation.objects.filter(user=u).exists()

        self.assertEqual(conf_first, False, 'fail')
        self.assertEqual(conf_second, True, 'fail')

        conf_first = Confirmation.objects.get(user=u)

        response = client.post('/api/gen_email_confirmation/')

        conf_second = Confirmation.objects.get(user=u)

        self.assertEqual(response.status_code, 200, "fail")
        self.assertEqual(response.data, {'status': 'ok'}, "fail")

        response = client.post('/api/gen_email_confirmation/')

        self.assertEqual(response.status_code, 200, "fail")
        self.assertEqual(response.data, {'status': 'ok'}, "fail")

        self.assertNotEqual(conf_first.key, conf_second.key, 'fail')


    def test_confirm_email(self):
        client = Client()
        response = client.post('/api/confirm_email/')

        self.assertEqual(response.status_code, 401, "already login")
        self.assertEqual(
            response.data,
            {'detail': 'Authentication credentials were not provided.'},
            "already login"
        )

        client, response = log_in("root", "123qwe123")

        response = client.get('/api/confirm_email/')

        self.assertEqual(response.status_code, 405, "method get no allowed")
        self.assertEqual(response.data, {'detail': 'Method "GET" not allowed.'}, "method get no allowed")

        response = client.post('/api/confirm_email/')

        self.assertEqual(response.status_code, 400, "fail")
        self.assertEqual(response.data, {'error': 'Empty email or key'}, "fail")

        response = client.post('/api/confirm_email/', {'email': 'root@mail.ru'})

        self.assertEqual(response.status_code, 400, "fail")
        self.assertEqual(response.data, {'error': 'Empty email or key'}, "fail")

        response = client.post('/api/confirm_email/', {'key': 'fhdhdgfhdghfga734'})

        self.assertEqual(response.status_code, 400, "fail")
        self.assertEqual(response.data, {'error': 'Empty email or key'}, "fail")

        response = client.post('/api/confirm_email/', {'email': 'root@mail.ru', 'key': 'gqrgergqer'})

        self.assertEqual(response.status_code, 400, "fail")
        self.assertEqual(response.data, {'error': 'User has not confirmation key for email'}, "fail")

        client.post('/api/gen_email_confirmation/')

        u = User.objects.get(username="root")
        conf = Confirmation.objects.get(user=u)

        response = client.post('/api/confirm_email/', {'email': 'root@mail.ru', 'key': 'gqrgergqer'})

        self.assertEqual(response.status_code, 400, "fail")
        self.assertEqual(response.data, {'error': 'Email and key are incorrect'}, "fail")

        response = client.post('/api/confirm_email/', {'email': 'root@mail.', 'key': 'gqrgergqer'})

        self.assertEqual(response.status_code, 400, "fail")
        self.assertEqual(response.data, {'error': 'Email and key are incorrect'}, "fail")

        response = client.post('/api/confirm_email/', {'email': 'root@mail.ru', 'key': conf.key})

        self.assertEqual(response.status_code, 200, "fail")
        self.assertEqual(response.data, {'status': 'ok'}, "fail")

        response = client.post('/api/confirm_email/', {'email': 'root@mail.ru', 'key': conf.key})

        self.assertEqual(response.status_code, 400, "fail")
        self.assertEqual(response.data, {'error': 'Email has already confirmed'}, "fail")


    def test_gen_email_reset_password(self):
        client = Client()
        response = client.post('/api/gen_email_reset_password/')

        response = client.get('/api/gen_email_reset_password/')

        self.assertEqual(response.status_code, 405, "method get no allowed")
        self.assertEqual(response.data, {'detail': 'Method "GET" not allowed.'}, "method get no allowed")

        response = client.post('/api/gen_email_reset_password/')

        self.assertEqual(response.status_code, 400, "fail")
        self.assertEqual(response.data, {'error': 'Empty email'}, "fail")

        response = client.post('/api/gen_email_reset_password/', {'email':'root@mail.rut'})

        self.assertEqual(response.status_code, 400, "fail")
        self.assertEqual(response.data, {'error': 'Incorrect email'}, "fail")

        r_p = ResetPassword.objects.filter(email='root@mail.ru').exists()

        self.assertEqual(r_p, False, 'fail')

        response = client.post('/api/gen_email_reset_password/', {'email': 'root@mail.ru'})

        self.assertEqual(response.status_code, 200, "fail")
        self.assertEqual(response.data, {'status': 'ok'}, "fail")

        r_p_first = ResetPassword.objects.get(email='root@mail.ru')

        response = client.post('/api/gen_email_reset_password/', {'email': 'root@mail.ru'})

        self.assertEqual(response.status_code, 200, "fail")
        self.assertEqual(response.data, {'status': 'ok'}, "fail")

        r_p_second = ResetPassword.objects.get(email='root@mail.ru')

        self.assertNotEqual(r_p_first.key, r_p_second.key, "fail")


    def test_reset_password(self):
        client = Client()

        response = client.get('/api/reset_password/')

        self.assertEqual(response.status_code, 405, "method get no allowed")
        self.assertEqual(response.data, {'detail': 'Method "GET" not allowed.'}, "method get no allowed")

        response = client.post('/api/reset_password/')

        self.assertEqual(response.status_code, 400, "fail")
        self.assertEqual(response.data, {'error': 'Empty email'}, "fail")

        response = client.post('/api/reset_password/', data={'email': 'root@mail.ru'})

        self.assertEqual(response.status_code, 400, "fail")
        self.assertEqual(response.data, {'error': 'Empty key'}, "fail")

        response = client.post('/api/reset_password/', data={'email': 'root@mail.ru', 'key': 'gghfghhg'})

        self.assertEqual(response.status_code, 400, "fail")
        self.assertEqual(response.data, {'error': 'Empty password'}, "fail")

        response = client.post('/api/reset_password/', data={
            'email': 'root@mail.ru', 'key': 'gghfghhg', 'password': 'fg'
        })

        self.assertEqual(response.status_code, 400, "fail")
        self.assertEqual(response.data, {'error': 'Incorrect email or key'}, "fail")

        client.post('/api/gen_email_reset_password/', {'email': 'root@mail.ru'})
        r_p = ResetPassword.objects.get(email='root@mail.ru')

        data = {
            'email': 'root@mail.ru',
            'key': r_p.key,
            'password': {'rf': 'dfsdf', 'fre': 55}
        }

        response = client.post('/api/reset_password/', data=json.dumps(data), content_type='application/json')

        self.assertEqual(response.status_code, 400, "fail")
        self.assertEqual(response.data, {'error': 'Incorrect password'}, "fail")

        client.post('/api/gen_email_reset_password/', {'email': 'root@mail.ru'})
        r_p = ResetPassword.objects.get(email='root@mail.ru')

        data = {
            'email': 'root@mail.ru',
            'key': r_p.key,
            'password': {'first': 'dfsdf', 'second': 'dfvdfvf'}
        }

        response = client.post('/api/reset_password/', data=json.dumps(data), content_type='application/json')

        self.assertEqual(response.status_code, 400, "fail")
        self.assertEqual(response.data, {'error': 'Incorrect password'}, "fail")

        client.post('/api/gen_email_reset_password/', {'email': 'root@mail.ru'})
        r_p = ResetPassword.objects.get(email='root@mail.ru')

        data = {
            'email': 'root@mail.ru',
            'key': r_p.key,
            'password': {'first': '123qwe', 'second': '123qwe'}
        }

        response = client.post('/api/reset_password/', data=json.dumps(data), content_type='application/json')

        self.assertEqual(response.status_code, 400, "fail")
        self.assertEqual(response.data, {'error': 'Incorrect password'}, "fail")

        client.post('/api/gen_email_reset_password/', {'email': 'root@mail.ru'})
        r_p = ResetPassword.objects.get(email='root@mail.ru')

        data = {
            'email': 'root@mail.ru',
            'key': r_p.key,
            'password': {'first': '123qwe123', 'second': '123qwe13'}
        }

        response = client.post('/api/reset_password/', data=json.dumps(data), content_type='application/json')

        self.assertEqual(response.status_code, 400, "fail")
        self.assertEqual(response.data, {'error': 'Incorrect password'}, "fail")

        client.post('/api/gen_email_reset_password/', {'email': 'root@mail.ru'})
        r_p = ResetPassword.objects.get(email='root@mail.ru')

        data = {
            'email': 'root@mail.ru',
            'key': r_p.key,
            'password': {'first': '123qwe123', 'second': '123qwe123'}
        }

        response = client.post('/api/reset_password/', data=json.dumps(data), content_type='application/json')

        u = User.objects.get(username="root")
        t = Token.objects.get(user=u)

        self.assertEqual(response.status_code, 200, "fail")
        self.assertEqual(response.data, {'token': t.key}, "fail")


    def test_create_account(self):
        client = Client()

        response = client.get('/api/create_account/')

        self.assertEqual(response.status_code, 405, "method get no allowed")
        self.assertEqual(response.data, {'detail': 'Method "GET" not allowed.'}, "method get no allowed")

        response = client.post('/api/create_account/')

        self.assertEqual(response.status_code, 400, "fail")
        self.assertEqual(response.data, {'error': 'Empty email'}, "fail")

        data = {
            'email': 'test1@mail.ru'
        }

        response = client.post('/api/create_account/', data=json.dumps(data), content_type='application/json')

        self.assertEqual(response.status_code, 400, "fail")
        self.assertEqual(response.data, {'error': 'Empty password'}, "fail")

        data = {
            'email': 1
        }

        response = client.post('/api/create_account/', data=json.dumps(data), content_type='application/json')

        self.assertEqual(response.status_code, 400, "fail")
        self.assertEqual(response.data, {'error': 'Incorrect type email (need str)'}, "fail")

        data = {
            'email': 'test1@mail.ru',
            'password': 'fg'
        }

        response = client.post('/api/create_account/', data=json.dumps(data), content_type='application/json')

        self.assertEqual(response.status_code, 400, "fail")
        self.assertEqual(response.data, {'error': 'Incorrect type password (need dict)'}, "fail")

        data = {
            'email': 'test1@mail.ru',
            'password': {'fg': 'gfg'}
        }

        response = client.post('/api/create_account/', data=json.dumps(data), content_type='application/json')

        self.assertEqual(response.status_code, 400, "fail")
        self.assertEqual(response.data, {'error': 'Empty first name'}, "fail")

        data = {
            'email': 'test1@mail.ru',
            'password': {'fg':'gfg'},
            'first_name': ['test'],
        }

        response = client.post('/api/create_account/', data=json.dumps(data), content_type='application/json')

        self.assertEqual(response.status_code, 400, "fail")
        self.assertEqual(response.data, {'error': 'Incorrect type first_name (need str)'}, "fail")

        data = {
            'email': 'test1@mail.ru',
            'password': {'fg': 'gfg'},
            'first_name': 'test',
        }

        response = client.post('/api/create_account/', data=json.dumps(data), content_type='application/json')

        self.assertEqual(response.status_code, 400, "fail")
        self.assertEqual(response.data, {'error': 'Empty last name'}, "fail")

        data = {
            'email': 'test1@mail.ru',
            'password': {'fg': 'gfg'},
            'first_name': 'test',
            'last_name': 0.554
        }

        response = client.post('/api/create_account/', data=json.dumps(data), content_type='application/json')

        self.assertEqual(response.status_code, 400, "fail")
        self.assertEqual(response.data, {'error': 'Incorrect type last_name (need str)'}, "fail")

        data = {
            'email': 'test1@mail.ru',
            'password': {'fg': 'gfg'},
            'first_name': 'test',
            'last_name': 'fgftest'
        }

        response = client.post('/api/create_account/', data=json.dumps(data), content_type='application/json')

        self.assertEqual(response.status_code, 400, "fail")
        self.assertEqual(response.data, {'error': 'You should agree with rools'}, "fail")

        data = {
            'email': 'test1@mail.ru',
            'password': {'fg': 'gfg'},
            'first_name': 'test',
            'last_name': 'testsds',
            'check': False
        }

        response = client.post('/api/create_account/', data=json.dumps(data), content_type='application/json')

        self.assertEqual(response.status_code, 400, "fail")
        self.assertEqual(response.data, {'error': 'You should agree with rools'}, "fail")

        data = {
            'email': 'test1@mail.ru',
            'password': {'fg': 'gfg'},
            'first_name': 'test',
            'last_name': 'testsds',
            'check': True,
            'middle_name': [{3:'ffd'}]
        }

        response = client.post('/api/create_account/', data=json.dumps(data), content_type='application/json')

        self.assertEqual(response.status_code, 400, "fail")
        self.assertEqual(response.data, {'error': 'Incorrect type middle_name (need str)'}, "fail")

        data = {
            'email': 'test1@mail.ru',
            'password': {'fg': 'gfg'},
            'first_name': 'test',
            'last_name': 'testsds',
            'check': True,
            'middle_name': 'ffd',
            'code_id': 1.58
        }

        response = client.post('/api/create_account/', data=json.dumps(data), content_type='application/json')

        self.assertEqual(response.status_code, 400, "fail")
        self.assertEqual(response.data, {'error': 'Incorrect type code_id (need int)'}, "fail")

        data = {
            'email': 'test1@mail.ru',
            'password': {'fg': 'gfg'},
            'first_name': 'test',
            'last_name': 'testsds',
            'check': True,
            'middle_name': 'ffd',
            'code_id': 10,
            'number_phone': 'fhfdh'
        }

        response = client.post('/api/create_account/', data=json.dumps(data), content_type='application/json')

        self.assertEqual(response.status_code, 400, "fail")
        self.assertEqual(response.data, {'error': 'Incorrect type number_phone (need int)'}, "fail")

        data = {
            'email': 'test1@mail.ru',
            'password': {'fg': 'gfg'},
            'first_name': 'test',
            'last_name': 'testsds',
            'check': True,
            'middle_name': 'ffd',
            'code_id': 10,
            'number_phone': 'fhfdh'
        }

        response = client.post('/api/create_account/', data=json.dumps(data), content_type='application/json')

        self.assertEqual(response.status_code, 400, "fail")
        self.assertEqual(response.data, {'error': 'Incorrect type number_phone (need int)'}, "fail")

        data = {
            'email': 'test1@mail.ru',
            'password': {'fg': 'dfdf'},
            'first_name': 'test',
            'last_name': 'testsds',
            'check': True
        }

        response = client.post('/api/create_account/', data=json.dumps(data), content_type='application/json')

        self.assertEqual(response.status_code, 400, "fail")
        self.assertEqual(response.data, {'error': 'Empty piece of passwords'}, "fail")

        data = {
            'email': 'test1@mail.ru',
            'password': {'first': 'dfdf'},
            'first_name': 'test',
            'last_name': 'testsds',
            'check': True
        }

        response = client.post('/api/create_account/', data=json.dumps(data), content_type='application/json')

        self.assertEqual(response.status_code, 400, "fail")
        self.assertEqual(response.data, {'error': 'Empty piece of passwords'}, "fail")

        data = {
            'email': 'test1@mail.ru',
            'password': {'second': 115},
            'first_name': 'test',
            'last_name': 'testsds',
            'check': True
        }

        response = client.post('/api/create_account/', data=json.dumps(data), content_type='application/json')

        self.assertEqual(response.status_code, 400, "fail")
        self.assertEqual(response.data, {'error': 'Empty piece of passwords'}, "fail")

        data = {
            'email': 'test1@mail',
            'password': {'first': 'dfdf', 'second': 115},
            'first_name': 'test',
            'last_name': 'testsds',
            'check': True
        }

        response = client.post('/api/create_account/', data=json.dumps(data), content_type='application/json')

        self.assertEqual(response.status_code, 400, "fail")
        self.assertEqual(response.data, {'error': 'Incorrect email'}, "fail")

        data = {
            'email': 'test1@mail.ru',
            'password': {'first': 'dfdf', 'second': 115},
            'first_name': 'test',
            'last_name': 'testsds',
            'check': True
        }

        response = client.post('/api/create_account/', data=json.dumps(data), content_type='application/json')

        self.assertEqual(response.status_code, 400, "fail")
        self.assertEqual(response.data, {'error': 'Passwords are incorrect'}, "fail")

        data = {
            'email': 'test1@mail.ru',
            'password': {'first': 'dfdf', 'second': 'dfdf'},
            'first_name': 'test',
            'last_name': 'testsds',
            'check': True
        }

        response = client.post('/api/create_account/', data=json.dumps(data), content_type='application/json')

        self.assertEqual(response.status_code, 400, "fail")

        data = {
            'email': 'test1@mail.ru',
            'password': {'first': '123qwe123', 'second': '123qwe123'},
            'first_name': 'test',
            'last_name': 'testsds',
            'check': True
        }

        u = User.objects.filter(email='test1@mail.ru').exists()
        self.assertEqual(u, False, "fail")

        response = client.post('/api/create_account/', data=json.dumps(data), content_type='application/json')

        u = User.objects.get(email='test1@mail.ru')
        t = Token.objects.get(user=u)

        self.assertEqual(response.status_code, 200, "fail")
        self.assertEqual(response.data, {'token': t.key}, "fail")

        self.assertEqual(u.first_name, 'test', "fail")
        self.assertEqual(u.last_name, 'testsds', "fail")

        data = {
            'email': 'test2@mail.ru',
            'password': {'first': '123qwe123', 'second': '123qwe123'},
            'first_name': 'test4',
            'last_name': 'testsds4',
            'check': True,
            'middle_name': 'ffd4',
            'code_id': 242,
            'number_phone': 15456
        }

        c = Country(
            name_en = 'VVf',
            show = True
        )
        c.save()

        cn = CountryNumberphone(
            code = 123,
            country = c
        )
        cn.save()

        response = client.post('/api/create_account/', data=json.dumps(data), content_type='application/json')
        self.assertEqual(response.status_code, 200, response.content)

        u = User.objects.get(email='test2@mail.ru')
        t = Token.objects.get(user=u)

        self.assertEqual(response.data, {'token': t.key}, "fail")

        self.assertEqual(u.first_name, 'test4', "fail")
        self.assertEqual(u.last_name, 'testsds4', "fail")
        self.assertEqual(u.profile.middle_name, 'ffd4', "fail")
        self.assertEqual(u.profile.code_num_phone.id, 242, "fail")
        self.assertEqual(u.profile.number_phone, 15456, "fail")

        data = {
            'email': 'testsdsd2@mail.ru',
            'password': {'first': '123qwe123', 'second': '123qwe123'},
            'first_name': 'test4',
            'last_name': 'testsds4',
            'check': True,
            'middle_name': 'ffd4',
            'code_id': 9999999,
            'number_phone': 15456
        }

        response = client.post('/api/create_account/', data=json.dumps(data), content_type='application/json')

        self.assertEqual(response.status_code, 400, "fail")
        self.assertEqual(response.data, {'error': 'Incorrect code_id'}, "fail")

        data = {
            'email': 'test22@mail.ru',
            'password': {'first': '123qwe123', 'second': '123qwe123'},
            'first_name': 'test4',
            'last_name': 'testsds4',
            'check': True,
            'code_id': 242,
            'number_phone': 15456
        }

        response = client.post('/api/create_account/', data=json.dumps(data), content_type='application/json')

        u = User.objects.get(email='test22@mail.ru')
        t = Token.objects.get(user=u)

        self.assertEqual(response.status_code, 200, "fail")
        self.assertEqual(response.data, {'token': t.key}, "fail")

        self.assertEqual(u.first_name, 'test4', "fail")
        self.assertEqual(u.last_name, 'testsds4', "fail")
        self.assertEqual(u.profile.middle_name, None, "fail")
        self.assertEqual(u.profile.code_num_phone.id, 242, "fail")
        self.assertEqual(u.profile.number_phone, 15456, "fail")

        data = {
            'email': 'test222@mail.ru',
            'password': {'first': '123qwe123', 'second': '123qwe123'},
            'first_name': 'test4',
            'last_name': 'testsds4',
            'check': True,
            'code_id': 242,
        }

        response = client.post('/api/create_account/', data=json.dumps(data), content_type='application/json')

        u = User.objects.get(email='test222@mail.ru')
        t = Token.objects.get(user=u)

        self.assertEqual(response.status_code, 200, "fail")
        self.assertEqual(response.data, {'token': t.key}, "fail")

        self.assertEqual(u.first_name, 'test4', "fail")
        self.assertEqual(u.last_name, 'testsds4', "fail")
        self.assertEqual(u.profile.middle_name, None, "fail")
        self.assertEqual(u.profile.code_num_phone, None, "fail")
        self.assertEqual(u.profile.number_phone, None, "fail")

        data = {
            'email': 'test2222@mail.ru',
            'password': {'first': '123qwe123', 'second': '123qwe123'},
            'first_name': 'test4',
            'last_name': 'testsds4',
            'check': True,
            'number_phone': 15456
        }

        response = client.post('/api/create_account/', data=json.dumps(data), content_type='application/json')

        u = User.objects.get(email='test2222@mail.ru')
        t = Token.objects.get(user=u)

        self.assertEqual(response.status_code, 200, "fail")
        self.assertEqual(response.data, {'token': t.key}, "fail")

        self.assertEqual(u.first_name, 'test4', "fail")
        self.assertEqual(u.last_name, 'testsds4', "fail")
        self.assertEqual(u.profile.middle_name, None, "fail")
        self.assertEqual(u.profile.code_num_phone, None, "fail")
        self.assertEqual(u.profile.number_phone, None, "fail")