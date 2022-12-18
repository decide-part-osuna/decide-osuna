import random
from django.contrib.auth.models import User
from django.test import TestCase
from rest_framework.test import APIClient


from .models import Census
from voting.models import Voting, Question, QuestionOption
from base import mods
from base.tests import BaseTestCase
from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from django.conf import settings
from base.models import Auth
from django.forms.models import model_to_dict

from django.urls import reverse
from .models import Census

from django.contrib.auth.models import User


from selenium import webdriver
from selenium.webdriver.common.by import By
from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from rest_framework.test import APITestCase
import os.path
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from django.contrib.staticfiles.testing import StaticLiveServerTestCase

class CensusTestCase(BaseTestCase):
      

    def setUp(self):
        super().setUp()
        q = Question(desc='test question')
        q.save()
        for i in range(5):
            opt = QuestionOption(question=q, option='option {}'.format(i+1))
            opt.save()
        questions=[]
        v = Voting(name='test voting', id=20)
        v.question.set(questions)
        v.save()


        a, _ = Auth.objects.get_or_create(url=settings.BASEURL,
                                          defaults={'me': True, 'name': 'test auth'})
        a.save()
        v.auths.add(a)
         
        voters=[]

        u = User(username='voter1', id=20)
        u.set_password('123')
        u.save()

        u2 = User(username='voter2', id=21)
        u2.set_password('123')
        u2.save()

        voters.append(u)
       
        self.census = Census(name='Huelva', voting_id=v, id=20)
        self.census.voter_id.set(voters)
        self.census.save()

    def tearDown(self):
        super().tearDown()
        self.census = None

    def test_check_vote_permissions(self):
        response = self.client.get('/census/{}/?voter_id={}'.format(20, 21), format='json')
        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.json(), 'Invalid voter')

        response = self.client.get('/census/{}/?voter_id={}'.format(20, 20), format='json')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), 'Valid voter')

    def test_list_voting(self):
        response = self.client.get('/census/?voting_id={}'.format(20), format='json')
        self.assertEqual(response.status_code, 401)

        self.login(user='noadmin')
        response = self.client.get('/census/?voting_id={}'.format(20), format='json')
        self.assertEqual(response.status_code, 403)

        self.login()
        response = self.client.get('/census/?voting_id={}'.format(20), format='json')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {'voters': [20]})

    def test_destroy_voter(self):
        data = {'voters': [20]}
        response = self.client.delete('/census/{}/'.format(20), data, format='json')
        self.assertEqual(response.status_code, 204)
        self.assertEqual(0, Census.objects.count())
        
        
class ImportExportTestCase(StaticLiveServerTestCase):

    def setUp(self):
        #Load base test functionality for decide
        self.base = BaseTestCase()
        self.base.setUp()

        options = webdriver.ChromeOptions()
        options.headless = True
        self.driver = webdriver.Chrome(options=options)

        super().setUp()            
            
    def tearDown(self):           
        super().tearDown()
        self.driver.quit()

        self.base.tearDown()
        
    def testExportCsv(self):                    
            self.driver.get(f'{self.live_server_url}/admin')
            self.driver.find_element(By.ID,'id_username').send_keys("admin")
            self.driver.find_element(By.ID,'id_password').send_keys("qwerty",Keys.ENTER)
            
            print(self.driver.current_url)
            self.driver.get(self.live_server_url+'/census/census/export/csv')
            self.assertTrue(self.live_server_url+"/census/census/export/csv" == self.driver.current_url)
            
    def testExportHtml(self):                    
            self.driver.get(f'{self.live_server_url}/admin')
            self.driver.find_element(By.ID,'id_username').send_keys("admin")
            self.driver.find_element(By.ID,'id_password').send_keys("qwerty",Keys.ENTER)
            
            print(self.driver.current_url)
            self.driver.get(self.live_server_url+'/census/census/export/html')
            self.assertTrue(self.live_server_url+"/census/census/export/html" == self.driver.current_url)
            

            
                 
    
        
        
    
    
    
