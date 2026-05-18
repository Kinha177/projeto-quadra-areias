from django.urls import path
from . import views

urlpatterns = [
    path('', views.lista_quadras, name='lista_quadras'),
]