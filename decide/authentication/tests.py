from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework.test import APITestCase

from django.contrib.auth.models import User
from rest_framework.authtoken.models import Token

from base import mods

from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys

from base.tests import BaseTestCase

class AuthTestCase(APITestCase):

    def setUp(self):
        self.client = APIClient()
        mods.mock_query(self.client)
        u = User(username='voter1')
        u.set_password('123')
        u.save()

        u2 = User(username='admin')
        u2.set_password('admin')
        u2.is_superuser = True
        u2.save()

    def tearDown(self):
        self.client = None

    def test_login(self):
        data = {'username': 'voter1', 'password': '123'}
        response = self.client.post('/authentication/login/', data, format='json')
        self.assertEqual(response.status_code, 200)

        token = response.json()
        self.assertTrue(token.get('token'))

    def test_login_fail(self):
        data = {'username': 'voter1', 'password': '321'}
        response = self.client.post('/authentication/login/', data, format='json')
        self.assertEqual(response.status_code, 400)

    def test_getuser(self):
        data = {'username': 'voter1', 'password': '123'}
        response = self.client.post('/authentication/login/', data, format='json')
        self.assertEqual(response.status_code, 200)
        token = response.json()

        response = self.client.post('/authentication/getuser/', token, format='json')
        self.assertEqual(response.status_code, 200)

        user = response.json()
        self.assertEqual(user['id'], 1)
        self.assertEqual(user['username'], 'voter1')

    def test_getuser_invented_token(self):
        token = {'token': 'invented'}
        response = self.client.post('/authentication/getuser/', token, format='json')
        self.assertEqual(response.status_code, 404)

    def test_getuser_invalid_token(self):
        data = {'username': 'voter1', 'password': '123'}
        response = self.client.post('/authentication/login/', data, format='json')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Token.objects.filter(user__username='voter1').count(), 1)

        token = response.json()
        self.assertTrue(token.get('token'))

        response = self.client.post('/authentication/logout/', token, format='json')
        self.assertEqual(response.status_code, 200)

        response = self.client.post('/authentication/getuser/', token, format='json')
        self.assertEqual(response.status_code, 404)

    def test_logout(self):
        data = {'username': 'voter1', 'password': '123'}
        response = self.client.post('/authentication/login/', data, format='json')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Token.objects.filter(user__username='voter1').count(), 1)

        token = response.json()
        self.assertTrue(token.get('token'))

        response = self.client.post('/authentication/logout/', token, format='json')
        self.assertEqual(response.status_code, 200)

        self.assertEqual(Token.objects.filter(user__username='voter1').count(), 0)

    #def test_register_bad_permissions(self):
    #    data = {'username': 'voter1', 'password': '123'}
    #    response = self.client.post('/authentication/login/', data, format='json')
    #    self.assertEqual(response.status_code, 200)
    #    token = response.json()

    #    token.update({'username': 'user1'})
    #    response = self.client.post('/authentication/register/', token, format='json')
    #    self.assertEqual(response.status_code, 401)

    #def test_register_bad_request(self):
    #    data = {'username': 'admin', 'password': 'admin'}
    #    response = self.client.post('/authentication/login/', data, format='json')
    #    self.assertEqual(response.status_code, 200)
    #    token = response.json()

    #    token.update({'username': 'user1'})
    #    response = self.client.post('/authentication/register/', token, format='json')
    #   self.assertEqual(response.status_code, 400)

    #def test_register_user_already_exist(self):
    #    data = {'username': 'admin', 'password': 'admin'}
    #    response = self.client.post('/authentication/login/', data, format='json')
    #    self.assertEqual(response.status_code, 200)
    #    token = response.json()

    #    token.update(data)
    #    response = self.client.post('/authentication/register/', token, format='json')
    #    self.assertEqual(response.status_code, 400)

    def test_register(self):
        data = {'userName': 'UserTest1', 'name': 'Usertest', 'surname': 'Register Test', 'email':'exampleTest@gmail.com', 'password':'test1', 'password2': 'test1'}
        response = self.client.post('/authentication/register/', data, format='json')
        self.assertEqual(response.status_code, 200)

    def test_register_only_username_and_password(self):
        data = {'userName': 'UserTest2', 'password':'test2', 'password2': 'test2'}
        response = self.client.post('/authentication/register/', data, format='json')
        self.assertEqual(response.status_code, 200)

    
