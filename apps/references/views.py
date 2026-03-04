import logging
import threading
import PyPDF2
import io

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils.decorators import method_decorator
from django.views import View

from .models import ReferenceDocument
from apps.rag_engine.pipeline import index_document

logger = logging.getLogger(__name__)


def extract_text_from_file(file_obj) -> str:
    """Extract raw text from uploaded file."""
    name = file_obj.name.lower()

    if name.endswith('.pdf'):
        reader = PyPDF2.PdfReader(file_obj)
        pages = []
        for page in reader.pages:
            pages.append(page.extract_text() or '')
        return '\n'.join(pages)

    elif name.endswith(('.txt', '.md')):
        return file_obj.read().decode('utf-8', errors='ignore')

    elif name.endswith('.docx'):
        try:
            import docx
            doc = docx.Document(file_obj)
            return '\n'.join([p.text for p in doc.paragraphs])
        except Exception as e:
            logger.error(f"DOCX read error: {e}")
            return ''

    else:
        # Try plain text
        try:
            return file_obj.read().decode('utf-8', errors='ignore')
        except Exception:
            return ''


@method_decorator(login_required, name='dispatch')
class DocumentListView(View):
    template_name = 'references/list.html'

    def get(self, request):
        documents = ReferenceDocument.objects.filter(user=request.user)
        return render(request, self.template_name, {'documents': documents})


@method_decorator(login_required, name='dispatch')
class DocumentUploadView(View):
    template_name = 'references/upload.html'

    def get(self, request):
        return render(request, self.template_name)

    def post(self, request):
        title = request.POST.get('title', '').strip()
        description = request.POST.get('description', '').strip()
        doc_type = request.POST.get('doc_type', '').strip()
        file_obj = request.FILES.get('file')
        manual_text = request.POST.get('manual_text', '').strip()

        if not title:
            messages.error(request, 'Please provide a document title.')
            return render(request, self.template_name)

        if not file_obj and not manual_text:
            messages.error(request, 'Please upload a file or paste document text.')
            return render(request, self.template_name)

        doc = ReferenceDocument.objects.create(
            user=request.user,
            title=title,
            description=description,
            doc_type=doc_type,
            file=file_obj,
            status='uploaded',
        )

        if file_obj:
            file_obj.seek(0)
            raw_text = extract_text_from_file(file_obj)
        else:
            raw_text = manual_text

        doc.raw_text = raw_text
        doc.save(update_fields=['raw_text'])

        # Index in background thread
        def _index():
            index_document(doc)

        thread = threading.Thread(target=_index, daemon=True)
        thread.start()

        messages.success(request, f'"{title}" uploaded and indexing started.')
        return redirect('references:list')


@method_decorator(login_required, name='dispatch')
class DocumentDetailView(View):
    template_name = 'references/detail.html'

    def get(self, request, pk):
        doc = get_object_or_404(ReferenceDocument, pk=pk, user=request.user)
        chunks = doc.chunks.all()[:20]
        return render(request, self.template_name, {'doc': doc, 'chunks': chunks})


@method_decorator(login_required, name='dispatch')
class DocumentReindexView(View):
    def post(self, request, pk):
        doc = get_object_or_404(ReferenceDocument, pk=pk, user=request.user)

        def _index():
            index_document(doc)

        thread = threading.Thread(target=_index, daemon=True)
        thread.start()
        messages.info(request, f'Re-indexing "{doc.title}" started.')
        return redirect('references:list')


@method_decorator(login_required, name='dispatch')
class DocumentDeleteView(View):
    def post(self, request, pk):
        doc = get_object_or_404(ReferenceDocument, pk=pk, user=request.user)
        title = doc.title
        doc.delete()
        messages.success(request, f'"{title}" deleted.')
        return redirect('references:list')
