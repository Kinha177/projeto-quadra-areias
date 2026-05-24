from django.contrib import admin
from .models import Aluno, Pagamento

@admin.register(Aluno)
class AlunoAdmin(admin.ModelAdmin):
    list_display = ('nome', 'quadra', 'get_dia_da_semana_display', 'horario', 'valor_mensalidade', 'dia_vencimento', 'ativo')
    list_filter = ('ativo', 'dia_da_semana', 'quadra')
    search_fields = ('nome', 'whatsapp')

    fieldsets = (
        ('Dados do Aluno', {
            'fields': ('nome', 'whatsapp', 'ativo')
        }),
        ('Agenda Fixa', {
            'fields': ('quadra', 'dia_da_semana', 'horario'),
            'description': 'Atencao: alterar o horario aqui bloqueia automaticamente no agendamento.'
        }),
        ('Financeiro', {
            'fields': ('valor_mensalidade', 'dia_vencimento')
        }),
    )

@admin.register(Pagamento)
class PagamentoAdmin(admin.ModelAdmin):
    list_display = ('aluno', 'mes_referencia', 'valor', 'pago', 'data_criacao')
    list_filter = ('pago', 'mes_referencia', 'aluno__quadra')
    search_fields = ('aluno__nome',)
    ordering = ('pago', 'aluno__nome')

    # Permite editar com apenas 1 clique direto na lista
    list_editable = ('pago',)
    actions = ['marcar_como_pago', 'marcar_como_pendente']

    @admin.action(description='Marcar selecionados como PAGO')
    def marcar_como_pago(self, request, queryset):
        atualizados = queryset.update(pago=True)
        self.message_user(request, f'{atualizados} pagamento(s) marcado(s) como pago.')

    @admin.action(description='Marcar selecionados como PENDENTE')
    def marcar_como_pendente(self, request, queryset):
        atualizados = queryset.update(pago=False)
        self.message_user(request, f'{atualizados} pagamento(s) revertido(s) para pendente.')