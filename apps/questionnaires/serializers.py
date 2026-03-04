from rest_framework import serializers
from .models import Questionnaire, Question, Answer, Run


class AnswerSerializer(serializers.ModelSerializer):
    confidence_label = serializers.ReadOnlyField()
    is_not_found = serializers.ReadOnlyField()

    class Meta:
        model = Answer
        fields = [
            'id', 'answer_text', 'confidence_score', 'confidence_label',
            'citations', 'evidence_snippets', 'is_edited', 'is_not_found',
            'created_at', 'updated_at',
        ]


class QuestionSerializer(serializers.ModelSerializer):
    latest_answer = AnswerSerializer(read_only=True)

    class Meta:
        model = Question
        fields = ['id', 'order', 'text', 'category', 'latest_answer', 'created_at']


class QuestionnaireSerializer(serializers.ModelSerializer):
    total_questions = serializers.ReadOnlyField()
    answered_questions = serializers.ReadOnlyField()
    not_found_count = serializers.ReadOnlyField()
    coverage_pct = serializers.ReadOnlyField()

    class Meta:
        model = Questionnaire
        fields = [
            'id', 'title', 'description', 'status',
            'total_questions', 'answered_questions', 'not_found_count',
            'coverage_pct', 'created_at', 'updated_at',
        ]


class RunSerializer(serializers.ModelSerializer):
    duration_seconds = serializers.ReadOnlyField()

    class Meta:
        model = Run
        fields = [
            'id', 'run_number', 'status', 'total_questions',
            'answered_count', 'not_found_count', 'error_message',
            'started_at', 'completed_at', 'duration_seconds',
        ]
