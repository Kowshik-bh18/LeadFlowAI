"""
Embeddings – generate vector embeddings via Google Gemini (v1 API).
Uses google-genai SDK (stable).
Model: gemini-embedding-001 (3072 dimensions)
"""

import logging
from google import genai
from django.conf import settings

logger = logging.getLogger(__name__)

# Initialize client once
client = genai.Client(api_key=settings.GEMINI_API_KEY)


def embed_text(text: str) -> list[float] | None:
    """
    Embed a single document string.
    Returns list of floats (3072 dims) or None on error.
    """
    try:
        response = client.models.embed_content(
            model="gemini-embedding-001",
            contents=text[:8000],
        )

        # New SDK returns a list of embeddings
        return response.embeddings[0].values

    except Exception as e:
        logger.error(f"Gemini embedding error: {e}")
        return None


def embed_query(text: str) -> list[float] | None:
    """
    Embed a query string.
    """
    try:
        response = client.models.embed_content(
            model="gemini-embedding-001",
            contents=text[:8000],
        )

        return response.embeddings[0].values

    except Exception as e:
        logger.error(f"Gemini query embedding error: {e}")
        return None


def embed_batch(texts: list[str]) -> list[list[float] | None]:
    """
    Embed a batch of strings.
    """
    results = []

    for text in texts:
        emb = embed_text(text)
        results.append(emb)

    return results