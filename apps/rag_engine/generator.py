"""
Generator – produces grounded answers using Google Gemini (v1 API).
Uses google-genai SDK (stable).
Model: gemini-2.5-flash
"""

import logging
from google import genai
from django.conf import settings

logger = logging.getLogger(__name__)

# Initialize client once
client = genai.Client(api_key=settings.GEMINI_API_KEY)


SYSTEM_PROMPT = """You are a compliance and security expert helping answer enterprise questionnaires.

Rules you MUST follow:
1. Answer ONLY based on the provided reference documents.
2. If the context does not contain enough information, respond with EXACTLY:
   Not found in references.
3. Be concise, factual, and professional (2-4 sentences).
4. Do NOT hallucinate or add any information not in the context.
5. Do not repeat the question in your answer.
"""

ANSWER_PROMPT_TEMPLATE = """Reference Documents:
{context}

---
Question: {question}

Answer strictly using the reference documents above.
If the information is not available, respond with exactly: Not found in references.
Keep the answer concise (2-4 sentences).
"""


def generate_answer(question: str, chunks: list[dict]) -> dict:

    if not chunks:
        return {
            "answer_text": "Not found in references.",
            "confidence_score": 0.0,
            "citations": [],
            "evidence_snippets": [],
        }

    threshold = settings.CONFIDENCE_THRESHOLD
    relevant_chunks = [c for c in chunks if c["score"] >= threshold]

    if not relevant_chunks:
        return {
            "answer_text": "Not found in references.",
            "confidence_score": 0.0,
            "citations": [],
            "evidence_snippets": [],
        }

    # Build context
    context_parts = []
    for i, chunk in enumerate(relevant_chunks, 1):
        context_parts.append(
            f"[{i}] Source: {chunk['document_title']}\n{chunk['text']}"
        )

    context = "\n\n".join(context_parts)
    prompt = ANSWER_PROMPT_TEMPLATE.format(
        context=context,
        question=question,
    )

    try:
        response = client.models.generate_content(
    model="gemini-2.5-flash",
    contents=f"{SYSTEM_PROMPT}\n\n{prompt}",
    config={
        "temperature": 0.1,
        "max_output_tokens": 600,
    },
)

        answer_text = (response.text or "").strip()

    except Exception as e:
        logger.error(f"Gemini generation error: {e}")
        return {
            "answer_text": "Not found in references.",
            "confidence_score": 0.0,
            "citations": [],
            "evidence_snippets": [],
        }

    # Confidence score
    confidence_score = round(
        sum(c["score"] for c in relevant_chunks) / len(relevant_chunks), 3
    )

    # Deduplicated citations
    seen_docs = set()
    citations = []

    for chunk in relevant_chunks:
        key = chunk["document_id"]
        if key not in seen_docs:
            seen_docs.add(key)
            citations.append(
                {
                    "document_id": chunk["document_id"],
                    "document_title": chunk["document_title"],
                    "chunk_text": chunk["text"][:300],
                    "score": round(chunk["score"], 3),
                }
            )

    evidence_snippets = [
        c["text"][:200] for c in relevant_chunks[:3]
    ]

    return {
        "answer_text": answer_text,
        "confidence_score": confidence_score,
        "citations": citations,
        "evidence_snippets": evidence_snippets,
    }