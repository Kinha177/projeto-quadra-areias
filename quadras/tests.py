from django.test import TestCase
from .models import Quadra # Tentando importar o órgão que ainda não existe

class QuadraModelTest(TestCase):
    def test_pode_criar_quadra_com_sucesso(self):
        """Testa se conseguimos cadastrar uma quadra física no sistema"""
        
        quadra = Quadra.objects.create(
            nome="Quadra 2 (Futevôlei)",
            descricao="Quadra com areia fina, ideal para futevôlei.",
            ativa=True # Se for False, a quadra não aparece para os clientes
        )
        
        self.assertEqual(Quadra.objects.count(), 1)
        self.assertEqual(quadra.nome, "Quadra 2 (Futevôlei)")
        self.assertTrue(quadra.ativa)