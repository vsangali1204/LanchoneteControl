from django.db import models
from django.utils import timezone


class Motoboy(models.Model):
    nome = models.CharField(max_length=100)
    telefone = models.CharField(max_length=20, blank=True)
    valor_fixo = models.DecimalField(max_digits=8, decimal_places=2, default=0,
                                     help_text="Valor fixo por turno/dia")
    ativo = models.BooleanField(default=True)

    def __str__(self):
        return self.nome

    class Meta:
        verbose_name = 'Motoboy'
        verbose_name_plural = 'Motoboys'
        ordering = ['nome']


class Rota(models.Model):
    """Rota = bairro/região com taxa fixa de entrega"""
    nome = models.CharField(max_length=100, help_text="Ex: Centro, Bairro Norte, Rota 1")
    taxa_entrega = models.DecimalField(max_digits=8, decimal_places=2, default=0,
                                       help_text="Taxa cobrada por entrega nesta rota")
    descricao = models.CharField(max_length=255, blank=True)
    ativa = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.nome} (R$ {self.taxa_entrega})"

    class Meta:
        verbose_name = 'Rota'
        verbose_name_plural = 'Rotas'
        ordering = ['nome']


class Despacho(models.Model):
    """Um despacho = um motoboy saindo com N entregas"""
    STATUS_CHOICES = [
        ('em_rota', 'Em Rota'),
        ('retornando', 'Retornando'),
        ('finalizado', 'Finalizado'),
    ]

    motoboy = models.ForeignKey(Motoboy, on_delete=models.PROTECT, related_name='despachos')
    data_saida = models.DateTimeField(default=timezone.now)
    data_retorno = models.DateTimeField(null=True, blank=True)
    qtd_saida = models.PositiveIntegerField(help_text="Quantidade de entregas que o motoboy saiu")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='em_rota')
    observacoes = models.TextField(blank=True)
    finalizado_em = models.DateTimeField(null=True, blank=True)

    @property
    def qtd_lancada(self):
        return self.entregas.count()

    @property
    def pode_finalizar(self):
        return self.qtd_lancada == self.qtd_saida

    @property
    def faltam(self):
        return self.qtd_saida - self.qtd_lancada

    @property
    def total_dinheiro(self):
        return sum(e.valor or 0 for e in self.entregas.filter(forma_pagamento='dinheiro'))

    @property
    def total_taxa(self):
        return sum(e.rota.taxa_entrega for e in self.entregas.select_related('rota').all())

    @property
    def duracao(self):
        if self.data_retorno and self.data_saida:
            delta = self.data_retorno - self.data_saida
            total_min = int(delta.total_seconds() // 60)
            h, m = divmod(total_min, 60)
            return f"{h}h {m:02d}min"
        return "—"

    def __str__(self):
        return f"Despacho #{self.pk} — {self.motoboy.nome} — {self.data_saida.strftime('%d/%m %H:%M')}"

    class Meta:
        verbose_name = 'Despacho'
        verbose_name_plural = 'Despachos'
        ordering = ['-data_saida']


PAGAMENTO_CHOICES = [
    ('dinheiro', 'Dinheiro'),
    ('cartao', 'Cartão'),
    ('online', 'Pago Online'),
    ('pix', 'Pix'),
]


class Retirada(models.Model):
    """Cliente pediu delivery mas vai retirar no balcão."""
    data = models.DateTimeField(default=timezone.now)
    forma_pagamento = models.CharField(max_length=20, choices=PAGAMENTO_CHOICES)
    valor = models.DecimalField(max_digits=10, decimal_places=2)
    observacoes = models.CharField(max_length=255, blank=True)

    def __str__(self):
        return f"Retirada #{self.pk} — {self.get_forma_pagamento_display()} — R$ {self.valor}"

    class Meta:
        verbose_name = 'Retirada'
        verbose_name_plural = 'Retiradas'
        ordering = ['-data']


class Entrega(models.Model):
    PAGAMENTO_CHOICES = PAGAMENTO_CHOICES

    despacho = models.ForeignKey(Despacho, on_delete=models.CASCADE, related_name='entregas')
    rota = models.ForeignKey(Rota, on_delete=models.PROTECT, related_name='entregas')
    forma_pagamento = models.CharField(max_length=20, choices=PAGAMENTO_CHOICES)
    valor = models.DecimalField(max_digits=10, decimal_places=2)  # removido null/blank
    observacoes = models.CharField(max_length=255, blank=True)

    def __str__(self):
        return f"Entrega #{self.pk} — {self.rota.nome} — {self.get_forma_pagamento_display()}"

    class Meta:
        verbose_name = 'Entrega'
        verbose_name_plural = 'Entregas'
        ordering = ['pk']