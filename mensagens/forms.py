from django import forms
from .models import ConfigMensageiro, Contato

DARK_INPUT  = 'form-control bg-dark text-light border-secondary'
DARK_SELECT = 'form-select bg-dark text-light border-secondary'


class ConfigForm(forms.ModelForm):
    class Meta:
        model = ConfigMensageiro
        fields = ['url_api', 'instancia', 'ativo']
        widgets = {
            'url_api':    forms.TextInput(attrs={'class': DARK_INPUT}),
            'instancia':  forms.TextInput(attrs={'class': DARK_INPUT, 'placeholder': 'Ex: lanchonete01'}),
            'ativo':      forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
        labels = {
            'url_api':   'URL da API',
            'instancia': 'Nome da Instância',
            'ativo':     'Ativo',
        }


class ContatoForm(forms.ModelForm):
    class Meta:
        model = Contato
        fields = ['nome', 'numero', 'ativo']
        widgets = {
            'nome':   forms.TextInput(attrs={'class': DARK_INPUT, 'placeholder': 'Ex: Gerente'}),
            'numero': forms.TextInput(attrs={
                'class': DARK_INPUT,
                'placeholder': '5527999998888',
                'pattern': r'[0-9]+',
                'title': 'Somente dígitos, com DDI. Ex: 5527999998888',
            }),
            'ativo':  forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
        labels = {
            'numero': 'Número (com DDI, só dígitos)',
        }
