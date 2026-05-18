from django.db import models
from quadras.models import Quadra # <-- Importamos a Quadra real aqui!

class Reserva(models.Model):
    # A MÁGICA DA REFATORAÇÃO: Deixou de ser texto livre e virou Chave Estrangeira
    # O "on_delete=models.CASCADE" significa que se o dono apagar a quadra, as reservas dela somem.
    quadra = models.ForeignKey(Quadra, on_delete=models.CASCADE)
    data = models.DateField()
    horario_inicio = models.TimeField()
    nome_cliente = models.CharField(max_length=100)

    class Meta:
        unique_together = ('quadra', 'data', 'horario_inicio')

    def __str__(self):
        # Agora o sistema é inteligente e sabe buscar o ".nome" dentro da quadra
        return f"{self.nome_cliente} - {self.quadra.nome} - {self.data} às {self.horario_inicio}"