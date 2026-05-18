from django.db import models
from quadras.models import Quadra

class Aluno(models.Model):
    DIAS_DA_SEMANA = [
        (0, 'Segunda-feira'),
        (1, 'Terça-feira'),
        (2, 'Quarta-feira'),
        (3, 'Quinta-feira'),
        (4, 'Sexta-feira'),
        (5, 'Sábado'),
        (6, 'Domingo'),
    ]

    nome = models.CharField(max_length=100)
    whatsapp = models.CharField(max_length=20)
    quadra = models.ForeignKey(Quadra, on_delete=models.CASCADE)
    dia_da_semana = models.IntegerField(choices=DIAS_DA_SEMANA)
    horario = models.TimeField()
    ativo = models.BooleanField(default=True)
    
    # --- NOVOS CAMPOS DA AUTOMAÇÃO FINANCEIRA ---
    valor_mensalidade = models.DecimalField(max_digits=10, decimal_places=2, default=150.00)
    dia_vencimento = models.IntegerField(default=10) # Ex: dia 5, 10, 15...

    def __str__(self):
        return f"{self.nome} - {self.get_dia_da_semana_display()} às {self.horario.strftime('%H:%M')}"

# --- NOVO MODELO FINANCEIRO ---
class Pagamento(models.Model):
    # O "fio invisível" que liga o pagamento ao aluno específico
    aluno = models.ForeignKey(Aluno, on_delete=models.CASCADE)
    
    # Usamos o dia 1 de cada mês para representar o mês de referência (ex: 01/03/2026 = Março)
    mes_referencia = models.DateField() 
    
    # max_digits=10 e decimal_places=2 garante precisão em centavos (ex: 150.00)
    valor = models.DecimalField(max_digits=10, decimal_places=2)
    
    # O status crucial: começa como "devendo" (False), e o dono marca como True quando recebe o Pix
    pago = models.BooleanField(default=False)
    
    # Registra a data e hora exatas em que a cobrança foi criada no sistema
    data_criacao = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        status = "Pago" if self.pago else "Pendente"
        return f"{self.aluno.nome} - Mês {self.mes_referencia.strftime('%m/%Y')} - R$ {self.valor} ({status})"