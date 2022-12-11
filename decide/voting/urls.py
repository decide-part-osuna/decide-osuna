from django.urls import path
from . import views


urlpatterns = [
    path('votings', views.VotingList.showVoting),
    path('votingsByName', views.sortByName),
    path('votingsByDesc', views.sortByDesc),
    path('votingsByStartDate', views.sortByStartDate),
    path('votingsByEndDate', views.sortByEndDate),
    path('', views.VotingView.as_view(), name='voting'),
    path('<int:voting_id>/', views.VotingUpdate.as_view(), name='voting'),
]
