"""
Chunker – splits text into overlapping windows for embedding.
"""
from django.conf import settings


def chunk_text(text: str, chunk_size: int = None, overlap: int = None) -> list[str]:
    """
    Split text into chunks of approximately `chunk_size` words
    with `overlap` words of context overlap between chunks.
    """
    chunk_size = chunk_size or settings.CHUNK_SIZE
    overlap = overlap or settings.CHUNK_OVERLAP

    # Normalise whitespace
    text = ' '.join(text.split())
    words = text.split(' ')

    if not words:
        return []

    chunks = []
    start = 0

    while start < len(words):
        end = start + chunk_size
        chunk = ' '.join(words[start:end])
        if chunk.strip():
            chunks.append(chunk.strip())
        start += chunk_size - overlap

    return chunks


def chunk_document(document) -> list[str]:
    """
    Chunk a ReferenceDocument instance.
    Returns list of chunk strings.
    """
    text = document.raw_text or ''
    if not text.strip():
        return []
    return chunk_text(text)
