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

        u3 = User(username='UserTestLogin')
        u3.set_password('TestUsuario1')
        u3.save()

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
        #self.assertEqual(user['id'], 9)
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

    #Positive registration tests
    def test_register(self):
        response = self.client.post('/authentication/register/', {'userName': 'UserTest1', 'name': 'Usertest', 'surname':'Register Test', 'email':'exampleTest@gmail.com', 'password':'test1', 'password2':'test1'})
        self.assertEqual(response.status_code, 200)

    def test_register_only_username_and_password(self):
        response = self.client.post('/authentication/register/', {'userName': 'UserTest2', 'password':'test2', 'password2': 'test2'})
        self.assertEqual(response.status_code, 200)
    
    #Negative registration tests
    def negative_test_register_no_username(self):
        response = self.client.post('/authentication/register/', {'name': 'Usertest Negative', 'surname': 'RegisterNegative Test', 'email':'exampleNegativeTest@gmail.com', 'password':'test3', 'password2': 'test3'})
        self.assertEqual(response.status_code, 400)

    def negative_test_register_no_password(self):
        response = self.client.post('/authentication/register/', {'userName':'UserNegativeTest2','name': 'Usertest Negative2', 'surname': 'RegisterNegative Test2', 'email':'exampleNegativeTest2@gmail.com', 'password2': 'test4'})
        self.assertEqual(response.status_code, 400)

    def negative_test_register_invalid_email(self):
        response = self.client.post('/authentication/register/', {'userName':'UserNegativeTest3','name': 'Usertest Negative3', 'surname': 'RegisterNegative Test3', 'email':'exampleNegativeTest3@invalid.com', 'password':'test5', 'password2':'test5'})
        self.assertEqual(response.status_code, 400)

    def negative_test_register_passwords_dont_match(self):
        response = self.client.post('/authentication/register/', {'userName':'UserNegativeTest4','name': 'Usertest Negative4', 'surname': 'RegisterNegative Test4', 'email':'exampleNegativeTest4@invalid.com', 'password':'test6', 'password2':'test6'})
        self.assertEqual(response.status_code, 400)

    def negative_test_register_no_second_password(self):
        response = self.client.post('/authentication/register/', {'userName':'UserNegativeTest5','name': 'Usertest Negative5', 'surname': 'RegisterNegative Test5', 'email':'exampleNegativeTest5@gmail.com', 'password': 'test5'})
        self.assertEqual(response.status_code, 400)

    #Positive loginUser tests
    def test_loginUser(self):
        response = self.client.post('/authentication/loginUser/', {'username': 'UserTestLogin', 'password':'TestUsuario1'})
        self.assertEqual(response.status_code, 200)

    #Negative loginUser tests
    def negative_test_loginUser_no_username(self):
        response = self.client.post('/authentication/loginUser/', {'password':'TestUsuario1'})
        self.assertEqual(response.status_code, 400)

    def negative_test_loginUser_no_password(self):
        response = self.client.post('/authentication/loginUser/', {'username': 'UserTestLogin'})
        self.assertEqual(response.status_code, 400)

    def negative_test_loginUser_wrong_password(self):
        response = self.client.post('/authentication/loginUser/', {'username': 'UserTestLogin', 'password':'aaaaaaaaa'})
        self.assertEqual(response.status_code, 400)

    def negative_test_loginUser_wrong_user(self):
        response = self.client.post('/authentication/loginUser/', {'username': 'EsteUsuarioNoExiste9645', 'password':'TestUsuario1'})
        self.assertEqual(response.status_code, 400)
    
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

    def negative_test_register_no_second_password(self):
        self.driver.get(f'{self.live_server_url}/authentication/register/')
        self.driver.find_element(By.NAME,'userName').send_keys('UserTestNegative5')
        self.driver.find_element(By.NAME,'name').send_keys('Usertest Negative5')
        self.driver.find_element(By.NAME,'surname').send_keys('RegisterNegative Test5')
        self.driver.find_element(By.NAME,'email').send_keys('exampleNegativeTest5@gmail.com')
        self.driver.find_element(By.NAME,'password').send_keys('testN5', Keys.ENTER)
        self.assertTrue(self.driver.title == 'Register')

class LoginUserTestCase(StaticLiveServerTestCase):
    def setUp(self):
        self.base = BaseTestCase()
        self.base.setUp()

        options = webdriver.ChromeOptions()
        options.headless = True
        self.driver = webdriver.Chrome(options = options)

        u = User(username='UserTest1')
        u.set_password('TestUsuario1')
        u.save()
        
        super().setUp()

    def tearDown(self):
        super().tearDown()
        self.driver.quit()

        self.base.tearDown()

    #Positive cases

    def test_loginUser(self):
        
        self.driver.get(f'{self.live_server_url}/authentication/loginUser/')
        self.driver.find_element(By.NAME,'username').send_keys('UserTest1')
        self.driver.find_element(By.NAME,'password').send_keys('TestUsuario1', Keys.ENTER)
        self.assertTrue(self.driver.title == 'Welcome')
    
    #Negative cases

    def negative_test_login_no_username(self):
        self.driver.get(f'{self.live_server_url}/authentication/loginUser/')        
        self.driver.find_element(By.NAME,'password').send_keys('TestUsuario1', Keys.ENTER)
        self.assertTrue(self.driver.title == 'Login')

    def negative_test_login_no_password(self):
        self.driver.get(f'{self.live_server_url}/authentication/loginUser/')
        self.driver.find_element(By.NAME,'username').send_keys('UserTest1', Keys.ENTER)
        self.assertTrue(self.driver.title == 'Login')

    def negative_test_login_wrong_password(self):
        self.driver.get(f'{self.live_server_url}/authentication/loginUser/')
        self.driver.find_element(By.NAME,'username').send_keys('UserTest1')
        self.driver.find_element(By.NAME,'password').send_keys('aaaaaaaaaaaa', Keys.ENTER)
        self.assertTrue(self.driver.title == 'Login')

    def negative_test_login_unexistant_username(self):
        self.driver.get(f'{self.live_server_url}/authentication/loginUser/')
        self.driver.find_element(By.NAME,'username').send_keys('UsuarioQueNoExiste6519')
        self.driver.find_element(By.NAME,'password').send_keys('TestUsuario1', Keys.ENTER)
        self.assertTrue(self.driver.title == 'Login')

