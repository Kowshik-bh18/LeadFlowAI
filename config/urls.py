from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import RedirectView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', RedirectView.as_view(url='/questionnaires/', permanent=False)),
    path('auth/', include('apps.authentication.urls')),
    path('questionnaires/', include('apps.questionnaires.urls')),
    path('references/', include('apps.references.urls')),
    path('exports/', include('apps.exports.urls')),
    path('api/', include('apps.questionnaires.api_urls')),
    path('api/references/', include('apps.references.api_urls')),
    path('accounts/', include('allauth.urls')),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
