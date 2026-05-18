from django.shortcuts import render
from django.utils.timezone import now, localtime
from datetime import time, datetime
from .models import Reserva
from quadras.models import Quadra
from alunos.models import Aluno
from django.urls import reverse
from django.http import HttpResponseRedirect

def homepage(request):
    # Essa view apenas renderiza o visual que desenhamos no Figma!
    return render(request, 'reservas/homepage.html')

def lista_quadras(request):
    hora_abertura = 8
    hora_fechamento = 22
    
    agora = localtime(now())
    hoje = agora.date()
    hora_atual_real = agora.time()
    
    data_parametro = request.GET.get('data')
    if data_parametro:
        try:
            dia_selecionado = datetime.strptime(data_parametro, '%Y-%m-%d').date()
        except ValueError:
            dia_selecionado = hoje
    else:
        dia_selecionado = hoje
        
    # Descobrimos qual é o dia da semana da data escolhida pelo cliente (ex: 2 para Quarta-feira)
    dia_da_semana_selecionado = dia_selecionado.weekday()
    
    quadras_ativas = Quadra.objects.filter(ativa=True)
    dados_das_quadras = []
    
    for quadra in quadras_ativas:
        
        # 1. Busca as Reservas Avulsas (as que são feitas por fora)
        reservas_do_dia = Reserva.objects.filter(data=dia_selecionado, quadra=quadra)
        horarios_avulsos = [reserva.horario_inicio for reserva in reservas_do_dia]
        
        # 2. Busca os Mensalistas (os que têm contrato fixo para ESTE dia da semana)
        mensalistas_do_dia = Aluno.objects.filter(
            quadra=quadra, 
            dia_da_semana=dia_da_semana_selecionado, 
            ativo=True # Só bloqueia se o aluno não estiver com o plano pausado
        )
        horarios_mensalistas = [aluno.horario for aluno in mensalistas_do_dia]
        
        # 3. Junta as duas listas em uma só grande lista de horários PROIBIDOS
        todos_horarios_bloqueados = horarios_avulsos + horarios_mensalistas
        
        horarios_da_quadra = []
        for hora in range(hora_abertura, hora_fechamento + 1):
            horario_atual = time(hour=hora, minute=0)
            
            passou_do_tempo = False
            if dia_selecionado < hoje:
                passou_do_tempo = True
            elif dia_selecionado == hoje and horario_atual <= hora_atual_real:
                passou_do_tempo = True
                
            # Agora verificamos contra a lista combinada!
            esta_ocupado = horario_atual in todos_horarios_bloqueados
            
            texto_whatsapp = ""
            if passou_do_tempo:
                status = "Esgotado"
                is_disponivel = False
            elif esta_ocupado:
                status = "Ocupado"
                is_disponivel = False
            else:
                status = "Livre"
                is_disponivel = True
                texto_whatsapp = f"Olá! Gostaria de reservar a {quadra.nome} no dia {dia_selecionado.strftime('%d/%m/%Y')} às {horario_atual.strftime('%H:%M')}."
            
            horarios_da_quadra.append({
                'hora_formatada': horario_atual.strftime('%H:%M'),
                'disponivel': is_disponivel,
                'status': status,
                'texto_whatsapp': texto_whatsapp
            })
            
        dados_das_quadras.append({
            'quadra': quadra,
            'horarios': horarios_da_quadra
        })

    whatsapp_dono = "5538999999999" 
    
    contexto = {
        'whatsapp_dono': whatsapp_dono,
        'dados_das_quadras': dados_das_quadras,
        'data_selecionada': dia_selecionado.strftime('%d/%m/%Y'),
        'data_input_html': dia_selecionado.strftime('%Y-%m-%d'),
    }
    
    return render(request, 'reservas/lista_quadras.html', contexto)



