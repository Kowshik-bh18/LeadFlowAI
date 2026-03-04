from django.urls import path
from . import views

app_name = 'questionnaires'

urlpatterns = [
    path('', views.QuestionnaireListView.as_view(), name='list'),
    path('create/', views.QuestionnaireCreateView.as_view(), name='create'),
    path('<uuid:pk>/', views.QuestionnaireDetailView.as_view(), name='detail'),
    path('<uuid:pk>/generate/', views.GenerateAnswersView.as_view(), name='generate'),
    path('<uuid:pk>/runs/', views.RunHistoryView.as_view(), name='run_history'),
    path('<uuid:pk>/delete/', views.QuestionnaireDeleteView.as_view(), name='delete'),
    path('answers/<uuid:answer_pk>/edit/', views.EditAnswerView.as_view(), name='edit_answer'),
]
