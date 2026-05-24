from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
 
from reservas.views import lista_quadras, homepage
from alunos.views import painel_financeiro
 
urlpatterns = [
    path('admin/', admin.site.urls),
 
    # Páginas públicas
    path('',            homepage,         name='homepage'),
    path('agendamento/', lista_quadras,   name='lista_quadras'),
 
    # Área gerencial (autenticada)
    path('financeiro/', painel_financeiro, name='painel_financeiro'),
 
    # PDV / Bar  ← NOVO
    path('pdv/', include('pdv.urls')),
]
 
# Serve arquivos de mídia em desenvolvimento
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

