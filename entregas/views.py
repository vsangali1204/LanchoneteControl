from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.utils import timezone
from datetime import date
from decimal import Decimal

from .models import Despacho, Entrega, PagamentoEntrega, Motoboy, Rota, Retirada, PAGAMENTO_CHOICES
from .forms import (
    DespachoForm, DespachoEditForm,
    EntregaRetornoForm, PagamentoFormSet,
    EntregaEditForm,
    MotoboyForm, RotaForm, RetiradaForm,
)


# ─── Helpers ─────────────────────────────────────────────────────────────────

def _resumo_pagamentos(queryset_valores):
    totais = {cod: Decimal('0') for cod, _ in PAGAMENTO_CHOICES}
    for forma, valor in queryset_valores:
        if forma in totais:
            totais[forma] += valor or Decimal('0')
    return totais


# ─── Dashboard ───────────────────────────────────────────────────────────────

def dashboard(request):
    hoje = date.today()
    em_rota = Despacho.objects.filter(status='em_rota').select_related('motoboy')
    retornando = Despacho.objects.filter(status='retornando').select_related('motoboy')
    ultimos = Despacho.objects.select_related('motoboy').order_by('-data_saida')[:10]
    context = {
        'em_rota': em_rota,
        'retornando': retornando,
        'ultimos': ultimos,
        'hoje': hoje,
        'total_hoje': Despacho.objects.filter(data_saida__date=hoje).count(),
        'entregas_hoje': sum(d.qtd_saida for d in Despacho.objects.filter(data_saida__date=hoje)),
        'retiradas_hoje': Retirada.objects.filter(data__date=hoje).count(),
    }
    return render(request, 'entregas/dashboard.html', context)


# ─── Retiradas ────────────────────────────────────────────────────────────────

def retirada_nova(request):
    if request.method == 'POST':
        form = RetiradaForm(request.POST)
        if form.is_valid():
            r = form.save()
            messages.success(
                request,
                f'Retirada #{r.pk} registrada — {r.get_forma_pagamento_display()} — R$ {r.valor:.2f}'
            )
            return redirect('entregas:retirada_nova')
    else:
        form = RetiradaForm()
    hoje = date.today()
    retiradas_hoje = Retirada.objects.filter(data__date=hoje).order_by('-data')
    total_hoje = sum(r.valor for r in retiradas_hoje)
    return render(request, 'entregas/retirada_nova.html', {
        'form': form,
        'retiradas_hoje': retiradas_hoje,
        'total_hoje': total_hoje,
    })


def retirada_remover(request, pk):
    retirada = get_object_or_404(Retirada, pk=pk)
    if request.method == 'POST':
        retirada.delete()
        messages.warning(request, 'Retirada removida.')
    return redirect('entregas:retirada_nova')


# ─── Dashboard de Caixa ───────────────────────────────────────────────────────

def dashboard_caixa(request):
    data_str = request.GET.get('data', str(date.today()))
    try:
        data_ref = date.fromisoformat(data_str)
    except ValueError:
        data_ref = date.today()

    # Pagamentos agora vêm de PagamentoEntrega
    pgto_entregas_qs = PagamentoEntrega.objects.filter(
        entrega__despacho__data_saida__date=data_ref,
        entrega__despacho__status='finalizado',
    ).values_list('forma_pagamento', 'valor')
    pgto_entregas = _resumo_pagamentos(pgto_entregas_qs)
    total_entregas = sum(pgto_entregas.values())
    qtd_entregas = Entrega.objects.filter(
        despacho__data_saida__date=data_ref,
        despacho__status='finalizado',
    ).count()

    retiradas_qs = Retirada.objects.filter(data__date=data_ref).values_list('forma_pagamento', 'valor')
    pgto_retiradas = _resumo_pagamentos(retiradas_qs)
    total_retiradas = sum(pgto_retiradas.values())
    qtd_retiradas = Retirada.objects.filter(data__date=data_ref).count()

    pgto_total = {
        forma: pgto_entregas[forma] + pgto_retiradas[forma]
        for forma, _ in PAGAMENTO_CHOICES
    }
    total_geral = total_entregas + total_retiradas
    qtd_total = qtd_entregas + qtd_retiradas
    formas_label = dict(PAGAMENTO_CHOICES)

    context = {
        'data_ref': data_ref,
        'data_str': data_str,
        'qtd_entregas': qtd_entregas,
        'total_entregas': total_entregas,
        'pgto_entregas': pgto_entregas,
        'qtd_retiradas': qtd_retiradas,
        'total_retiradas': total_retiradas,
        'pgto_retiradas': pgto_retiradas,
        'qtd_total': qtd_total,
        'total_geral': total_geral,
        'pgto_total': pgto_total,
        'formas_label': formas_label,
        'formas': [f[0] for f in PAGAMENTO_CHOICES],
    }
    return render(request, 'entregas/dashboard_caixa.html', context)


