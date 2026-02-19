from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.utils import timezone
from datetime import date

from .models import Despacho, Entrega, Motoboy, Rota
from .forms import DespachoForm, EntregaRetornoForm, MotoboyForm, RotaForm


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
    }
    return render(request, 'entregas/dashboard.html', context)


# ─── Rotas (bairros/regiões) ──────────────────────────────────────────────────

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
        messages.success(request, f'{despacho.motoboy.nome} retornou! Agora lance as {despacho.qtd_saida} entregas.')
    return redirect('entregas:despacho_lancar', pk=pk)


def despacho_lancar(request, pk):
    despacho = get_object_or_404(Despacho, pk=pk)

    if despacho.status == 'finalizado':
        return redirect('entregas:despacho_resumo', pk=pk)

    entregas = despacho.entregas.select_related('rota').all()
    form = EntregaRetornoForm()

    if request.method == 'POST':

        if 'add_entrega' in request.POST:
            # ── Bloqueia se já atingiu o limite ──
            if despacho.qtd_lancada >= despacho.qtd_saida:
                messages.error(
                    request,
                    f'Limite atingido! Este despacho saiu com apenas {despacho.qtd_saida} entrega(s).'
                )
            else:
                form = EntregaRetornoForm(request.POST)
                if form.is_valid():
                    e = form.save(commit=False)
                    e.despacho = despacho
                    e.save()
                    # Recarrega contagem após salvar
                    lancadas = despacho.entregas.count()
                    messages.success(
                        request,
                        f'Entrega {lancadas}/{despacho.qtd_saida} lançada — '
                        f'{e.rota.nome} ({e.get_forma_pagamento_display()})'
                    )
            return redirect('entregas:despacho_lancar', pk=pk)

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
                messages.success(request, f'Despacho #{despacho.pk} finalizado com sucesso!')
                return redirect('entregas:despacho_resumo', pk=pk)
            else:
                messages.error(
                    request,
                    f'Não é possível finalizar: lançadas {despacho.qtd_lancada} de {despacho.qtd_saida}. '
                    f'Faltam {despacho.faltam} entrega(s).'
                )

    rotas_info = {str(r.pk): str(r.taxa_entrega) for r in Rota.objects.filter(ativa=True)}

    context = {
        'despacho': despacho,
        'entregas': entregas,
        'form': form,
        'rotas_info': rotas_info,
    }
    return render(request, 'entregas/despacho_lancar.html', context)


def despacho_resumo(request, pk):
    despacho = get_object_or_404(Despacho, pk=pk)
    entregas = despacho.entregas.select_related('rota').all()
    return render(request, 'entregas/despacho_resumo.html', {
        'despacho': despacho,
        'entregas': entregas,
    })


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

def relatorio_motoboy(request):
    from django.db.models import Count, Sum

    data_inicio = request.GET.get('data_inicio', str(date.today()))
    data_fim = request.GET.get('data_fim', str(date.today()))
    motoboy_id = request.GET.get('motoboy', '')

    despachos = Despacho.objects.filter(
        status='finalizado',
        data_saida__date__gte=data_inicio,
        data_saida__date__lte=data_fim,
    ).select_related('motoboy').prefetch_related('entregas__rota')

    if motoboy_id:
        despachos = despachos.filter(motoboy_id=motoboy_id)

    # Agrupar por motoboy
    resumo = {}
    for d in despachos:
        mb = d.motoboy
        if mb.pk not in resumo:
            resumo[mb.pk] = {
                'motoboy': mb,
                'viagens': 0,
                'entregas': 0,
                'total_taxas': 0,
                'rotas': {},
            }
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

    # Calcular total a receber
    for pk in resumo:
        mb = resumo[pk]['motoboy']
        resumo[pk]['valor_fixo'] = float(mb.valor_fixo)
        resumo[pk]['total_receber'] = float(mb.valor_fixo) + resumo[pk]['total_taxas']
        resumo[pk]['rotas'] = dict(
            sorted(resumo[pk]['rotas'].items())
        )

    motoboys = Motoboy.objects.filter(ativo=True)

    context = {
        'resumo': list(resumo.values()),
        'motoboys': motoboys,
        'data_inicio': data_inicio,
        'data_fim': data_fim,
        'motoboy_id': motoboy_id,
    }
    return render(request, 'relatorios/motoboy.html', context)