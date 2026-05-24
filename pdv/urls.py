"""
pdv/urls.py
===========
Rotas do módulo PDV.

Inclua no urls.py principal:
    from django.urls import path, include

    urlpatterns = [
        ...
        path('pdv/', include('pdv.urls')),
    ]
"""

from django.urls import path
from . import views

app_name = 'pdv'

urlpatterns = [
    # Cockpit principal
    path('',                   views.pdv_dashboard,    name='dashboard'),

    # Operações de escrita (todas via POST + JSON)
    path('abrir/',             views.abrir_comanda,    name='abrir_comanda'),
    path('adicionar-item/',    views.adicionar_item,   name='adicionar_item'),
    path('remover-item/',      views.remover_item,     name='remover_item'),
    path('fechar/<int:pk>/',   views.fechar_comanda,   name='fechar_comanda'),
    path('cancelar/<int:pk>/', views.cancelar_comanda, name='cancelar_comanda'),
]
