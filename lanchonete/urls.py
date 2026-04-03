from django.contrib import admin
from django.urls import path, include
from django.shortcuts import redirect

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', lambda request: redirect('entregas:dashboard'), name='home'),
    path('entregas/', include('entregas.urls', namespace='entregas')),
    path('caixa/', include('caixa.urls', namespace='caixa')),
    path('mensagens/', include('mensagens.urls', namespace='mensagens')),
]
