from django.test import TestCase
from django.urls import reverse
from datetime import time, date
from quadras.models import Quadra
from .models import Aluno, Pagamento

class AlunoModelTest(TestCase):
    def setUp(self):
        # Criamos a quadra de base para o teste rodar
        self.quadra = Quadra.objects.create(nome="Arena Principal", ativa=True)

    def test_pode_criar_aluno_mensalista(self):
        """Testa se conseguimos cadastrar um mensalista com dia e hora fixos"""
        aluno = Aluno.objects.create(
            nome="Carlos (Turma de Terça)",
            whatsapp="5538999999999",
            quadra=self.quadra,
            dia_da_semana=1, # No Python: 0=Segunda, 1=Terça, 2=Quarta...
            horario=time(hour=19, minute=0)
        )
        
        self.assertEqual(Aluno.objects.count(), 1)
        self.assertEqual(aluno.nome, "Carlos (Turma de Terça)")

class PagamentoModelTest(TestCase):
    def setUp(self):
        # Preparar o terreno: precisamos de uma quadra e de um aluno para poder cobrar
        self.quadra = Quadra.objects.create(nome="Arena Financeiro", ativa=True)
        self.aluno = Aluno.objects.create(
            nome="Carlos (Turma de Terça)",
            whatsapp="5538999999999",
            quadra=self.quadra,
            dia_da_semana=1,
            horario=time(hour=19, minute=0)
        )

    def test_pode_registar_pagamento_do_mensalista(self):
        """Testa se conseguimos registar que o Carlos pagou o mês de Março"""
        
        pagamento = Pagamento.objects.create(
            aluno=self.aluno, # O "fio invisível" (Chave Estrangeira)
            mes_referencia=date(2026, 3, 1), # Usamos o dia 1 para representar o mês de "Março/2026"
            valor=150.00,
            pago=True # Se for False, significa que ele está a dever
        )
        
        self.assertEqual(Pagamento.objects.count(), 1)
        self.assertTrue(pagamento.pago)
        self.assertEqual(pagamento.aluno.nome, "Carlos (Turma de Terça)")

    class FinanceiroViewTest(TestCase):
        def setUp(self):
            # Preparando o terreno com um devedor
            self.quadra = Quadra.objects.create(nome="Arena Financeiro", ativa=True)
            self.aluno = Aluno.objects.create(
                nome="Devedor da Silva",
                whatsapp="5538999999999",
                quadra=self.quadra,
                dia_da_semana=1,
                horario=time(hour=19, minute=0)
            )
            self.pagamento = Pagamento.objects.create(
                aluno=self.aluno,
                mes_referencia=date(2026, 3, 1),
                valor=150.00,
                pago=False # Ele está devendo!
            )

        def test_dashboard_financeiro_exibe_devedores(self):
            """Testa se a página financeira carrega e mostra quem não pagou"""
            
            # Simulamos você acessando o link do painel financeiro (que ainda não existe)
            resposta = self.client.get(reverse('painel_financeiro'))
            
            self.assertEqual(resposta.status_code, 200)
            
            html = resposta.content.decode('utf-8')
            
            self.assertIn("Devedor da Silva", html)
            self.assertIn("Pendente", html)