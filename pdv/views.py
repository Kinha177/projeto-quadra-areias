"""
pdv/views.py
============
Views do cockpit de Bar/PDV da Arena Ibituruna Beach.

Endpoints:
    GET  /pdv/                    → dashboard principal
    POST /pdv/abrir/              → abre nova comanda
    POST /pdv/adicionar-item/     → adiciona produto a uma comanda (JSON)
    POST /pdv/remover-item/       → remove 1 unidade de um item    (JSON)
    POST /pdv/fechar/<pk>/        → fecha/paga a comanda
    POST /pdv/cancelar/<pk>/      → cancela a comanda

Todas as respostas de escrita retornam JSON para que o frontend
atualize a UI via fetch() sem reload de página — operação ágil
em tablet no balcão.
"""

import json
from decimal import Decimal

from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.db.models import F
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from .models import Comanda, ItemComanda, Produto


# ─────────────────────────────────────────────────────────────────
# Utilitário interno
# ─────────────────────────────────────────────────────────────────

def _comanda_json(comanda):
    """Serializa uma comanda com seus itens para retorno JSON."""
    itens = []
    for item in comanda.itens.select_related('produto').order_by('id'):
        itens.append({
            'id':             item.pk,
            'produto_id':     item.produto.pk,
            'produto_nome':   item.produto.nome,
            'quantidade':     item.quantidade,
            'preco_unitario': str(item.preco_unitario),
            'subtotal':       str(item.subtotal),
        })
    return {
        'id':             comanda.pk,
        'identificacao':  comanda.identificacao,
        'status':         comanda.status,
        'aberta_em':      comanda.aberta_em.strftime('%H:%M'),
        'total':          str(comanda.total),
        'total_itens':    comanda.total_itens,
        'itens':          itens,
    }


# ─────────────────────────────────────────────────────────────────
# 1. DASHBOARD
# ─────────────────────────────────────────────────────────────────

@login_required(login_url='/admin/login/')
def pdv_dashboard(request):
    """
    Cockpit principal do PDV.
    Renderiza as comandas abertas e o catálogo de produtos disponíveis.
    O JS da página assume o controle a partir daqui via fetch().
    """
    comandas_abertas = (
        Comanda.objects
        .filter(status=Comanda.STATUS_ABERTA)
        .prefetch_related('itens__produto')
        .order_by('-aberta_em')
    )

    produtos = (
        Produto.objects
        .filter(disponivel=True)
        .select_related('categoria')
        .order_by('categoria__ordem', 'categoria__nome', 'nome')
    )

    # Agrupa produtos por categoria para renderizar no template
    categorias_dict: dict[str, list] = {}
    for p in produtos:
        cat = p.categoria.nome
        categorias_dict.setdefault(cat, []).append(p)

    # Resumo do cabeçalho
    total_aberto = sum(c.total for c in comandas_abertas)
    qtd_abertas  = comandas_abertas.count()

    contexto = {
        'comandas':        comandas_abertas,
        'categorias_dict': categorias_dict,
        'total_aberto':    total_aberto,
        'qtd_abertas':     qtd_abertas,
        # Serializa as comandas para o JS bootstrapar o estado inicial
        'comandas_json':   json.dumps(
            [_comanda_json(c) for c in comandas_abertas],
            ensure_ascii=False,
        ),
        'produtos_json':   json.dumps(
            [
                {
                    'id':        p.pk,
                    'nome':      p.nome,
                    'preco':     str(p.preco),
                    'estoque':   p.estoque,
                    'foto_url':  p.foto.url if p.foto else '',
                    'categoria': p.categoria.nome,
                }
                for p in produtos
            ],
            ensure_ascii=False,
        ),
    }
    return render(request, 'pdv/pdv_dashboard.html', contexto)


# ─────────────────────────────────────────────────────────────────
# 2. ABRIR COMANDA
# ─────────────────────────────────────────────────────────────────

@login_required(login_url='/admin/login/')
@require_POST
def abrir_comanda(request):
    """
    Cria uma nova comanda vazia.
    Body: { "identificacao": "João / Mesa 3" }
    Retorna: { "comanda": { ... } }
    """
    try:
        data = json.loads(request.body)
        identificacao = data.get('identificacao', '').strip()
    except (json.JSONDecodeError, AttributeError):
        identificacao = request.POST.get('identificacao', '').strip()

    if not identificacao:
        return JsonResponse(
            {'erro': 'Informe o nome do cliente ou número da mesa.'},
            status=400,
        )

    comanda = Comanda.objects.create(identificacao=identificacao)
    return JsonResponse({'comanda': _comanda_json(comanda)}, status=201)


