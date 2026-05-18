from django.contrib import admin
from .models import Aluno, Pagamento # <-- Trazemos o Pagamento para a luz do dia

@admin.register(Aluno)
class AlunoAdmin(admin.ModelAdmin):
    # Adicionamos o valor_mensalidade e dia_vencimento aqui na lista visual!
    list_display = ('nome', 'quadra', 'get_dia_da_semana_display', 'horario', 'valor_mensalidade', 'dia_vencimento', 'ativo')
    list_filter = ('ativo', 'dia_da_semana', 'quadra')
    search_fields = ('nome', 'whatsapp')

# --- NOVA SEÇÃO DE PAGAMENTOS ---
@admin.register(Pagamento)
class PagamentoAdmin(admin.ModelAdmin):
    # O que você vai bater o olho e ver na lista
    list_display = ('aluno', 'mes_referencia', 'valor', 'pago', 'data_criacao')
    
    # Filtros super úteis: "Quero ver só quem NÃO pagou" ou "Só os pagamentos de Março"
    list_filter = ('pago', 'mes_referencia')
    
    # Barra de pesquisa para buscar pelo nome do aluno devedor (o duplo underline é a mágica do Django para buscar em outra tabela)
    search_fields = ('aluno__nome',)