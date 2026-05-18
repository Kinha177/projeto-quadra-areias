from django.contrib import admin
from .models import Reserva

# Aqui estamos dizendo ao Django para mostrar a Reserva no painel
@admin.register(Reserva)
class ReservaAdmin(admin.ModelAdmin):
    # Quais colunas o dono da quadra vai ver na lista
    list_display = ('nome_cliente', 'quadra', 'data', 'horario_inicio')
    # Adicionando um filtro lateral prático
    list_filter = ('data', 'quadra')