# ─── Rotas ───────────────────────────────────────────────────────────────────

def rota_lista(request):
    rotas = Rota.objects.all()
    return render(request, 'entregas/rota_lista.html', {'rotas': rotas})


def rota_nova(request):
    if request.method == 'POST':
        form = RotaForm(request.POST)
        if form.is_valid():
            r = form.save()
            messages.success(request, f'Rota "{r.nome}" cadastrada com taxa R$ {r.taxa_entrega}!')
            return redirect('entregas:rota_lista')
    else:
        form = RotaForm()
    return render(request, 'entregas/rota_form.html', {'form': form, 'titulo': 'Nova Rota'})


def rota_editar(request, pk):
    rota = get_object_or_404(Rota, pk=pk)
    if request.method == 'POST':
        form = RotaForm(request.POST, instance=rota)
        if form.is_valid():
            form.save()
            messages.success(request, 'Rota atualizada!')
            return redirect('entregas:rota_lista')
    else:
        form = RotaForm(instance=rota)
    return render(request, 'entregas/rota_form.html', {'form': form, 'titulo': 'Editar Rota', 'rota': rota})


# ─── Despacho ─────────────────────────────────────────────────────────────────

def despacho_novo(request):
    if request.method == 'POST':
        form = DespachoForm(request.POST)
        if form.is_valid():
            d = form.save()
            messages.success(
                request,
                f'{d.motoboy.nome} despachado com {d.qtd_saida} entrega(s) às {d.data_saida.strftime("%H:%M")}!'
            )
            return redirect('entregas:dashboard')
    else:
        form = DespachoForm()
    return render(request, 'entregas/despacho_form.html', {'form': form})


def despacho_retorno(request, pk):
    despacho = get_object_or_404(Despacho, pk=pk)
    if despacho.status == 'em_rota':
        despacho.status = 'retornando'
        despacho.data_retorno = timezone.now()
        despacho.save()
        messages.success(request, f'{despacho.motoboy.nome} retornou! Lance as {despacho.qtd_saida} entrega(s).')
    return redirect('entregas:despacho_lancar', pk=pk)


