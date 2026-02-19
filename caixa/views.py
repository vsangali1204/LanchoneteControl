from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.utils import timezone
from .models import Caixa, ContaCaixa, DENOMINACOES, DENOMINACAO_VALORES


def caixa_lista(request):
    caixas = Caixa.objects.all()
    caixa_aberto = Caixa.objects.filter(status='aberto').first()
    return render(request, 'caixa/lista.html', {'caixas': caixas, 'caixa_aberto': caixa_aberto})


def caixa_abrir(request):
    if Caixa.objects.filter(status='aberto').exists():
        messages.warning(request, 'Já existe um caixa aberto!')
        return redirect('caixa:lista')

    if request.method == 'POST':
        responsavel = request.POST.get('responsavel', 'Operador')
        caixa = Caixa.objects.create(responsavel=responsavel)

        total = 0
        for cod, label, valor in DENOMINACOES:
            qtd = int(request.POST.get(f'qtd_{cod}', 0) or 0)
            if qtd > 0:
                ContaCaixa.objects.create(
                    caixa=caixa, tipo='abertura', denominacao=cod, quantidade=qtd
                )
                total += qtd * valor

        caixa.total_abertura = total
        caixa.save()
        messages.success(request, f'Caixa aberto com R$ {total:.2f}!')
        return redirect('caixa:detalhe', pk=caixa.pk)

    return render(request, 'caixa/abertura.html', {'denominacoes': DENOMINACOES})


def caixa_detalhe(request, pk):
    caixa = get_object_or_404(Caixa, pk=pk)
    contas_abertura = caixa.contas.filter(tipo='abertura')
    contas_fechamento = caixa.contas.filter(tipo='fechamento')

    context = {
        'caixa': caixa,
        'contas_abertura': contas_abertura,
        'contas_fechamento': contas_fechamento,
        'diferenca': (caixa.total_fechamento or 0) - caixa.total_abertura if caixa.total_fechamento else None,
    }
    return render(request, 'caixa/detalhe.html', context)


def caixa_fechar(request, pk):
    caixa = get_object_or_404(Caixa, pk=pk)
    if caixa.status != 'aberto':
        messages.warning(request, 'Este caixa já está fechado.')
        return redirect('caixa:detalhe', pk=pk)

    if request.method == 'POST':
        total = 0
        for cod, label, valor in DENOMINACOES:
            qtd = int(request.POST.get(f'qtd_{cod}', 0) or 0)
            ContaCaixa.objects.filter(caixa=caixa, tipo='fechamento').delete()
            if qtd > 0:
                ContaCaixa.objects.create(
                    caixa=caixa, tipo='fechamento', denominacao=cod, quantidade=qtd
                )
                total += qtd * valor

        # Recalcular (pode ter duplicata no loop acima, vamos refazer)
        ContaCaixa.objects.filter(caixa=caixa, tipo='fechamento').delete()
        total = 0
        for cod, label, valor in DENOMINACOES:
            qtd = int(request.POST.get(f'qtd_{cod}', 0) or 0)
            if qtd > 0:
                ContaCaixa.objects.create(
                    caixa=caixa, tipo='fechamento', denominacao=cod, quantidade=qtd
                )
                total += qtd * valor

        caixa.total_fechamento = total
        caixa.data_fechamento = timezone.now()
        caixa.status = 'fechado'
        caixa.save()
        messages.success(request, f'Caixa fechado com R$ {total:.2f}!')
        return redirect('caixa:relatorio', pk=caixa.pk)

    # Preencher com valores de abertura como sugestão
    abertura_qtd = {c.denominacao: c.quantidade for c in caixa.contas.filter(tipo='abertura')}
    return render(request, 'caixa/fechamento.html', {
        'caixa': caixa,
        'denominacoes': DENOMINACOES,
        'abertura_qtd': abertura_qtd,
    })


def caixa_relatorio(request, pk):
    caixa = get_object_or_404(Caixa, pk=pk)
    contas_abertura = list(caixa.contas.filter(tipo='abertura'))
    contas_fechamento = list(caixa.contas.filter(tipo='fechamento'))

    # Merge para comparação
    abertura_map = {c.denominacao: c for c in contas_abertura}
    fechamento_map = {c.denominacao: c for c in contas_fechamento}

    comparacao = []
    for cod, label, valor in DENOMINACOES:
        a = abertura_map.get(cod)
        f = fechamento_map.get(cod)
        if a or f:
            qtd_a = a.quantidade if a else 0
            qtd_f = f.quantidade if f else 0
            comparacao.append({
                'label': label,
                'valor': valor,
                'qtd_abertura': qtd_a,
                'qtd_fechamento': qtd_f,
                'sub_abertura': qtd_a * valor,
                'sub_fechamento': qtd_f * valor,
                'diferenca': (qtd_f - qtd_a) * valor,
            })

    diferenca = (caixa.total_fechamento or 0) - caixa.total_abertura

    context = {
        'caixa': caixa,
        'comparacao': comparacao,
        'diferenca': diferenca,
    }
    return render(request, 'caixa/relatorio.html', context)
