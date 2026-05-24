"""
pdv/models.py
=============
Models do módulo de Bar/PDV da Arena Ibituruna Beach.

Hierarquia:
    Categoria
        └── Produto  (com foto, estoque e preço)
    Comanda  (identificada por nome do cliente / mesa)
        └── ItemComanda  (produto + quantidade + preço histórico)

Decisões de design:
    ─ Produto.estoque é decrementado atomicamente via F() expression
      na view, eliminando race condition em dias de pico.
    ─ ItemComanda.preco_unitario congela o preço no momento do
      lançamento — reajustes futuros não afetam o histórico.
    ─ Comanda.total é uma @property calculada, nunca armazenada,
      para garantir consistência automática a qualquer momento.
"""

from decimal import Decimal
from django.db import models
from django.utils.timezone import now


# ──────────────────────────────────────────────────────────
# 1. CATEGORIA
# ──────────────────────────────────────────────────────────

class Categoria(models.Model):
    nome  = models.CharField(max_length=60, unique=True, verbose_name='Categoria')
    ordem = models.PositiveSmallIntegerField(
        default=0,
        verbose_name='Ordem',
        help_text='Categorias com número menor aparecem primeiro no PDV.',
    )

    class Meta:
        verbose_name        = 'Categoria'
        verbose_name_plural = 'Categorias'
        ordering            = ['ordem', 'nome']

    def __str__(self):
        return self.nome


# ──────────────────────────────────────────────────────────
# 2. PRODUTO
# ──────────────────────────────────────────────────────────

class Produto(models.Model):
    categoria  = models.ForeignKey(
        Categoria,
        on_delete=models.PROTECT,   # impede apagar categoria com produtos
        related_name='produtos',
        verbose_name='Categoria',
    )
    nome       = models.CharField(max_length=100, verbose_name='Nome')
    preco      = models.DecimalField(
        max_digits=8, decimal_places=2, verbose_name='Preço (R$)',
    )
    estoque    = models.PositiveIntegerField(
        default=0,
        verbose_name='Estoque atual',
        help_text='Unidades disponíveis. Decrementado automaticamente a cada venda.',
    )
    foto       = models.ImageField(
        upload_to='pdv/produtos/',
        blank=True,
        null=True,
        verbose_name='Foto',
        help_text='Recomendado: imagem quadrada, mínimo 400×400 px.',
    )
    disponivel = models.BooleanField(
        default=True,
        verbose_name='Disponível no PDV',
        help_text='Desmarque para ocultar o produto do cockpit sem apagá-lo.',
    )

    class Meta:
        verbose_name        = 'Produto'
        verbose_name_plural = 'Produtos'
        ordering            = ['categoria', 'nome']

    def __str__(self):
        return f'{self.nome}  —  R$ {self.preco:.2f}  (estoque: {self.estoque})'

    @property
    def sem_estoque(self):
        return self.estoque == 0


# ──────────────────────────────────────────────────────────
# 3. COMANDA
# ──────────────────────────────────────────────────────────

class Comanda(models.Model):
    STATUS_ABERTA    = 'aberta'
    STATUS_PAGA      = 'paga'
    STATUS_CANCELADA = 'cancelada'

    STATUS_CHOICES = [
        (STATUS_ABERTA,    'Aberta'),
        (STATUS_PAGA,      'Paga'),
        (STATUS_CANCELADA, 'Cancelada'),
    ]

    # Identifica o cliente / mesa de forma livre — sem FK obrigatória
    identificacao = models.CharField(
        max_length=80,
        verbose_name='Cliente / Mesa',
        help_text='Ex: "João Silva", "Mesa 3", "Quadra 1 – turma das 18h".',
    )
    status     = models.CharField(
        max_length=10,
        choices=STATUS_CHOICES,
        default=STATUS_ABERTA,
        verbose_name='Status',
        db_index=True,
    )
    aberta_em  = models.DateTimeField(default=now, verbose_name='Aberta em')
    fechada_em = models.DateTimeField(
        null=True, blank=True, verbose_name='Fechada em',
    )
    observacao = models.TextField(
        blank=True, null=True, verbose_name='Observação',
    )

    class Meta:
        verbose_name        = 'Comanda'
        verbose_name_plural = 'Comandas'
        ordering            = ['-aberta_em']

    # ── Propriedades calculadas ──────────────────────────────────────

    @property
    def total(self):
        """Soma os subtotais de todos os itens. Retorna Decimal."""
        return sum(
            (item.subtotal for item in self.itens.select_related('produto')),
            Decimal('0.00'),
        )

    @property
    def total_itens(self):
        """Número total de unidades lançadas (não de linhas)."""
        return sum(item.quantidade for item in self.itens.all())

    def fechar(self, status=STATUS_PAGA):
        """Fecha a comanda registrando o timestamp."""
        self.status    = status
        self.fechada_em = now()
        self.save(update_fields=['status', 'fechada_em'])

    def __str__(self):
        numero = f'#{self.pk:04d}' if self.pk else '#nova'
        return f'Comanda {numero} — {self.identificacao} ({self.get_status_display()})'


# ──────────────────────────────────────────────────────────
# 4. ITEM DE COMANDA
# ──────────────────────────────────────────────────────────

class ItemComanda(models.Model):
    comanda         = models.ForeignKey(
        Comanda,
        on_delete=models.CASCADE,
        related_name='itens',
        verbose_name='Comanda',
    )
    produto         = models.ForeignKey(
        Produto,
        on_delete=models.PROTECT,
        related_name='itens_venda',
        verbose_name='Produto',
    )
    quantidade      = models.PositiveSmallIntegerField(
        default=1, verbose_name='Qtd.',
    )
    # Preço histórico: congelado no momento do lançamento
    preco_unitario  = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        verbose_name='Preço unit.',
    )

    class Meta:
        verbose_name        = 'Item da Comanda'
        verbose_name_plural = 'Itens da Comanda'

    @property
    def subtotal(self):
        return Decimal(self.quantidade) * self.preco_unitario

    def __str__(self):
        return f'{self.quantidade}× {self.produto.nome}'