def despacho_lancar(request, pk):
    despacho = get_object_or_404(Despacho, pk=pk)
    if despacho.status == 'finalizado':
        return redirect('entregas:despacho_resumo', pk=pk)

    entregas = despacho.entregas.prefetch_related('pagamentos', 'rota').all()
    pode_adicionar = despacho.qtd_lancada < despacho.qtd_saida

    if request.method == 'POST':
        if 'add_entrega' in request.POST:
            if not pode_adicionar:
                messages.error(request, f'Limite atingido! Despacho saiu com {despacho.qtd_saida} entrega(s).')
                return redirect('entregas:despacho_lancar', pk=pk)

            form = EntregaRetornoForm(request.POST)
            pagamento_fs = PagamentoFormSet(request.POST)

            if form.is_valid() and pagamento_fs.is_valid():
                entrega = form.save(commit=False)
                entrega.despacho = despacho
                entrega.save()
                pagamento_fs.instance = entrega
                pagamento_fs.save()

                lancadas = despacho.entregas.count()
                faltam = despacho.qtd_saida - lancadas
                if faltam == 0:
                    messages.success(request, f'Entrega {lancadas}/{despacho.qtd_saida} — tudo lançado, finalize!')
                else:
                    messages.success(request, f'Entrega {lancadas}/{despacho.qtd_saida} — faltam {faltam}.')
                return redirect('entregas:despacho_lancar', pk=pk)
            # se inválido, re-renderiza com erros (form + pagamento_fs com erros)

        elif 'remover_entrega' in request.POST:
            entrega_id = request.POST.get('entrega_id')
            Entrega.objects.filter(pk=entrega_id, despacho=despacho).delete()
            messages.warning(request, 'Entrega removida.')
            return redirect('entregas:despacho_lancar', pk=pk)

        elif 'finalizar' in request.POST:
            if despacho.pode_finalizar:
                despacho.status = 'finalizado'
                despacho.finalizado_em = timezone.now()
                despacho.save()
                messages.success(request, f'Despacho #{despacho.pk} finalizado!')
                return redirect('entregas:despacho_resumo', pk=pk)
            else:
                messages.error(request, f'Faltam {despacho.faltam} entrega(s) para finalizar.')

    else:
        form = EntregaRetornoForm() if pode_adicionar else None
        pagamento_fs = PagamentoFormSet() if pode_adicionar else None

    # Totais por forma agora somam os PagamentoEntrega
    totais_pgto = {}
    for e in entregas:
        for p in e.pagamentos.all():
            label = p.get_forma_pagamento_display()
            totais_pgto[label] = totais_pgto.get(label, Decimal('0')) + (p.valor or Decimal('0'))

    rotas_info = {str(r.pk): str(r.taxa_entrega) for r in Rota.objects.filter(ativa=True)}

    context = {
        'despacho': despacho,
        'entregas': entregas,
        'form': form,
        'pagamento_fs': pagamento_fs,
        'pode_adicionar': pode_adicionar,
        'rotas_info': rotas_info,
        'totais_pgto': totais_pgto,
    }
    return render(request, 'entregas/despacho_lancar.html', context)


def despacho_resumo(request, pk):
    despacho = get_object_or_404(Despacho, pk=pk)
    entregas = despacho.entregas.prefetch_related('pagamentos', 'rota').all()
    return render(request, 'entregas/despacho_resumo.html', {'despacho': despacho, 'entregas': entregas})


def despacho_lista(request):
    status_f = request.GET.get('status', '')
    data_f = request.GET.get('data', str(date.today()))
    motoboy_f = request.GET.get('motoboy', '')
    qs = Despacho.objects.select_related('motoboy').all()
    if status_f:
        qs = qs.filter(status=status_f)
    if data_f:
        qs = qs.filter(data_saida__date=data_f)
    if motoboy_f:
        qs = qs.filter(motoboy_id=motoboy_f)
    context = {
        'despachos': qs,
        'motoboys': Motoboy.objects.filter(ativo=True),
        'status_choices': Despacho.STATUS_CHOICES,
        'status_f': status_f,
        'data_f': data_f,
        'motoboy_f': motoboy_f,
    }
    return render(request, 'entregas/despacho_lista.html', context)


# ─── Motoboys ────────────────────────────────────────────────────────────────

def motoboy_lista(request):
    return render(request, 'entregas/motoboy_lista.html', {'motoboys': Motoboy.objects.all()})


def motoboy_novo(request):
    if request.method == 'POST':
        form = MotoboyForm(request.POST)
        if form.is_valid():
            m = form.save()
            messages.success(request, f'Motoboy {m.nome} cadastrado!')
            return redirect('entregas:motoboy_lista')
    else:
        form = MotoboyForm()
    return render(request, 'entregas/motoboy_form.html', {'form': form, 'titulo': 'Novo Motoboy'})


def motoboy_editar(request, pk):
    motoboy = get_object_or_404(Motoboy, pk=pk)
    if request.method == 'POST':
        form = MotoboyForm(request.POST, instance=motoboy)
        if form.is_valid():
            form.save()
            messages.success(request, 'Motoboy atualizado!')
            return redirect('entregas:motoboy_lista')
    else:
        form = MotoboyForm(instance=motoboy)
    return render(request, 'entregas/motoboy_form.html', {'form': form, 'titulo': 'Editar Motoboy', 'motoboy': motoboy})


# ─── Edição ───────────────────────────────────────────────────────────────────

