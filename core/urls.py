from django.contrib import admin
from django.shortcuts import redirect
from django.urls import include, path, reverse
from django.conf import settings
from django.conf.urls.static import static


urlpatterns = [
    path('admin/', admin.site.urls),
    path('auth/', include('usuarios.urls')),
    path('mentorados/', include('mentorados.urls')),
    path('', lambda home: redirect(reverse('mentorados'))),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
