from django.db import models
from django.utils import timezone


class Caixa(models.Model):
    STATUS_CHOICES = [
        ('aberto', 'Aberto'),
        ('fechado', 'Fechado'),
    ]

    data_abertura = models.DateTimeField(default=timezone.now)
    data_fechamento = models.DateTimeField(null=True, blank=True)
    responsavel = models.CharField(max_length=100, default='Operador')
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='aberto')
    observacoes = models.TextField(blank=True)

    # Totais calculados
    total_abertura = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    total_fechamento = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)

    def __str__(self):
        return f"Caixa {self.data_abertura.strftime('%d/%m/%Y')} - {self.responsavel}"

    class Meta:
        verbose_name = 'Caixa'
        verbose_name_plural = 'Caixas'
        ordering = ['-data_abertura']


DENOMINACOES = [
    # Notas
    ('nota_200', 'Nota R$ 200', 200.0),
    ('nota_100', 'Nota R$ 100', 100.0),
    ('nota_50', 'Nota R$ 50', 50.0),
    ('nota_20', 'Nota R$ 20', 20.0),
    ('nota_10', 'Nota R$ 10', 10.0),
    ('nota_5', 'Nota R$ 5', 5.0),
    ('nota_2', 'Nota R$ 2', 2.0),
    # Moedas
    ('moeda_100', 'Moeda R$ 1,00', 1.0),
    ('moeda_50', 'Moeda R$ 0,50', 0.5),
    ('moeda_25', 'Moeda R$ 0,25', 0.25),
    ('moeda_10', 'Moeda R$ 0,10', 0.10),
    ('moeda_5', 'Moeda R$ 0,05', 0.05),
    ('moeda_1', 'Moeda R$ 0,01', 0.01),
]

DENOMINACAO_CHOICES = [(d[0], d[1]) for d in DENOMINACOES]
DENOMINACAO_VALORES = {d[0]: d[2] for d in DENOMINACOES}


class ContaCaixa(models.Model):
    TIPO_CHOICES = [
        ('abertura', 'Abertura'),
        ('fechamento', 'Fechamento'),
    ]

    caixa = models.ForeignKey(Caixa, on_delete=models.CASCADE, related_name='contas')
    tipo = models.CharField(max_length=15, choices=TIPO_CHOICES)
    denominacao = models.CharField(max_length=20, choices=DENOMINACAO_CHOICES)
    quantidade = models.PositiveIntegerField(default=0)

    @property
    def valor_unitario(self):
        return DENOMINACAO_VALORES.get(self.denominacao, 0)

    @property
    def subtotal(self):
        return self.quantidade * self.valor_unitario

    def __str__(self):
        return f"{self.get_denominacao_display()} x {self.quantidade}"

    class Meta:
        pass  # ordenação feita via DENOMINACOES no template
