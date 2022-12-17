from rest_framework.response import Response
from rest_framework.status import (
        HTTP_201_CREATED,
        HTTP_400_BAD_REQUEST,
        HTTP_401_UNAUTHORIZED
)
from rest_framework.views import APIView
from rest_framework.authtoken.models import Token
from django.contrib.auth.models import User
from django.db import IntegrityError
from django.shortcuts import get_object_or_404
from django.core.exceptions import ObjectDoesNotExist
from django.shortcuts import render

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
            return render(request, 'authentication/RegisterView.html', {'errores':errorList})
        
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
                return render(request, 'authentication/RegisterView.html', {'errores':errorList})
        
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
            return Response({}, status=HTTP_400_BAD_REQUEST)
        return render(request, 'welcome.html', {'message': "Se ha registrado correctamente al usuario con nombre: " + username})