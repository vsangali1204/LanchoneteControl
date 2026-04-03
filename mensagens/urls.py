from django.urls import path
from . import views

app_name = 'mensagens'

urlpatterns = [
    path('config/',                  views.config_mensageiro, name='config'),
    path('contatos/novo/',           views.contato_novo,      name='contato_novo'),
    path('contatos/<int:pk>/editar/', views.contato_editar,   name='contato_editar'),
    path('contatos/<int:pk>/remover/', views.contato_remover, name='contato_remover'),
    path('enviar/motoboy/',          views.enviar_motoboy,    name='enviar_motoboy'),
]
