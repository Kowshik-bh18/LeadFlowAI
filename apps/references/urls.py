from django.urls import path
from . import views

app_name = 'references'

urlpatterns = [
    path('', views.DocumentListView.as_view(), name='list'),
    path('upload/', views.DocumentUploadView.as_view(), name='upload'),
    path('<uuid:pk>/', views.DocumentDetailView.as_view(), name='detail'),
    path('<uuid:pk>/reindex/', views.DocumentReindexView.as_view(), name='reindex'),
    path('<uuid:pk>/delete/', views.DocumentDeleteView.as_view(), name='delete'),
]
