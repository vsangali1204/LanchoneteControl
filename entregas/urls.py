from django.urls import path
from . import views

app_name = 'entregas'

urlpatterns = [
    path('', views.dashboard, name='dashboard'),

    # Rotas
    path('rotas/', views.rota_lista, name='rota_lista'),
    path('rotas/nova/', views.rota_nova, name='rota_nova'),
    path('rotas/<int:pk>/editar/', views.rota_editar, name='rota_editar'),

    # Despachos
    path('despachos/', views.despacho_lista, name='despacho_lista'),
    path('despachos/novo/', views.despacho_novo, name='despacho_novo'),
    path('despachos/<int:pk>/retorno/', views.despacho_retorno, name='despacho_retorno'),
    path('despachos/<int:pk>/lancar/', views.despacho_lancar, name='despacho_lancar'),
    path('despachos/<int:pk>/resumo/', views.despacho_resumo, name='despacho_resumo'),

    # Retiradas
    path('retiradas/', views.retirada_nova, name='retirada_nova'),
    path('retiradas/<int:pk>/remover/', views.retirada_remover, name='retirada_remover'),

    # Dashboard de Caixa
    path('caixa-dashboard/', views.dashboard_caixa, name='dashboard_caixa'),

    # Motoboys
    path('motoboys/', views.motoboy_lista, name='motoboy_lista'),
    path('motoboys/novo/', views.motoboy_novo, name='motoboy_novo'),
    path('motoboys/<int:pk>/editar/', views.motoboy_editar, name='motoboy_editar'),

    # Edição
    path('despachos/<int:pk>/editar/', views.despacho_editar, name='despacho_editar'),
    path('entregas/<int:pk>/editar/', views.entrega_editar, name='entrega_editar'),
    path('retiradas/<int:pk>/editar/', views.retirada_editar, name='retirada_editar'),

    path('relatorios/motoboy/', views.relatorio_motoboy, name='relatorio_motoboy'),
]
