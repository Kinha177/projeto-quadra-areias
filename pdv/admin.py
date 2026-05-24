"""
pdv/admin.py
============
Painel administrativo do módulo PDV.

Funcionalidades-chave:
    ─ ProdutoAdmin: edita preço e estoque direto na listagem (list_editable)
    ─ thumbnail() exibe miniatura da foto na grade do Admin
    ─ CategoriaAdmin: reordena as categorias direto na lista
"""

from django.contrib import admin
from django.utils.html import format_html
from .models import Categoria, Produto, Comanda, ItemComanda


# ──────────────────────────────────────────────────────────
# CATEGORIA
# ──────────────────────────────────────────────────────────

@admin.register(Categoria)
class CategoriaAdmin(admin.ModelAdmin):
    list_display  = ('nome', 'ordem', 'qtd_produtos')
    list_editable = ('ordem',)
    search_fields = ('nome',)

    @admin.display(description='Produtos')
    def qtd_produtos(self, obj):
        return obj.produtos.count()


# ──────────────────────────────────────────────────────────
# PRODUTO
# ──────────────────────────────────────────────────────────

@admin.register(Produto)
class ProdutoAdmin(admin.ModelAdmin):
    # Thumbnail + campos editáveis na listagem
    list_display  = (
        'thumbnail',        # miniatura da foto
        'nome',
        'categoria',
        'preco',            # list_editable abaixo
        'estoque',          # list_editable abaixo
        'disponivel',
    )
    list_editable  = ('preco', 'estoque', 'disponivel')
    list_filter    = ('disponivel', 'categoria')
    search_fields  = ('nome',)
    ordering       = ('categoria', 'nome')

    fieldsets = (
        ('📦 Produto', {
            'fields': ('categoria', 'nome', 'foto'),
        }),
        ('💰 Preço e Estoque', {
            'fields': ('preco', 'estoque', 'disponivel'),
            'description': (
                'Atenção: alterar o preço afeta apenas novas vendas. '
                'Itens já lançados em comandas abertas mantêm o preço histórico.'
            ),
        }),
    )

    # ── Miniatura ────────────────────────────────────────────────────
    @admin.display(description='Foto')
    def thumbnail(self, obj):
        if obj.foto:
            return format_html(
                '<img src="{}" style="'
                'width:52px; height:52px; object-fit:cover;'
                'border-radius:10px; box-shadow:0 2px 8px rgba(0,0,0,0.15);'
                '" />',
                obj.foto.url,
            )
        return format_html(
            '<div style="'
            'width:52px; height:52px; border-radius:10px;'
            'background:#f3f4f6; display:flex; align-items:center;'
            'justify-content:center; font-size:1.4rem;'
            '">🍽️</div>'
        )


# ──────────────────────────────────────────────────────────
# COMANDA  (somente leitura no admin — operação é no PDV)
# ──────────────────────────────────────────────────────────

class ItemComandaInline(admin.TabularInline):
    model          = ItemComanda
    extra          = 0
    can_delete     = False
    readonly_fields = ('produto', 'quantidade', 'preco_unitario', 'subtotal_display')
    fields          = ('produto', 'quantidade', 'preco_unitario', 'subtotal_display')

    @admin.display(description='Subtotal')
    def subtotal_display(self, obj):
        return format_html(
            '<strong style="color:#6F42C1;">R$ {:.2f}</strong>', obj.subtotal
        )

    def has_add_permission(self, request, obj=None):
        return False  # Adição acontece pelo cockpit, não pelo admin


@admin.register(Comanda)
class ComandaAdmin(admin.ModelAdmin):
    inlines      = [ItemComandaInline]
    list_display = (
        'numero', 'identificacao', 'status_badge',
        'aberta_em', 'total_display',
    )
    list_filter  = ('status',)
    search_fields = ('identificacao',)
    date_hierarchy = 'aberta_em'
    readonly_fields = (
        'aberta_em', 'fechada_em', 'total_display',
    )

    def has_add_permission(self, request):
        # Comandas são abertas pelo cockpit PDV, não pelo admin
        return False

    @admin.display(description='#', ordering='pk')
    def numero(self, obj):
        return format_html(
            '<span style="font-family:monospace;font-weight:700;color:#6F42C1;">#{:04d}</span>',
            obj.pk,
        )

    @admin.display(description='Status')
    def status_badge(self, obj):
        estilos = {
            'aberta':    ('#d1fae5', '#065f46', '#6ee7b7', '🟢 Aberta'),
            'paga':      ('#ede9fe', '#4c1d95', '#c4b5fd', '✅ Paga'),
            'cancelada': ('#fee2e2', '#991b1b', '#fca5a5', '❌ Cancelada'),
        }
        bg, txt, border, label = estilos.get(
            obj.status, ('#f3f4f6', '#374151', '#d1d5db', obj.status)
        )
        return format_html(
            '<span style="background:{};color:{};border:1px solid {};'
            'border-radius:50px;padding:3px 12px;font-size:.78rem;font-weight:700;">'
            '{}</span>',
            bg, txt, border, label,
        )

    @admin.display(description='Total')
    def total_display(self, obj):
        return format_html(
            '<strong style="color:#6F42C1;font-variant-numeric:tabular-nums;">'
            'R$ {:.2f}</strong>',
            obj.total,
        )


# ══════════════════════════════════════════════════════════
# SNIPPET PARA settings.py  ──  Cole no seu JAZZMIN_SETTINGS
# ══════════════════════════════════════════════════════════
#
# 1. Adicione 'pdv' em INSTALLED_APPS:
#
#   INSTALLED_APPS = [
#       ...
#       'pdv',
#   ]
#
# 2. Atualize JAZZMIN_SETTINGS — adicione as chaves abaixo
#    DENTRO do dicionário existente:
#
#   "icons": {
#       # ── apps já existentes ──
#       "auth":              "fas fa-users-cog",
#       "auth.user":         "fas fa-user-shield",
#       "alunos.Aluno":      "fas fa-user-graduate",
#       "alunos.Pagamento":  "fas fa-dollar-sign",
#       "quadras.Quadra":    "fas fa-volleyball-ball",
#       "reservas.Reserva":  "fas fa-calendar-check",
#       # ── PDV / Bar ──
#       "pdv":               "fas fa-cash-register",
#       "pdv.Categoria":     "fas fa-tags",
#       "pdv.Produto":       "fas fa-burger",
#       "pdv.Comanda":       "fas fa-receipt",
#       "pdv.ItemComanda":   "fas fa-list-ul",
#   },
#
#   "order_with_respect_to": [
#       "pdv.Comanda",        # 1. ver comandas abertas
#       "pdv.Produto",        # 2. ajustar estoque / preços
#       "pdv.Categoria",      # 3. raramente muda
#       "alunos.Pagamento",
#       "reservas.Reserva",
#       "alunos.Aluno",
#       "quadras.Quadra",
#       "auth",
#   ],
#
#   "topmenu_links": [
#       {"name": "🌐 Ver o Site",        "url": "/",            "new_window": True},
#       {"name": "🍺 PDV / Bar",          "url": "/pdv/",        "new_window": True},
#       {"name": "📊 Financeiro",         "url": "/financeiro/"},
#       {"name": "📅 Agendamento",        "url": "/agendamento/","new_window": True},
#   ],
