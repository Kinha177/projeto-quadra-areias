from django.shortcuts import render
from django.utils.timezone import now, localtime
from datetime import time, datetime
from .models import Reserva
from quadras.models import Quadra
from alunos.models import Aluno
from urllib.parse import quote  # Codificação segura de URL

def homepage(request):
    return render(request, 'reservas/homepage.html')

def lista_quadras(request):
    hora_abertura = 8
    hora_fechamento = 22
    
    agora = localtime(now())
    hoje = agora.date()
    
    data_param = request.GET.get('data')
    if data_param:
        try:
            dia_selecionado = datetime.strptime(data_param, '%Y-%m-%d').date()
        except ValueError:
            dia_selecionado = hoje
    else:
        dia_selecionado = hoje
        
    dia_da_semana_selecionado = dia_selecionado.weekday()
    
    quadras = Quadra.objects.filter(ativa=True)
    dados_das_quadras = []
    
    whatsapp_dono = "5538999999999"  # Insira o número real da Arena aqui
    
    for quadra in quadras:
        horarios_da_quadra = []
        for hora in range(hora_abertura, hora_fechamento):
            horario_atual = time(hour=hora, minute=0)
            
            # 1. Verifica se o horário já passou (para o dia de hoje)
            if dia_selecionado == hoje and hora <= agora.hour:
                status = "Esgotado"
                is_disponivel = False
                texto_whatsapp = ""
            else:
                # 2. Verifica se existe uma reserva avulsa
                tem_reserva = Reserva.objects.filter(
                    quadra=quadra,
                    data=dia_selecionado,
                    horario_inicio=horario_atual
                ).exists()
                
                # 3. Verifica se existe um mensalista fixo ativo
                tem_mensalista = Aluno.objects.filter(
                    quadra=quadra,
                    dia_da_semana=dia_da_semana_selecionado,
                    horario=horario_atual,
                    ativo=True
                ).exists()
                
                if tem_reserva or tem_mensalista:
                    status = "Ocupado"
                    is_disponivel = False
                    texto_whatsapp = ""
                else:
                    status = "Livre"
                    is_disponivel = True
                    # Proteção e formatação via quote contra caracteres especiais
                    mensagem_raw = (
                        f"Olá! Gostaria de reservar a {quadra.nome} "
                        f"no dia {dia_selecionado.strftime('%d/%m/%Y')} "
                        f"às {horario_atual.strftime('%H:%M')}."
                    )
                    texto_whatsapp = quote(mensagem_raw)
            
            horarios_da_quadra.append({
                'hora_formatada': f"{hora:02d}:00",
                'status': status,
                'disponivel': is_disponivel,
                'texto_whatsapp': texto_whatsapp
            })
            
        dados_das_quadras.append({
            'quadra': quadra,
            'horarios': horarios_da_quadra
        })
        
    contexto = {
        'whatsapp_dono': whatsapp_dono,
        'dados_das_quadras': dados_das_quadras,
        'data_selecionada': dia_selecionado.strftime('%d/%m/%Y'),
        'data_input_html': dia_selecionado.strftime('%Y-%m-%d'),
        'hoje_input_html': hoje.strftime('%Y-%m-%d'),  # Restrição de data no HTML
    }
    
    return render(request, 'reservas/lista_quadras.html', contexto)