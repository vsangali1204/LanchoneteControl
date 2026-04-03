from django.db import models


class ConfigMensageiro(models.Model):
    """Configuração global do mensageiro (singleton)."""
    url_api = models.CharField(
        max_length=255,
        default='https://mensageiro.exata.net/api/messages/sendText/',
        help_text='URL completa do endpoint sendText'
    )
    instancia = models.CharField(
        max_length=100,
        help_text='Nome da instância no mensageiro'
    )
    ativo = models.BooleanField(default=True)

    def __str__(self):
        return f'Mensageiro — {self.instancia}'

    class Meta:
        verbose_name = 'Configuração do Mensageiro'
        verbose_name_plural = 'Configuração do Mensageiro'

    @classmethod
    def get(cls):
        """Retorna a config ativa ou None."""
        return cls.objects.filter(ativo=True).first()


class Contato(models.Model):
    """Número que receberá os relatórios via WhatsApp."""
    nome = models.CharField(max_length=100)
    numero = models.CharField(
        max_length=30,
        help_text='Somente dígitos, com DDI. Ex: 5527999998888'
    )
    ativo = models.BooleanField(default=True)

    def __str__(self):
        return f'{self.nome} ({self.numero})'

    class Meta:
        verbose_name = 'Contato'
        verbose_name_plural = 'Contatos'
        ordering = ['nome']
