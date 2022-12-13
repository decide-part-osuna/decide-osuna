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

# class LoginView(APIView):
#     def get(self, request):
#         form = AuthenticationForm()
#         return render(request, 'authentication/LoginView.html', {'form':form})

#     def post(self, request):
#         key = request.data.get('token', '')
#         tk = get_object_or_404(Token, key=key)
#         username = request.data.get('username', '')
#         pwd = request.data.get('password', '')
#         if not username or not pwd:
#             return Response({}, status=HTTP_400_BAD_REQUEST)
#         try:
#             user = authenticate(username=username, password=password)
#             if user is not None:
#                 login(request, user)
#                 messages.info(request, f"You are now logged in as {username}.")
#                 return redirect("")
#             else:
#                 messages.error(request,"Invalid username or password.")
#             token, _ = Token.objects.get_or_create(user=user)
#         except IntegrityError:
#             return Response({}, status=HTTP_400_BAD_REQUEST)
#         return Response({'user_pk': user.pk, 'token': token.key}, HTTP_200_OK)


class LoginView(APIView):
    def get(self, request):
        form = AuthenticationForm()
        return render(request, 'authentication/LoginView.html', {'form':form})

    def post(self, request):
        username = request.data.get('username')
        pwd = request.data.get('password')
        user = Metodos.getUsuarioPorNombre(username)
        if user:
            flag = pwd == user.password
            if flag:
                messages.info(request, f"You are now logged in as {username}.")
                return redirect("")
        else:
            messages.error(request,"Invalid username or password.")
        return render (request, 'loginUsuario.html')