from django.urls import include, path
from .views import WelcomeView
from authentication.views import LogoutView

urlpatterns = [
    path('welcome/', WelcomeView.as_view(), name='welcome')
]