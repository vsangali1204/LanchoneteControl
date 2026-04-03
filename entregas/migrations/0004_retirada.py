from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('entregas', '0003_alter_entrega_forma_pagamento'),
    ]

    operations = [
        migrations.CreateModel(
            name='Retirada',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('data', models.DateTimeField(default=django.utils.timezone.now)),
                ('forma_pagamento', models.CharField(max_length=20, choices=[
                    ('dinheiro', 'Dinheiro'),
                    ('cartao', 'Cartão'),
                    ('online', 'Pago Online'),
                    ('pix', 'Pix'),
                ])),
                ('valor', models.DecimalField(max_digits=10, decimal_places=2)),
                ('observacoes', models.CharField(max_length=255, blank=True)),
            ],
            options={
                'verbose_name': 'Retirada',
                'verbose_name_plural': 'Retiradas',
                'ordering': ['-data'],
            },
        ),
    ]
