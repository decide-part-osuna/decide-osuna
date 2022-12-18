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