class RegisterTestCase(StaticLiveServerTestCase):
    def setUp(self):
        self.base = BaseTestCase()
        self.base.setUp()

        options = webdriver.ChromeOptions()
        options.headless = True
        self.driver = webdriver.Chrome(options = options)

        super().setUp()

    def tearDown(self):
        super().tearDown()
        self.driver.quit()

        self.base.tearDown()

    #Positive registration tests
    def test_register(self):
        self.driver.get(f'{self.live_server_url}/authentication/register/')
        self.driver.find_element(By.NAME,'userName').send_keys('UserTest1')
        self.driver.find_element(By.NAME,'name').send_keys('Usertest')
        self.driver.find_element(By.NAME,'surname').send_keys('Register Test')
        self.driver.find_element(By.NAME,'email').send_keys('exampleTest@gmail.com')
        self.driver.find_element(By.NAME,'password').send_keys('test1')
        self.driver.find_element(By.NAME,'password2').send_keys('test1', Keys.ENTER)
        self.assertTrue(self.driver.title == 'Welcome')
    
    def test_register_only_username_and_password(self):
        self.driver.get(f'{self.live_server_url}/authentication/register/')
        self.driver.find_element(By.NAME,'userName').send_keys('UserTest2')
        self.driver.find_element(By.NAME,'password').send_keys('test2')
        self.driver.find_element(By.NAME,'password2').send_keys('test2', Keys.ENTER)
        self.assertTrue(self.driver.title == 'Welcome')

    #Negative registration tests
    def negative_test_register_no_username(self):
        self.driver.get(f'{self.live_server_url}/authentication/register/')        
        self.driver.find_element(By.NAME,'name').send_keys('Usertest Negative')
        self.driver.find_element(By.NAME,'surname').send_keys('RegisterNegative Test')
        self.driver.find_element(By.NAME,'email').send_keys('exampleNegativeTest@gmail.com')
        self.driver.find_element(By.NAME,'password').send_keys('testN1')
        self.driver.find_element(By.NAME,'password2').send_keys('testN1', Keys.ENTER)
        self.assertTrue(self.driver.title == 'Register')

    def negative_test_register_no_password(self):
        self.driver.get(f'{self.live_server_url}/authentication/register/')
        self.driver.find_element(By.NAME,'userName').send_keys('UserTestNegative2')
        self.driver.find_element(By.NAME,'name').send_keys('Usertest Negative2')
        self.driver.find_element(By.NAME,'surname').send_keys('RegisterNegative Test2')
        self.driver.find_element(By.NAME,'email').send_keys('exampleNegativeTest2@gmail.com')
        self.driver.find_element(By.NAME,'password2').send_keys('testN2', Keys.ENTER)
        self.assertTrue(self.driver.title == 'Register')

    def negative_test_register_invalid_email(self):
        self.driver.get(f'{self.live_server_url}/authentication/register/')
        self.driver.find_element(By.NAME,'userName').send_keys('UserTestNegative3')
        self.driver.find_element(By.NAME,'name').send_keys('Usertest Negative3')
        self.driver.find_element(By.NAME,'surname').send_keys('RegisterNegative Test3')
        self.driver.find_element(By.NAME,'email').send_keys('exampleNegativeTest3@invalid.com')
        self.driver.find_element(By.NAME,'password').send_keys('testN3')
        self.driver.find_element(By.NAME,'password2').send_keys('testN3', Keys.ENTER)
        self.assertTrue(self.driver.title == 'Register')

    def negative_test_register_passwords_dont_match(self):
        self.driver.get(f'{self.live_server_url}/authentication/register/')
        self.driver.find_element(By.NAME,'userName').send_keys('UserTestNegative4')
        self.driver.find_element(By.NAME,'name').send_keys('Usertest Negative4')
        self.driver.find_element(By.NAME,'surname').send_keys('RegisterNegative Test4')
        self.driver.find_element(By.NAME,'email').send_keys('exampleNegativeTest4@gmail.com')
        self.driver.find_element(By.NAME,'password').send_keys('testN4')
        self.driver.find_element(By.NAME,'password2').send_keys('testN', Keys.ENTER)
        self.assertTrue(self.driver.title == 'Register')