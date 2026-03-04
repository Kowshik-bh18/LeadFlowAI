from django.urls import path
from . import api_views

urlpatterns = [
    path('questionnaires/', api_views.QuestionnaireListAPIView.as_view(), name='api_questionnaires'),
    path('questionnaires/<uuid:pk>/status/', api_views.QuestionnaireStatusAPIView.as_view(), name='api_q_status'),
    path('questionnaires/<uuid:pk>/answers/', api_views.QuestionnaireAnswersAPIView.as_view(), name='api_q_answers'),
]