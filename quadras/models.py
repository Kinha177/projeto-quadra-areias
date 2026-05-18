from django.db import models

class Quadra(models.Model):
    # O nome da quadra (ex: "Arena Principal", "Quadra 2 (Futevôlei)")
    nome = models.CharField(max_length=100)
    
    # Uma descrição opcional para ajudar o cliente a escolher
    descricao = models.TextField(blank=True, null=True)
    
    # Esse campo é crucial para a nossa lógica de escalabilidade!
    # Se o dono fechar uma quadra para manutenção, ele desmarca isso no painel
    # e ela some do site automaticamente, sem precisarmos mexer no código.
    ativa = models.BooleanField(default=True)

    def __str__(self):
        # Como a quadra vai aparecer escrita no painel do administrador
        status = "Ativa" if self.ativa else "Inativa"
        return f"{self.nome} ({status})"