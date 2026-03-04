from django.urls import path
from . import views

app_name = 'exports'

urlpatterns = [
    path('<uuid:pk>/docx/', views.ExportDocxView.as_view(), name='docx'),
    path('<uuid:pk>/pdf/', views.ExportPdfView.as_view(), name='pdf'),
]
