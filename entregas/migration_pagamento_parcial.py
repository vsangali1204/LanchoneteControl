"""
Migration em dois passos:

PASSO 1 — Rode esta migration ANTES de remover forma_pagamento/valor de Entrega:
    python manage.py makemigrations --empty entregas --name pagamento_parcial_estrutura
    (cole o conteúdo abaixo no arquivo gerado)

PASSO 2 — Depois de rodar esta migration, remova os campos forma_pagamento e valor
    do model Entrega e rode:
    python manage.py makemigrations entregas --name remove_campos_legado_entrega
    python manage.py migrate

──────────────────────────────────────────────────────────────────────────────
"""

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        # Ajuste para o nome real da sua última migration
        ('entregas', '0001_initial'),
    ]

    operations = [
        # 1. Cria a tabela PagamentoEntrega
        migrations.CreateModel(
            name='PagamentoEntrega',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('forma_pagamento', models.CharField(
                    choices=[
                        ('dinheiro', 'Dinheiro'),
                        ('cartao', 'Cartão'),
                        ('online', 'Pago Online'),
                        ('pix', 'Pix'),
                    ],
                    max_length=20,
                )),
                ('valor', models.DecimalField(decimal_places=2, max_digits=10)),
                ('entrega', models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name='pagamentos',
                    to='entregas.entrega',
                )),
            ],
            options={
                'verbose_name': 'Pagamento',
                'verbose_name_plural': 'Pagamentos',
                'ordering': ['pk'],
            },
        ),

        # 2. Migração de dados: copia forma_pagamento + valor de cada Entrega
        #    existente para um PagamentoEntrega correspondente.
        migrations.RunPython(
            code=migrar_pagamentos_existentes,
            reverse_code=migrations.RunPython.noop,
        ),
    ]


def migrar_pagamentos_existentes(apps, schema_editor):
    """
    Para cada Entrega que ainda tem forma_pagamento e valor preenchidos,
    cria um PagamentoEntrega equivalente.
    Seguro rodar mesmo que as entregas já não tenham esses campos (no-op).
    """
    Entrega = apps.get_model('entregas', 'Entrega')
    PagamentoEntrega = apps.get_model('entregas', 'PagamentoEntrega')

    for e in Entrega.objects.all():
        # Verifica se os campos legados ainda existem no registro
        forma = getattr(e, 'forma_pagamento', None)
        valor = getattr(e, 'valor', None)
        if forma and valor is not None:
            PagamentoEntrega.objects.get_or_create(
                entrega=e,
                forma_pagamento=forma,
                defaults={'valor': valor},
            )
