from django import forms
from django.forms import inlineformset_factory
from .models import Despacho, Entrega, PagamentoEntrega, Motoboy, Rota, Retirada

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
    """Form principal da entrega — rota + obs. Pagamentos vêm via PagamentoFormSet."""
    class Meta:
        model = Entrega
        fields = ['rota', 'observacoes']
        widgets = {
            'rota': forms.Select(attrs={'class': DARK_SELECT, 'id': 'id_rota_entrega'}),
            'observacoes': forms.TextInput(attrs={'class': DARK_INPUT, 'placeholder': 'Opcional'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['rota'].queryset = Rota.objects.filter(ativa=True)


class PagamentoEntregaForm(forms.ModelForm):
    class Meta:
        model = PagamentoEntrega
        fields = ['forma_pagamento', 'valor']
        widgets = {
            'forma_pagamento': forms.Select(attrs={
                'class': DARK_SELECT + ' pagamento-forma',
            }),
            'valor': forms.NumberInput(attrs={
                'class': DARK_INPUT + ' pagamento-valor',
                'step': '0.01', 'min': '0', 'placeholder': '0,00',
            }),
        }


# Formset inline: mínimo 1 pagamento por entrega, máximo 4 (uma por forma)
PagamentoFormSet = inlineformset_factory(
    Entrega,
    PagamentoEntrega,
    form=PagamentoEntregaForm,
    extra=1,
    min_num=1,
    validate_min=True,
    can_delete=True,
)


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
    """Form de edição da entrega — rota + obs. Pagamentos editados via formset inline."""
    class Meta:
        model = Entrega
        fields = ['rota', 'observacoes']
        widgets = {
            'rota': forms.Select(attrs={'class': DARK_SELECT, 'id': 'id_rota_entrega'}),
            'observacoes': forms.TextInput(attrs={'class': DARK_INPUT, 'placeholder': 'Opcional'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['rota'].queryset = Rota.objects.filter(ativa=True)


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