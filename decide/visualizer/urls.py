from django.urls import path, re_path
from .views import VisualizerView
from .views import listaCorreos


urlpatterns = [
    path('<int:voting_id>/', VisualizerView.as_view(), name="Visualizer"),
    path('<int:voting_id>/mail', listaCorreos, name="listaCorreos")
]
