"""
RAG Pipeline – orchestrates chunking, embedding, retrieval, and generation.
"""
import logging
from django.utils import timezone

from apps.references.models import ReferenceDocument, DocumentChunk
from apps.questionnaires.models import Questionnaire, Question, Answer, Run
from .chunker import chunk_document
from .embeddings import embed_text, embed_batch
from .retriever import retrieve_chunks
from .generator import generate_answer

logger = logging.getLogger(__name__)


def index_document(document: ReferenceDocument) -> bool:
    """
    Chunk and embed a reference document, storing vectors in pgvector.
    Returns True on success.
    """
    try:
        document.status = 'processing'
        document.save(update_fields=['status'])

        # Delete old chunks
        document.chunks.all().delete()

        # Chunk
        chunks = chunk_document(document)
        if not chunks:
            logger.warning(f"No chunks for document {document.id}")
            document.status = 'error'
            document.save(update_fields=['status'])
            return False

        # Embed in batch
        embeddings = embed_batch(chunks)

        # Store
        chunk_objects = []
        for idx, (chunk_text, embedding) in enumerate(zip(chunks, embeddings)):
            chunk_obj = DocumentChunk(
                document=document,
                chunk_index=idx,
                text=chunk_text,
                embedding=embedding,
                token_count=len(chunk_text.split()),
            )
            chunk_objects.append(chunk_obj)

        DocumentChunk.objects.bulk_create(chunk_objects, batch_size=200)

        document.total_chunks = len(chunk_objects)
        document.status = 'indexed'
        document.save(update_fields=['total_chunks', 'status'])

        logger.info(f"Indexed {len(chunk_objects)} chunks for {document.title}")
        return True

    except Exception as e:
        logger.error(f"Indexing error for {document.id}: {e}")
        document.status = 'error'
        document.save(update_fields=['status'])
        return False


def run_questionnaire(questionnaire: Questionnaire, user, question_ids=None) -> Run:
    """
    Run the full RAG pipeline for a questionnaire.
    If question_ids is provided, only regenerate those questions.
    Returns the Run object.
    """
    # Determine run number
    last_run = questionnaire.runs.first()
    run_number = (last_run.run_number + 1) if last_run else 1

    run = Run.objects.create(
        questionnaire=questionnaire,
        user=user,
        status='running',
        run_number=run_number,
    )

    try:
        if question_ids:
            questions = questionnaire.questions.filter(id__in=question_ids)
        else:
            questions = questionnaire.questions.all()

        run.total_questions = questions.count()
        run.save(update_fields=['total_questions'])

        answered = 0
        not_found = 0

        for question in questions:
            # Retrieve
            chunks = retrieve_chunks(question.text, user)

            # Generate
            result = generate_answer(question.text, chunks)

            # Save answer (linked to this run)
            Answer.objects.create(
                question=question,
                run=run,
                answer_text=result['answer_text'],
                confidence_score=result['confidence_score'],
                citations=result['citations'],
                evidence_snippets=result['evidence_snippets'],
            )

            if result['answer_text'] == 'Not found in references.':
                not_found += 1
            else:
                answered += 1

        run.answered_count = answered
        run.not_found_count = not_found
        run.status = 'completed'
        run.completed_at = timezone.now()
        run.save()

        questionnaire.status = 'ready'
        questionnaire.save(update_fields=['status'])

        return run

    except Exception as e:
        logger.error(f"Pipeline error: {e}")
        run.status = 'failed'
        run.error_message = str(e)
        run.completed_at = timezone.now()
        run.save()
        return run