def despacho_editar(request, pk):
    despacho = get_object_or_404(Despacho, pk=pk)
    if request.method == 'POST':
        form = DespachoEditForm(request.POST, instance=despacho)
        if form.is_valid():
            form.save()
            messages.success(request, f'Despacho #{despacho.pk} atualizado.')
            return redirect('entregas:despacho_lancar', pk=pk)
    else:
        form = DespachoEditForm(instance=despacho)
    return render(request, 'entregas/despacho_editar.html', {'form': form, 'despacho': despacho})


def entrega_editar(request, pk):
    entrega = get_object_or_404(Entrega, pk=pk)
    despacho = entrega.despacho
    if request.method == 'POST':
        form = EntregaEditForm(request.POST, instance=entrega)
        pagamento_fs = PagamentoFormSet(request.POST, instance=entrega)
        if form.is_valid() and pagamento_fs.is_valid():
            form.save()
            pagamento_fs.save()
            messages.success(request, f'Entrega #{entrega.pk} atualizada.')
            return redirect('entregas:despacho_lancar', pk=despacho.pk)
    else:
        form = EntregaEditForm(instance=entrega)
        pagamento_fs = PagamentoFormSet(instance=entrega)
    rotas_info = {str(r.pk): str(r.taxa_entrega) for r in Rota.objects.filter(ativa=True)}
    return render(request, 'entregas/entrega_editar.html', {
        'form': form,
        'pagamento_fs': pagamento_fs,
        'entrega': entrega,
        'despacho': despacho,
        'rotas_info': rotas_info,
    })


def retirada_editar(request, pk):
    retirada = get_object_or_404(Retirada, pk=pk)
    if request.method == 'POST':
        form = RetiradaForm(request.POST, instance=retirada)
        if form.is_valid():
            form.save()
            messages.success(request, f'Retirada #{retirada.pk} atualizada.')
            return redirect('entregas:retirada_nova')
    else:
        form = RetiradaForm(instance=retirada)
    return render(request, 'entregas/retirada_editar.html', {'form': form, 'retirada': retirada})


# ─── Relatório Motoboy ────────────────────────────────────────────────────────

def relatorio_motoboy(request):
    data_inicio = request.GET.get('data_inicio', str(date.today()))
    data_fim = request.GET.get('data_fim', str(date.today()))
    motoboy_id = request.GET.get('motoboy', '')
    despachos = Despacho.objects.filter(
        status='finalizado',
        data_saida__date__gte=data_inicio,
        data_saida__date__lte=data_fim,
    ).select_related('motoboy').prefetch_related('entregas__rota', 'entregas__pagamentos')
    if motoboy_id:
        despachos = despachos.filter(motoboy_id=motoboy_id)
    resumo = {}
    for d in despachos:
        mb = d.motoboy
        if mb.pk not in resumo:
            resumo[mb.pk] = {'motoboy': mb, 'viagens': 0, 'entregas': 0, 'total_taxas': 0, 'rotas': {}}
        resumo[mb.pk]['viagens'] += 1
        resumo[mb.pk]['entregas'] += d.qtd_lancada
        for e in d.entregas.all():
            resumo[mb.pk]['total_taxas'] += float(e.rota.taxa_entrega)
            nome_rota = e.rota.nome
            taxa = float(e.rota.taxa_entrega)
            if nome_rota not in resumo[mb.pk]['rotas']:
                resumo[mb.pk]['rotas'][nome_rota] = {'qtd': 0, 'taxa': taxa, 'total': 0}
            resumo[mb.pk]['rotas'][nome_rota]['qtd'] += 1
            resumo[mb.pk]['rotas'][nome_rota]['total'] += taxa
    for pk in resumo:
        mb = resumo[pk]['motoboy']
        resumo[pk]['valor_fixo'] = float(mb.valor_fixo)
        resumo[pk]['total_receber'] = float(mb.valor_fixo) + resumo[pk]['total_taxas']
        resumo[pk]['rotas'] = dict(sorted(resumo[pk]['rotas'].items()))
    context = {
        'resumo': list(resumo.values()),
        'motoboys': Motoboy.objects.filter(ativo=True),
        'data_inicio': data_inicio,
        'data_fim': data_fim,
        'motoboy_id': motoboy_id,
    }
    return render(request, 'relatorios/motoboy.html', context)