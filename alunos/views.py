from django.shortcuts import render
from django.utils.timezone import now, localtime
from django.contrib.auth.decorators import login_required
from .models import Aluno, Pagamento

@login_required(login_url='/admin/login/')
def painel_financeiro(request):
    hoje = localtime(now()).date()
    mes_atual = hoje.month
    ano_atual = hoje.year

    alunos = Aluno.objects.filter(ativo=True)
    lista_financeira = []

    for aluno in alunos:
        pagou_este_mes = Pagamento.objects.filter(
            aluno=aluno,
            mes_referencia__year=ano_atual,
            mes_referencia__month=mes_atual,
            pago=True
        ).exists()

        if pagou_este_mes:
            status = "Pagamento OK"
            classe_css = "ok"
        else:
            if hoje.day > aluno.dia_vencimento:
                status = f"Atrasado (Venceu dia {aluno.dia_vencimento})"
                classe_css = "atrasado"
            else:
                status = f"A Vencer (Dia {aluno.dia_vencimento})"
                classe_css = "avencer"

        lista_financeira.append({
            'nome': aluno.nome,
            'valor': aluno.valor_mensalidade,
            'status': status,
            'classe_css': classe_css,
        })

    # Cálculos dos totais recomendados pela auditoria
    total_ok = sum(1 for i in lista_financeira if i['classe_css'] == 'ok')
    total_atrasado = sum(1 for i in lista_financeira if i['classe_css'] == 'atrasado')
    total_avencer = sum(1 for i in lista_financeira if i['classe_css'] == 'avencer')
    
    receita_confirmada = sum(i['valor'] for i in lista_financeira if i['classe_css'] == 'ok')
    receita_pendente = sum(i['valor'] for i in lista_financeira if i['classe_css'] != 'ok')

    contexto = {
        'lista_financeira': lista_financeira,
        'mes_texto': hoje.strftime('%B de %Y').capitalize(),
        'total_ok': total_ok,
        'total_atrasado': total_atrasado,
        'total_avencer': total_avencer,
        'receita_confirmada': receita_confirmada,
        'receita_pendente': receita_pendente,
    }

    return render(request, 'alunos/painel_financeiro.html', contexto)