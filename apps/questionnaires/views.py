import csv
import io
import logging
import PyPDF2
import threading

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils.decorators import method_decorator
from django.views import View
from django.http import JsonResponse
from django.views.decorators.http import require_POST

from .models import Questionnaire, Question, Answer, Run
from apps.rag_engine.pipeline import run_questionnaire

logger = logging.getLogger(__name__)


def parse_questionnaire_file(file_obj) -> list[str]:
    """Parse uploaded file into list of question strings."""
    questions = []
    name = file_obj.name.lower()

    if name.endswith('.csv'):
        content = file_obj.read().decode('utf-8', errors='ignore')
        reader = csv.reader(io.StringIO(content))
        for row in reader:
            for cell in row:
                cell = cell.strip()
                if cell and len(cell) > 5:
                    # Skip header-like rows
                    if cell.lower() not in ('question', 'questions', '#', 'no', 'id'):
                        questions.append(cell)

    elif name.endswith('.pdf'):
        reader = PyPDF2.PdfReader(file_obj)
        for page in reader.pages:
            text = page.extract_text() or ''
            for line in text.split('\n'):
                line = line.strip()
                if len(line) > 10 and '?' in line:
                    questions.append(line)

    elif name.endswith('.txt'):
        content = file_obj.read().decode('utf-8', errors='ignore')
        for line in content.split('\n'):
            line = line.strip()
            if line and len(line) > 5:
                questions.append(line)

    # Deduplicate while preserving order
    seen = set()
    unique = []
    for q in questions:
        if q not in seen:
            seen.add(q)
            unique.append(q)

    return unique


@method_decorator(login_required, name='dispatch')
class QuestionnaireListView(View):
    template_name = 'questionnaires/list.html'

    def get(self, request):
        questionnaires = Questionnaire.objects.filter(user=request.user)
        return render(request, self.template_name, {'questionnaires': questionnaires})


@method_decorator(login_required, name='dispatch')
class QuestionnaireCreateView(View):
    template_name = 'questionnaires/create.html'

    def get(self, request):
        return render(request, self.template_name)

    def post(self, request):
        title = request.POST.get('title', '').strip()
        description = request.POST.get('description', '').strip()
        file_obj = request.FILES.get('file')
        manual_questions = request.POST.get('manual_questions', '').strip()

        if not title:
            messages.error(request, 'Please provide a title.')
            return render(request, self.template_name)

        questionnaire = Questionnaire.objects.create(
            user=request.user,
            title=title,
            description=description,
            file=file_obj,
        )

        question_texts = []

        if file_obj:
            file_obj.seek(0)
            question_texts = parse_questionnaire_file(file_obj)
        elif manual_questions:
            for line in manual_questions.split('\n'):
                line = line.strip()
                if line:
                    question_texts.append(line)

        if not question_texts:
            messages.warning(request, 'No questions could be parsed. Please check your file or input.')
            questionnaire.delete()
            return render(request, self.template_name)

        for i, text in enumerate(question_texts):
            Question.objects.create(
                questionnaire=questionnaire,
                order=i + 1,
                text=text,
            )

        messages.success(request, f'Questionnaire created with {len(question_texts)} questions.')
        return redirect('questionnaires:detail', pk=questionnaire.pk)


@method_decorator(login_required, name='dispatch')
class QuestionnaireDetailView(View):
    template_name = 'questionnaires/detail.html'

    def get(self, request, pk):
        questionnaire = get_object_or_404(Questionnaire, pk=pk, user=request.user)
        questions = questionnaire.questions.prefetch_related('answers').all()
        runs = questionnaire.runs.all()[:10]

        # Get latest answer for each question
        questions_with_answers = []
        for q in questions:
            latest = q.answers.order_by('-created_at').first()
            questions_with_answers.append((q, latest))

        context = {
            'questionnaire': questionnaire,
            'questions_with_answers': questions_with_answers,
            'runs': runs,
        }
        return render(request, self.template_name, context)


@method_decorator(login_required, name='dispatch')
class GenerateAnswersView(View):
    def post(self, request, pk):
        questionnaire = get_object_or_404(Questionnaire, pk=pk, user=request.user)
        question_ids = request.POST.getlist('question_ids')

        # Check if user has indexed reference documents
        from apps.references.models import ReferenceDocument
        indexed_docs = ReferenceDocument.objects.filter(
            user=request.user, status='indexed'
        ).count()

        if indexed_docs == 0:
            messages.error(request, 'Please upload and index at least one reference document first.')
            return redirect('questionnaires:detail', pk=pk)

        questionnaire.status = 'processing'
        questionnaire.save(update_fields=['status'])

        def _run():
            run_questionnaire(questionnaire, request.user,
                              question_ids=question_ids if question_ids else None)

        thread = threading.Thread(target=_run, daemon=True)
        thread.start()

        messages.info(request, 'Answer generation started. Refresh the page in a moment.')
        return redirect('questionnaires:detail', pk=pk)


@method_decorator(login_required, name='dispatch')
class EditAnswerView(View):
    def post(self, request, answer_pk):
        answer = get_object_or_404(Answer, pk=answer_pk, question__questionnaire__user=request.user)
        new_text = request.POST.get('answer_text', '').strip()
        if new_text:
            answer.answer_text = new_text
            answer.is_edited = True
            answer.save()
            messages.success(request, 'Answer updated.')
        qid = answer.question.questionnaire.pk
        return redirect('questionnaires:detail', pk=qid)


@method_decorator(login_required, name='dispatch')
class RunHistoryView(View):
    template_name = 'questionnaires/run_history.html'

    def get(self, request, pk):
        questionnaire = get_object_or_404(Questionnaire, pk=pk, user=request.user)
        runs = questionnaire.runs.all()
        return render(request, self.template_name, {
            'questionnaire': questionnaire,
            'runs': runs,
        })


@method_decorator(login_required, name='dispatch')
class QuestionnaireDeleteView(View):
    def post(self, request, pk):
        questionnaire = get_object_or_404(Questionnaire, pk=pk, user=request.user)
        title = questionnaire.title
        questionnaire.delete()
        messages.success(request, f'"{title}" deleted.')
        return redirect('questionnaires:list')
