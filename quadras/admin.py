from django.contrib import admin
from .models import Quadra

@admin.register(Quadra)
class QuadraAdmin(admin.ModelAdmin):
    # Colunas que o dono vai ver na lista
    list_display = ('nome', 'ativa')
    # Filtro lateral para ver apenas as ativas ou inativas
    list_filter = ('ativa',)
    # Barra de pesquisa para facilitar quando houver muitas quadras
    search_fields = ('nome',)