from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated

from .models import Questionnaire, Answer
from .serializers import QuestionnaireSerializer, AnswerSerializer


class QuestionnaireListAPIView(generics.ListAPIView):
    serializer_class = QuestionnaireSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Questionnaire.objects.filter(user=self.request.user)


class QuestionnaireStatusAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, pk):
        try:
            q = Questionnaire.objects.get(pk=pk, user=request.user)
        except Questionnaire.DoesNotExist:
            return Response({'error': 'Not found'}, status=404)

        return Response({
            'id': str(q.id),
            'status': q.status,
            'total_questions': q.total_questions,
            'answered_questions': q.answered_questions,
            'not_found_count': q.not_found_count,
        })


class QuestionnaireAnswersAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, pk):
        try:
            q = Questionnaire.objects.get(pk=pk, user=request.user)
        except Questionnaire.DoesNotExist:
            return Response({'error': 'Not found'}, status=404)

        questions = q.questions.prefetch_related('answers').all()
        data = []
        for question in questions:
            latest = question.answers.order_by('-created_at').first()
            data.append({
                'question_id': str(question.id),
                'order': question.order,
                'text': question.text,
                'answer': AnswerSerializer(latest).data if latest else None,
            })

        return Response({'questionnaire': str(q.id), 'questions': data})
