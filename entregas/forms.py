from django import forms
from .models import Despacho, Entrega, Motoboy, Rota, Retirada

DARK_INPUT = 'form-control bg-dark text-light border-secondary'
DARK_SELECT = 'form-select bg-dark text-light border-secondary'
DARK_TEXTAREA = 'form-control bg-dark text-light border-secondary'


class RotaForm(forms.ModelForm):
    class Meta:
        model = Rota
        fields = ['nome', 'taxa_entrega', 'descricao', 'ativa']
        widgets = {
            'nome': forms.TextInput(attrs={'class': DARK_INPUT, 'placeholder': 'Ex: Centro, Rota 1, Bairro Sul'}),
            'taxa_entrega': forms.NumberInput(attrs={'class': DARK_INPUT, 'step': '0.01', 'min': '0'}),
            'descricao': forms.TextInput(attrs={'class': DARK_INPUT}),
            'ativa': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }


class DespachoForm(forms.ModelForm):
    class Meta:
        model = Despacho
        fields = ['motoboy', 'qtd_saida', 'observacoes']
        widgets = {
            'motoboy': forms.Select(attrs={'class': DARK_SELECT}),
            'qtd_saida': forms.NumberInput(attrs={
                'class': DARK_INPUT, 'min': '1', 'placeholder': 'Quantas entregas saiu?'
            }),
            'observacoes': forms.Textarea(attrs={'class': DARK_TEXTAREA, 'rows': 2}),
        }
        labels = {
            'qtd_saida': 'Quantidade de Entregas',
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['motoboy'].queryset = Motoboy.objects.filter(ativo=True)


class EntregaRetornoForm(forms.ModelForm):
    class Meta:
        model = Entrega
        fields = ['rota', 'forma_pagamento', 'valor', 'observacoes']
        widgets = {
            'rota': forms.Select(attrs={'class': DARK_SELECT, 'id': 'id_rota_entrega'}),
            'forma_pagamento': forms.Select(attrs={'class': DARK_SELECT, 'id': 'id_forma_pgto'}),
            'valor': forms.NumberInput(attrs={'class': DARK_INPUT, 'step': '0.01', 'min': '0', 'placeholder': '0,00'}),
            'observacoes': forms.TextInput(attrs={'class': DARK_INPUT, 'placeholder': 'Opcional'}),
        }
        labels = {
            'valor': 'Valor Pago pelo Cliente (R$)',
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['rota'].queryset = Rota.objects.filter(ativa=True)
        self.fields['valor'].required = True

class MotoboyForm(forms.ModelForm):
    class Meta:
        model = Motoboy
        fields = ['nome', 'telefone', 'valor_fixo', 'ativo']
        widgets = {
            'nome': forms.TextInput(attrs={'class': DARK_INPUT}),
            'telefone': forms.TextInput(attrs={'class': DARK_INPUT}),
            'valor_fixo': forms.NumberInput(attrs={'class': DARK_INPUT, 'step': '0.01'}),
            'ativo': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }


class DespachoEditForm(forms.ModelForm):
    class Meta:
        model = Despacho
        fields = ['motoboy', 'qtd_saida', 'status', 'observacoes']
        widgets = {
            'motoboy': forms.Select(attrs={'class': DARK_SELECT}),
            'qtd_saida': forms.NumberInput(attrs={'class': DARK_INPUT, 'min': '1'}),
            'status': forms.Select(attrs={'class': DARK_SELECT}),
            'observacoes': forms.Textarea(attrs={'class': DARK_TEXTAREA, 'rows': 2}),
        }
        labels = {'qtd_saida': 'Quantidade de Entregas'}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['motoboy'].queryset = Motoboy.objects.filter(ativo=True)


class EntregaEditForm(forms.ModelForm):
    class Meta:
        model = Entrega
        fields = ['rota', 'forma_pagamento', 'valor', 'observacoes']
        widgets = {
            'rota': forms.Select(attrs={'class': DARK_SELECT}),
            'forma_pagamento': forms.Select(attrs={'class': DARK_SELECT}),
            'valor': forms.NumberInput(attrs={'class': DARK_INPUT, 'step': '0.01', 'min': '0'}),
            'observacoes': forms.TextInput(attrs={'class': DARK_INPUT, 'placeholder': 'Opcional'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['rota'].queryset = Rota.objects.filter(ativa=True)
        self.fields['valor'].required = True


class RetiradaForm(forms.ModelForm):
    class Meta:
        model = Retirada
        fields = ['valor', 'forma_pagamento', 'observacoes']
        widgets = {
            'valor': forms.NumberInput(attrs={
                'class': DARK_INPUT, 'step': '0.01', 'min': '0',
                'placeholder': '0,00', 'autofocus': True,
            }),
            'forma_pagamento': forms.Select(attrs={'class': DARK_SELECT}),
            'observacoes': forms.TextInput(attrs={'class': DARK_INPUT, 'placeholder': 'Opcional'}),
        }
        labels = {
            'valor': 'Valor (R$)',
        }
