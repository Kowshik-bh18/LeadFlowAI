from django.urls import path
from . import api_views

urlpatterns = [
    path('', api_views.DocumentListAPIView.as_view(), name='api_docs'),
    path('<uuid:pk>/status/', api_views.DocumentStatusAPIView.as_view(), name='api_doc_status'),
]
