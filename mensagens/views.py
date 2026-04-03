import json
import urllib.request
import urllib.error
from datetime import date, datetime

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_POST

from .models import ConfigMensageiro, Contato
from .forms import ConfigForm, ContatoForm
from entregas.models import Despacho, Entrega, Retirada


# ─── Helpers ──────────────────────────────────────────────────────────────────

def _montar_resumo_motoboy(resumo_motoboy, data_inicio, data_fim):
    """Monta o texto da mensagem formatado para WhatsApp."""
    r = resumo_motoboy
    linhas = []

    if data_inicio == data_fim:
        d = date.fromisoformat(data_inicio)
        data_str = d.strftime('%d/%m/%Y')
    else:
        d1 = date.fromisoformat(data_inicio)
        d2 = date.fromisoformat(data_fim)
        data_str = f'{d1.strftime("%d/%m")} a {d2.strftime("%d/%m/%Y")}'

    linhas.append('   *RELATÓRIO MOTOBOY*')
    linhas.append('   *PREDILETA HAMBUEGUERIA*')
    linhas.append('TESTE DE MENSAGEM AUTOMÁTICA - NÃO RESPONDA')
    linhas.append(f'_{data_str}_')
    linhas.append('')
    linhas.append(f' *{r["motoboy"].nome.upper()}*')
    linhas.append(f'Viagens: *{r["viagens"]}*  |  Entregas: *{r["entregas"]}*')
    linhas.append('')
    linhas.append('   *Entregas por Rota*')
    for nome_rota, dados in r['rotas'].items():
        linhas.append(f'• *{nome_rota}* — {dados["qtd"]}x')
        linhas.append(f'  R$ {dados["taxa"]:.2f}/un  →  *R$ {dados["total"]:.2f}*')
    linhas.append('')
    linhas.append('   *Pagamento*')
    linhas.append(f'Valor fixo:   R$ {r["valor_fixo"]:.2f}')
    linhas.append(f'Total taxas:  R$ {r["total_taxas"]:.2f}')
    linhas.append('')
    linhas.append(f' *TOTAL A RECEBER: R$ {r["total_receber"]:.2f}*')
    linhas.append('')
    linhas.append(f'_Emitido em {datetime.now().strftime("%d/%m/%Y %H:%M")}_')

    return '\n'.join(linhas)


def _enviar_whatsapp(url_api, instancia, numero, texto):
    """Chama a API do mensageiro. Retorna (ok: bool, detalhe: str)."""
    payload = json.dumps({
        'instance_name': instancia,
        'number': numero,
        'text': texto,
    }).encode('utf-8')

    req = urllib.request.Request(
        url_api,
        data=payload,
        headers={'Content-Type': 'application/json'},
        method='POST',
    )
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            return True, resp.read().decode('utf-8')
    except urllib.error.HTTPError as e:
        return False, f'HTTP {e.code}: {e.read().decode("utf-8", errors="replace")}'
    except Exception as e:
        return False, str(e)


def _montar_resumo_view(data_inicio, data_fim, motoboy_id=None):
    """Reutiliza a mesma lógica de agrupamento do relatorio_motoboy."""
    from decimal import Decimal
    despachos = Despacho.objects.filter(
        status='finalizado',
        data_saida__date__gte=data_inicio,
        data_saida__date__lte=data_fim,
    ).select_related('motoboy').prefetch_related('entregas__rota')

    if motoboy_id:
        despachos = despachos.filter(motoboy_id=motoboy_id)

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

    for pk in resumo:
        mb = resumo[pk]['motoboy']
        resumo[pk]['valor_fixo'] = float(mb.valor_fixo)
        resumo[pk]['total_receber'] = float(mb.valor_fixo) + resumo[pk]['total_taxas']
        resumo[pk]['rotas'] = dict(sorted(resumo[pk]['rotas'].items()))

    return list(resumo.values())


# ─── Config e Contatos ────────────────────────────────────────────────────────

def config_mensageiro(request):
    config = ConfigMensageiro.objects.first()
    contatos = Contato.objects.all()

    if request.method == 'POST':
        form = ConfigForm(request.POST, instance=config)
        if form.is_valid():
            form.save()
            messages.success(request, 'Configuração salva!')
            return redirect('mensagens:config')
    else:
        form = ConfigForm(instance=config)

    return render(request, 'mensagens/config.html', {
        'form': form,
        'contatos': contatos,
        'config': config,
    })


def contato_novo(request):
    if request.method == 'POST':
        form = ContatoForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Contato adicionado!')
            return redirect('mensagens:config')
    else:
        form = ContatoForm()
    return render(request, 'mensagens/contato_form.html', {'form': form, 'titulo': 'Novo Contato'})


def contato_editar(request, pk):
    contato = get_object_or_404(Contato, pk=pk)
    if request.method == 'POST':
        form = ContatoForm(request.POST, instance=contato)
        if form.is_valid():
            form.save()
            messages.success(request, 'Contato atualizado!')
            return redirect('mensagens:config')
    else:
        form = ContatoForm(instance=contato)
    return render(request, 'mensagens/contato_form.html', {'form': form, 'titulo': 'Editar Contato', 'contato': contato})


def contato_remover(request, pk):
    contato = get_object_or_404(Contato, pk=pk)
    if request.method == 'POST':
        contato.delete()
        messages.warning(request, f'Contato "{contato.nome}" removido.')
    return redirect('mensagens:config')


# ─── Envio ────────────────────────────────────────────────────────────────────

@require_POST
def enviar_motoboy(request):
    """
    Envia o resumo de UM motoboy para todos os contatos ativos.
    Chamado via AJAX do relatório.
    """
    motoboy_id = request.POST.get('motoboy_id')
    data_inicio = request.POST.get('data_inicio', str(date.today()))
    data_fim = request.POST.get('data_fim', str(date.today()))

    config = ConfigMensageiro.get()
    if not config:
        return JsonResponse({'ok': False, 'erro': 'Mensageiro não configurado. Acesse Configurações → Mensageiro.'})

    contatos = list(Contato.objects.filter(ativo=True))
    if not contatos:
        return JsonResponse({'ok': False, 'erro': 'Nenhum contato ativo cadastrado.'})

    resumos = _montar_resumo_view(data_inicio, data_fim, motoboy_id=motoboy_id)
    if not resumos:
        return JsonResponse({'ok': False, 'erro': 'Nenhum dado encontrado para este motoboy no período.'})

    resumo = resumos[0]
    texto = _montar_resumo_motoboy(resumo, data_inicio, data_fim)

    resultados = []
    for contato in contatos:
        ok, detalhe = _enviar_whatsapp(config.url_api, config.instancia, contato.numero, texto)
        resultados.append({'contato': contato.nome, 'numero': contato.numero, 'ok': ok, 'detalhe': detalhe})

    total_ok = sum(1 for r in resultados if r['ok'])
    return JsonResponse({
        'ok': total_ok > 0,
        'motoboy': resumo['motoboy'].nome,
        'enviados': total_ok,
        'total': len(resultados),
        'resultados': resultados,
    })