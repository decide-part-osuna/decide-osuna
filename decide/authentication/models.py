from django.db import models
from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist

# Create your models here.

class Metodos():

    @staticmethod
    def getUsuarioPorNombre(username):
        return User.objects.get(username=username)