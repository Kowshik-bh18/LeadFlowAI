from django.db import models
from django.conf import settings
import uuid


class Questionnaire(models.Model):
    STATUS_CHOICES = [
        ('uploaded', 'Uploaded'),
        ('processing', 'Processing'),
        ('ready', 'Ready'),
        ('error', 'Error'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='questionnaires')
    title = models.CharField(max_length=300)
    description = models.TextField(blank=True)
    file = models.FileField(upload_to='questionnaires/', blank=True, null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='uploaded')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Questionnaire'

    def __str__(self):
        return self.title

    @property
    def total_questions(self):
        return self.questions.count()
    
    @property
    def answered_questions(self):
        return self.questions.filter(
            answers__isnull=False
        ).exclude(
            answers__answer_text='Not found in references.'
        ).distinct().count()


    @property
    def not_found_count(self):
        return self.questions.filter(
            answers__answer_text='Not found in references.'
        ).distinct().count()

    @property
    def coverage_pct(self):
        total = self.total_questions
        if total == 0:
            return 0
        return round(((total - self.not_found_count) / total) * 100)


class Question(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    questionnaire = models.ForeignKey(Questionnaire, on_delete=models.CASCADE, related_name='questions')
    order = models.PositiveIntegerField(default=0)
    text = models.TextField()
    category = models.CharField(max_length=100, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['order']

    def __str__(self):
        return f"Q{self.order}: {self.text[:80]}"

    @property
    def latest_answer(self):
        return self.answers.order_by('-created_at').first()


class Run(models.Model):
    """Version history for answer generation runs."""
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('running', 'Running'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    questionnaire = models.ForeignKey(Questionnaire, on_delete=models.CASCADE, related_name='runs')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    run_number = models.PositiveIntegerField(default=1)
    total_questions = models.PositiveIntegerField(default=0)
    answered_count = models.PositiveIntegerField(default=0)
    not_found_count = models.PositiveIntegerField(default=0)
    error_message = models.TextField(blank=True)
    started_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['-started_at']

    def __str__(self):
        return f"Run #{self.run_number} – {self.questionnaire.title}"

    @property
    def duration_seconds(self):
        if self.completed_at:
            return (self.completed_at - self.started_at).seconds
        return None


class Answer(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='answers')
    run = models.ForeignKey(Run, on_delete=models.CASCADE, related_name='answers', null=True, blank=True)
    answer_text = models.TextField()
    is_edited = models.BooleanField(default=False)
    confidence_score = models.FloatField(default=0.0)
    citations = models.JSONField(default=list)        # list of {doc_title, chunk_text, score}
    evidence_snippets = models.JSONField(default=list) # list of snippet strings
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Answer for: {self.question.text[:60]}"

    @property
    def is_not_found(self):
        return self.answer_text.strip() == 'Not found in references.'

    @property
    def confidence_label(self):
        score = self.confidence_score
        if score >= 0.75:
            return 'high'
        elif score >= 0.5:
            return 'medium'
        elif score >= 0.25:
            return 'low'
        return 'not_found'
