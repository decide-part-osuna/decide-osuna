from django.db import models

# Create your models here.

class Metodos():

    @staticmethod
    def getUsuarioPorNombre(username):
        return Users.objects.filter(username=username)