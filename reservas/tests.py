from django.test import TestCase
from django.utils import timezone
from django.db import IntegrityError
from django.urls import reverse
from datetime import time
from .models import Reserva
from quadras.models import Quadra
from alunos.models import Aluno

# IMPORTANTE: Importando o "órgão" do nosso novo módulo!
from quadras.models import Quadra 

class ReservaModelTest(TestCase):
    def setUp(self):
        # O TDD exige que a gente prepare o terreno antes do teste.
        # Criamos uma quadra virtual apenas para este teste rodar.
        self.quadra_teste = Quadra.objects.create(nome="Quadra de Teste", ativa=True)

    def test_pode_criar_reserva_com_sucesso(self):
        """Testa se conseguimos criar uma reserva atrelada a uma Quadra real"""
        agora = timezone.now()
        
        reserva = Reserva.objects.create(
            quadra=self.quadra_teste, # <-- Aqui passamos o OBJETO, não mais um texto!
            data=agora.date(),
            horario_inicio=agora.time(),
            nome_cliente="João Silva"
        )
        
        self.assertEqual(Reserva.objects.count(), 1)
        # Vamos exigir que o sistema saiba ler o NOME da quadra através do relacionamento
        self.assertEqual(reserva.quadra.nome, "Quadra de Teste") 

    def test_nao_pode_criar_reserva_duplicada(self):
        """Testa o bloqueio de double booking com a nova Chave Estrangeira"""
        agora = timezone.now()

        Reserva.objects.create(
            quadra=self.quadra_teste,
            data=agora.date(),
            horario_inicio=agora.time(),
            nome_cliente="João (Primeiro)"
        )

        with self.assertRaises(IntegrityError):
            Reserva.objects.create(
                quadra=self.quadra_teste,
                data=agora.date(),
                horario_inicio=agora.time(),
                nome_cliente="Maria (Duplicada)"
            )

class ReservaViewTest(TestCase):
    def test_tela_recebe_lista_de_horarios(self):
        resposta = self.client.get(reverse('lista_quadras'))
        self.assertEqual(resposta.status_code, 200)
        # Atualizamos a busca para a nova variável 'dados_das_quadras'
        self.assertIn('dados_das_quadras', resposta.context)

    def test_tela_aceita_data_futura_na_url(self):
        """Testa se a página consegue carregar a agenda de um dia específico passado na URL"""
        # Simulamos o cliente acessando o site e pedindo o dia 25/12/2026
        resposta = self.client.get(reverse('lista_quadras'), {'data': '2026-12-25'})
        
        self.assertEqual(resposta.status_code, 200)
        # Verificamos se a View devolveu a data correta para o HTML exibir
        self.assertEqual(resposta.context['data_selecionada'], '25/12/2026')

    def test_horarios_passados_aparecem_como_esgotados(self):
        """Testa se datas no passado bloqueiam todos os horários"""
        # Simulamos o cliente acessando o dia 1 de Janeiro de 2020
        resposta = self.client.get(reverse('lista_quadras'), {'data': '2020-01-01'})
        
        # Lemos o HTML que a View gerou
        html = resposta.content.decode('utf-8')
        
        # Exigimos que a palavra 'Livre' NÃO EXISTA nessa página, 
        # pois o dia já passou completamente!
        self.assertNotIn('Livre', html)

    def test_mensalista_bloqueia_horario_automaticamente(self):
        """Testa se o horário fixo do aluno bloqueia a quadra no dia correto da semana"""
        # 1. Preparando o terreno
        quadra = Quadra.objects.create(nome="Quadra de Teste Mensalista", ativa=True)
        
        # Vamos simular uma data específica no futuro (ex: 20 de Maio de 2026, que é uma Quarta-feira)
        # Quarta-feira no Python é o dia número 2 (0=Seg, 1=Ter, 2=Qua...)
        data_futura = '2026-05-20'
        
        # 2. Criamos o mensalista com contrato fixo para toda Quarta-feira às 20:00
        Aluno.objects.create(
            nome="Turma de Quarta",
            whatsapp="5538999999999",
            quadra=quadra,
            dia_da_semana=2, # Quarta-feira
            horario=time(hour=20, minute=0)
        )
        
        # 3. Simulamos o cliente acessando exatamente essa quarta-feira no calendário
        resposta = self.client.get(reverse('lista_quadras'), {'data': data_futura})
        html = resposta.content.decode('utf-8')
        
        # 4. A Prova de Fogo: O sistema NÃO pode renderizar o botão das 20:00 como "Livre"
        self.assertNotIn('20:00 - Livre', html)