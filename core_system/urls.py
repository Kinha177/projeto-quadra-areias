from django.contrib import admin
from django.urls import path
from reservas.views import lista_quadras, homepage
from alunos.views import painel_financeiro
# Vamos criar essa view de homepage rapidinho ali embaixo
from django.http import HttpResponse 

urlpatterns = [
    path('admin/', admin.site.urls),
    
    # 1. Homepage real e definitiva!
    path('', homepage, name='homepage'), 
    
    # 2. Grade funcional de agendamento
    path('agendamento/', lista_quadras, name='lista_quadras'), 
    
    path('financeiro/', painel_financeiro, name='painel_financeiro'),
]