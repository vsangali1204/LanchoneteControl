from django.urls import path
from . import views

app_name = 'caixa'

urlpatterns = [
    path('', views.caixa_lista, name='lista'),
    path('abrir/', views.caixa_abrir, name='abrir'),
    path('<int:pk>/', views.caixa_detalhe, name='detalhe'),
    path('<int:pk>/fechar/', views.caixa_fechar, name='fechar'),
    path('<int:pk>/relatorio/', views.caixa_relatorio, name='relatorio'),
]
