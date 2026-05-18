from django.shortcuts import render
from django.utils.timezone import now, localtime
from .models import Aluno, Pagamento

def painel_financeiro(request):
    # Descobrimos o dia, mês e ano exatos de HOJE
    hoje = localtime(now()).date()
    mes_atual = hoje.month
    ano_atual = hoje.year

    # Puxamos TODOS os clientes ativos da arena
    alunos = Aluno.objects.filter(ativo=True)
    
    lista_financeira = []

    for aluno in alunos:
        # O sistema procura: "Existe algum Pix/Pagamento salvo para ESSE aluno, NESSE mês e NESSE ano?"
        pagou_este_mes = Pagamento.objects.filter(
            aluno=aluno,
            mes_referencia__year=ano_atual,
            mes_referencia__month=mes_atual,
            pago=True
        ).exists()

        if pagou_este_mes:
            status = "Pagamento OK"
            classe_css = "ok" # Vai ficar verde na tela
        else:
            # Se não pagou, vamos cruzar o dia de hoje com a data de vencimento dele
            if hoje.day > aluno.dia_vencimento:
                status = f"Atrasado (Venceu dia {aluno.dia_vencimento})"
                classe_css = "atrasado" # Vai ficar vermelho
            else:
                status = f"A Vencer (Dia {aluno.dia_vencimento})"
                classe_css = "avencer" # Vai ficar laranja

        lista_financeira.append({
            'nome': aluno.nome,
            'valor': aluno.valor_mensalidade,
            'status': status,
            'classe_css': classe_css,
        })

    contexto = {
        'lista_financeira': lista_financeira,
        'mes_texto': hoje.strftime('%m/%Y')
    }
    
    return render(request, 'alunos/painel_financeiro.html', contexto)