# ─────────────────────────────────────────────────────────────────
# 3. ADICIONAR PRODUTO À COMANDA  (operação mais frequente)
# ─────────────────────────────────────────────────────────────────

@login_required(login_url='/admin/login/')
@require_POST
def adicionar_item(request):
    """
    Adiciona +1 unidade de um produto a uma comanda.
    Body: { "comanda_id": 5, "produto_id": 12 }

    Usa select_for_update() + F() para garantir atomicidade
    do decremento de estoque sem race condition.
    """
    try:
        data       = json.loads(request.body)
        comanda_id = int(data['comanda_id'])
        produto_id = int(data['produto_id'])
    except (KeyError, ValueError, json.JSONDecodeError):
        return JsonResponse({'erro': 'Dados inválidos.'}, status=400)

    try:
        with transaction.atomic():
            comanda = get_object_or_404(
                Comanda.objects.select_for_update(),
                pk=comanda_id,
                status=Comanda.STATUS_ABERTA,
            )
            produto = get_object_or_404(
                Produto.objects.select_for_update(),
                pk=produto_id,
                disponivel=True,
            )

            if produto.estoque <= 0:
                return JsonResponse(
                    {'erro': f'"{produto.nome}" está sem estoque.'},
                    status=400,
                )

            # Decrementa estoque de forma atômica
            Produto.objects.filter(pk=produto_id).update(
                estoque=F('estoque') - 1
            )

            # Incrementa a linha existente OU cria nova
            item, criado = ItemComanda.objects.get_or_create(
                comanda=comanda,
                produto=produto,
                defaults={'preco_unitario': produto.preco, 'quantidade': 1},
            )
            if not criado:
                item.quantidade += 1
                item.save(update_fields=['quantidade'])

            # Recarrega comanda para retornar estado fresco
            comanda.refresh_from_db()

    except Exception as exc:
        return JsonResponse({'erro': str(exc)}, status=500)

    return JsonResponse({'comanda': _comanda_json(comanda)})


# ─────────────────────────────────────────────────────────────────
# 4. REMOVER 1 UNIDADE DE UM ITEM
# ─────────────────────────────────────────────────────────────────

@login_required(login_url='/admin/login/')
@require_POST
def remover_item(request):
    """
    Remove 1 unidade de um ItemComanda.
    Se a quantidade chegar a 0, o item é apagado.
    Body: { "item_id": 42 }
    """
    try:
        data    = json.loads(request.body)
        item_id = int(data['item_id'])
    except (KeyError, ValueError, json.JSONDecodeError):
        return JsonResponse({'erro': 'Dados inválidos.'}, status=400)

    try:
        with transaction.atomic():
            item    = get_object_or_404(
                ItemComanda.objects.select_for_update().select_related('comanda', 'produto'),
                pk=item_id,
                comanda__status=Comanda.STATUS_ABERTA,
            )
            comanda = item.comanda

            # Devolve 1 unidade ao estoque
            Produto.objects.filter(pk=item.produto_id).update(
                estoque=F('estoque') + 1
            )

            if item.quantidade > 1:
                item.quantidade -= 1
                item.save(update_fields=['quantidade'])
            else:
                item.delete()

            comanda.refresh_from_db()

    except Exception as exc:
        return JsonResponse({'erro': str(exc)}, status=500)

    return JsonResponse({'comanda': _comanda_json(comanda)})


# ─────────────────────────────────────────────────────────────────
# 5. FECHAR / PAGAR COMANDA
# ─────────────────────────────────────────────────────────────────

@login_required(login_url='/admin/login/')
@require_POST
def fechar_comanda(request, pk):
    """
    Marca a comanda como PAGA.
    POST /pdv/fechar/<pk>/
    """
    comanda = get_object_or_404(Comanda, pk=pk, status=Comanda.STATUS_ABERTA)
    comanda.fechar(status=Comanda.STATUS_PAGA)
    return JsonResponse({'ok': True, 'comanda_id': pk})


# ─────────────────────────────────────────────────────────────────
# 6. CANCELAR COMANDA
# ─────────────────────────────────────────────────────────────────

@login_required(login_url='/admin/login/')
@require_POST
def cancelar_comanda(request, pk):
    """
    Cancela a comanda e devolve todo o estoque dos itens.
    POST /pdv/cancelar/<pk>/
    """
    comanda = get_object_or_404(Comanda, pk=pk, status=Comanda.STATUS_ABERTA)

    with transaction.atomic():
        for item in comanda.itens.select_related('produto'):
            Produto.objects.filter(pk=item.produto_id).update(
                estoque=F('estoque') + item.quantidade
            )
        comanda.fechar(status=Comanda.STATUS_CANCELADA)

    return JsonResponse({'ok': True, 'comanda_id': pk})
