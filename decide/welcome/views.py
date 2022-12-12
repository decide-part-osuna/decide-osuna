from django.shortcuts import render
from rest_framework.views import APIView

class WelcomeView(APIView):
    def get(self, request):
        return render(request, 'welcome.html')