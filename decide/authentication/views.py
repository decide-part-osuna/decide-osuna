from rest_framework.response import Response
from rest_framework.status import (
        HTTP_201_CREATED,
        HTTP_400_BAD_REQUEST,
        HTTP_401_UNAUTHORIZED,
        HTTP_200_OK
)
from rest_framework.views import APIView
from rest_framework.authtoken.models import Token
from django.contrib.auth.models import User
from django.db import IntegrityError
from django.shortcuts import get_object_or_404
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import login, authenticate
from django.shortcuts import render
from authentication.models import Metodos
from django.contrib.auth.hashers import check_password

from .serializers import UserSerializer


class GetUserView(APIView):
    def post(self, request):
        key = request.data.get('token', '')
        tk = get_object_or_404(Token, key=key)
        return Response(UserSerializer(tk.user, many=False).data)


class LogoutView(APIView):
    def post(self, request):
        key = request.data.get('token', '')
        try:
            tk = Token.objects.get(key=key)
            tk.delete()
        except ObjectDoesNotExist:
            pass

        return render(request, 'welcome.html')


class RegisterView(APIView):
    def get(self, request):
        return render(request, 'authentication/RegisterView.html')

    def post(self, request):
        postData = request.POST
        errorList = []

        username = postData.get('userName')
        pwd = postData.get('password')
        pwd2 = postData.get('password2')
        if not username or not pwd or not pwd2 or pwd != pwd2:
            if not username:
                errorMessage = "You have to introduce an username"
                errorList.append(errorMessage)
            if not pwd:
                errorMessage = "You have to introduce a password"
                errorList.append(errorMessage)
            if not pwd2:
                errorMessage = "You have to repeat your password"
                errorList.append(errorMessage)
            if pwd != pwd2:
                errorMessage = "The passwords introduced have to be the same"
                errorList.append(errorMessage)
            return render(request, 'authentication/RegisterView.html', {'errores':errorList}, status=HTTP_400_BAD_REQUEST) 
        
        name = '' 
        surname = ''
        email = ''
        if postData.get('name'):
            name = postData.get('name')
        if postData.get('surname'):
            surname = postData.get('surname')
        if postData.get('email'):
            email = postData.get('email')
            if "@gmail.com" not in email and "@yahoo.es" not in email and "@hotmail.com" not in email and "@hotmail.es" not in email and "@outlook.com" not in email and "@alum.us.es" not in email and "@us.es" not in email:
                errorMessage = "You have to enter a valid email. This system allows the following endinds: @gmail.com, @yahoo.es, @hotmail.com, @hotmail.es, @outlook.com, @alum.us.es, @us.es"
                errorList.append(errorMessage)
                return render(request, 'authentication/RegisterView.html', {'errores':errorList}, status=HTTP_400_BAD_REQUEST)
        
        try:
            user = User(username=username)
            user.set_password(pwd)
            if name != '':
                user.first_name = name
            if surname != '':
                user.last_name = surname
            if email != '':
                user.email = email
            user.save()
            Token.objects.create(user=user)
        except IntegrityError:
            errorMessage = "You're trying to create a user which is already registered, try changing the username and/or email introduced"
            errorList.append(errorMessage)
            return render(request, 'authentication/RegisterView.html', {'errores':errorList}, status=HTTP_400_BAD_REQUEST)
        return render(request, 'welcome.html', {'message': "Se ha registrado correctamente al usuario con nombre: " + username})

class LoginView(APIView):
    def get(self, request):
        form = AuthenticationForm()
        return render(request, 'authentication/LoginView.html',{'form':form})

    def post(self, request):
        postData = request.POST
        errorList = []
        username = postData.get('username', '')
        password = postData.get('password', '')
        if not username or not password:
            if not username:
                errorMessage = "You have to introduce an username"
                errorList.append(errorMessage)
            if not password:
                errorMessage = "You have to introduce a password"
                errorList.append(errorMessage)
            return render(request, 'authentication/LoginView.html', {'errorList':errorList})
        try:
            userTest = Metodos.getUsuarioPorNombre(username)
            correctPassword = check_password(password, userTest.password)
            if correctPassword!=True or userTest is None:
                if correctPassword!=True:
                    errorMessage = "Wrong password"
                    errorList.append(errorMessage)
                return render(request, 'authentication/LoginView.html', {'errorList':errorList})
            user = authenticate(username=username, password=password, request=request)
            if user is not None:
                login(request, user)
                return render(request, 'welcome.html', {'message': "Succesful login: " + username})
            else:
                return render (request, 'authentication/LoginView.html')
        except:
            errorMessage = "Non existant user"
            errorList.append(errorMessage)
            return render(request, 'authentication/LoginView.html', {'errorList':errorList})
