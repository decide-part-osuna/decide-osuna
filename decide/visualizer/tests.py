from django.test import TestCase
import random
import itertools
from django.utils import timezone
from django.conf import settings
from django.contrib.auth.models import User
from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework.test import APITestCase

from base import mods
from base.tests import BaseTestCase
from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from census.models import Census
from mixnet.mixcrypt import ElGamal
from mixnet.mixcrypt import MixCrypt
from mixnet.models import Auth
from visualizer.models import Mail
from voting.models import Voting

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities

class MailTestCase(BaseTestCase):

    def setUp(self):
        super().setUp()

    def tearDown(self):
        super().tearDown()

    def testCreateMailList(self):
        count = len(Mail.objects.all())
        v = Voting(name='test voting', id=20)
        v.save()
        mail = Mail(mail='prueba@gmail.com', voting_id=20)
        mail.save()

        self.assertEquals(count+1, len(Mail.objects.all()))
    def testDeleteMailList(self):
        count = len(Mail.objects.all())
        v = Voting(name='test voting', id=20)
        v.save()
        mail = Mail(mail='prueba@gmail.com', voting_id=20)
        mail.save()

        self.assertEquals(count+1, len(Mail.objects.all()))
        mail.delete()
        self.assertEquals(count, len(Mail.objects.all()))


class MailSeleniumTestCase(StaticLiveServerTestCase):
    def setUp(self):
        #Load base test functionality for decide
        self.base = BaseTestCase()
        self.base.setUp()
        a, _ = Auth.objects.get_or_create(url=self.live_server_url,
                                          defaults={'me': True, 'name': 'test auth'})
        print(self.live_server_url)
        self.v = Voting(name='test voting', id=20)
        self.v.save()
        self.v.auths.add(a)
        self.v.save()

        options = webdriver.ChromeOptions()
        options.headless = True
        self.driver = webdriver.Chrome(options=options)

        super().setUp()            
            
    def tearDown(self):           
        super().tearDown()
        self.driver.quit()
        self.base.tearDown()
    
    def testAddMailList(self):
        count = len(Mail.objects.all())
        self.driver.get(f'{self.live_server_url}/admin/')
        self.driver.find_element(By.ID,'id_username').send_keys("admin")
        self.driver.find_element(By.ID,'id_password').send_keys("qwerty",Keys.ENTER) 
        print(self.driver.current_url)
        #In case of a correct loging, a element with id 'user-tools' is shown in the upper right part
        self.assertTrue(len(self.driver.find_elements(By.ID,'user-tools'))==1)
        self.driver.find_element(By.LINK_TEXT, "Votings").click()
        self.driver.find_element(By.NAME, "_selected_action").click()
        dropdown = self.driver.find_element(By.NAME, "action")
        dropdown.find_element(By.XPATH, "//option[. = 'Start']").click()
        element = self.driver.find_element(By.NAME, "action")
        actions = ActionChains(self.driver)
        actions.move_to_element(element).click_and_hold().perform()
        element = self.driver.find_element(By.NAME, "action")
        actions = ActionChains(self.driver)
        actions.move_to_element(element).perform()
        element = self.driver.find_element(By.NAME, "action")
        actions = ActionChains(self.driver)
        actions.move_to_element(element).release().perform()
        self.driver.find_element(By.NAME, "index").click()
        self.driver.get(f'{self.live_server_url}/visualizer/'+str(self.v.id))
       

        self.driver.find_element(By.NAME, "email").send_keys("prueba.egc.decide.osuna@yopmail.com")
        self.driver.find_element(By.CSS_SELECTOR, ".btn").click()
        self.assertEquals(count+1, len(Mail.objects.all()))
        
    
 