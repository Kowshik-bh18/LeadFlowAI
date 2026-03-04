"""
Retriever – cosine similarity search against pgvector store.
"""
import logging
from django.db import connection
from django.conf import settings

from .embeddings import embed_query

logger = logging.getLogger(__name__)


def retrieve_chunks(query: str, user, top_k: int = None) -> list[dict]:
    """
    Retrieve top-k most relevant document chunks for a query.

    Returns list of dicts:
    {
        chunk_id, document_id, document_title, text, score
    }
    """
    top_k = top_k or settings.TOP_K_CHUNKS
    query_embedding = embed_query(query)

    if query_embedding is None:
        logger.warning("Could not generate query embedding – returning empty results")
        return []

    # pgvector cosine distance operator: <=>
    # We get cosine similarity as 1 - cosine_distance
    sql = """
        SELECT
            dc.id::text AS chunk_id,
            dc.document_id::text AS document_id,
            rd.title AS document_title,
            dc.text AS chunk_text,
            1 - (dc.embedding <=> %s::vector) AS score
        FROM references_documentchunk dc
        JOIN references_referencedocument rd ON rd.id = dc.document_id
        WHERE rd.user_id = %s
          AND dc.embedding IS NOT NULL
          AND rd.status = 'indexed'
        ORDER BY dc.embedding <=> %s::vector
        LIMIT %s
    """

    embedding_str = '[' + ','.join(str(x) for x in query_embedding) + ']'

    try:
        with connection.cursor() as cursor:
            cursor.execute(sql, [embedding_str, str(user.id), embedding_str, top_k])
            rows = cursor.fetchall()

        results = []
        for row in rows:
            chunk_id, doc_id, doc_title, chunk_text, score = row
            results.append({
                'chunk_id': chunk_id,
                'document_id': doc_id,
                'document_title': doc_title,
                'text': chunk_text,
                'score': float(score),
            })

        return results

    except Exception as e:
        logger.error(f"Retrieval error: {e}")
        return []
