from django.db import migrations, models
import django.db.models.deletion


def migrar_pagamentos_existentes(apps, schema_editor):
    """
    Copia forma_pagamento + valor de cada Entrega existente
    para um PagamentoEntrega correspondente.
    """
    Entrega = apps.get_model('entregas', 'Entrega')
    PagamentoEntrega = apps.get_model('entregas', 'PagamentoEntrega')

    for e in Entrega.objects.all():
        forma = e.forma_pagamento
        valor = e.valor
        if forma and valor is not None:
            PagamentoEntrega.objects.create(
                entrega=e,
                forma_pagamento=forma,
                valor=valor,
            )


class Migration(migrations.Migration):

    dependencies = [
        ('entregas', '0004_retirada'),
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

        # 2. Migra dados existentes: cada Entrega vira um PagamentoEntrega
        migrations.RunPython(migrar_pagamentos_existentes, migrations.RunPython.noop),

        # 3. Remove os campos legados de Entrega
        migrations.RemoveField(
            model_name='entrega',
            name='forma_pagamento',
        ),
        migrations.RemoveField(
            model_name='entrega',
            name='valor',
        ),
    ]
