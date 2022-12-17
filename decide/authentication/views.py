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
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import login, authenticate
from django.shortcuts import render
from authentication.models import Metodos
from django.shortcuts import render
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

        return Response({})


class RegisterView(APIView):
    def get(self, request):
        form = UserCreationForm()
        return render(request, 'authentication/RegisterView.html', {'form':form})

    def post(self, request):
        key = request.data.get('token', '')
        tk = get_object_or_404(Token, key=key)
        if not tk.user.is_superuser:
            return Response({}, status=HTTP_401_UNAUTHORIZED)

        username = request.data.get('username', '')
        pwd = request.data.get('password', '')
        if not username or not pwd:
            return Response({}, status=HTTP_400_BAD_REQUEST)

        try:
            user = User(username=username)
            user.set_password(pwd)
            user.save()
            token, _ = Token.objects.get_or_create(user=user)
        except IntegrityError:
            return Response({}, status=HTTP_400_BAD_REQUEST)
        return Response({'user_pk': user.pk, 'token': token.key}, HTTP_201_CREATED)

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
