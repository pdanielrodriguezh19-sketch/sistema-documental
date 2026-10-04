import math
import uuid

from sqlalchemy.orm import Session

from app.models.document_chunk import DocumentChunk
from app.models.document import Document
from app.models.folder import Folder
from app.models.repository import Repository
from app.ai.ai_service import embed_text, ask_ai

NO_INFO_MESSAGE = "No se encontró información suficiente en los documentos disponibles."
SIMILARITY_THRESHOLD = 0.5
TOP_K = 5

SYSTEM_PROMPT = (
    "Eres un asistente que responde preguntas ÚNICAMENTE con base en el CONTEXTO proporcionado, "
    "extraído de documentos reales de una empresa. "
    "Si el contexto no contiene información suficiente para responder la pregunta, "
    f'responde EXACTAMENTE: "{NO_INFO_MESSAGE}" '
    "NUNCA inventes información que no esté en el contexto. Responde en español, de forma clara y directa."
)


def _cosine_similarity(a: list[float], b: list[float]) -> float:
    dot = sum(x * y for x, y in zip(a, b))
    norm_a = math.sqrt(sum(x * x for x in a))
    norm_b = math.sqrt(sum(y * y for y in b))
    if norm_a == 0 or norm_b == 0:
        return 0.0
    return dot / (norm_a * norm_b)


def _retrieve_chunks(db: Session, question_embedding: list[float], owner_id: uuid.UUID, document_id: uuid.UUID | None = None):
    """Busca los fragmentos más relevantes para la pregunta, dentro del alcance del usuario
    (y opcionalmente de un solo documento). Retorna lista de (chunk, score) ordenada descendente."""
    query = (
        db.query(DocumentChunk)
        .join(Document, DocumentChunk.document_id == Document.id)
        .join(Folder, Document.folder_id == Folder.id)
        .join(Repository, Folder.repository_id == Repository.id)
        .filter(Repository.owner_id == owner_id)
    )
    if document_id:
        query = query.filter(DocumentChunk.document_id == document_id)

    candidates = query.all()

    scored = []
    for chunk in candidates:
        if not chunk.embedding:
            continue
        score = _cosine_similarity(question_embedding, chunk.embedding)
        scored.append((chunk, score))

    scored.sort(key=lambda item: item[1], reverse=True)
    return scored[:TOP_K]


def answer_question(db: Session, question: str, owner_id: uuid.UUID, document_id: uuid.UUID | None = None) -> tuple[str, list[dict]]:
    """Ejecuta el flujo RAG completo: embebe la pregunta, recupera fragmentos relevantes,
    y genera una respuesta basada solo en ellos. Retorna (respuesta, fuentes)."""
    question_embedding = embed_text(question)
    top_chunks = _retrieve_chunks(db, question_embedding, owner_id, document_id)

    relevant = [(chunk, score) for chunk, score in top_chunks if score >= SIMILARITY_THRESHOLD]

    if not relevant:
        return NO_INFO_MESSAGE, []

    context = "\n\n---\n\n".join(chunk.content for chunk, _ in relevant)
    user_prompt = f"CONTEXTO:\n{context}\n\nPREGUNTA: {question}"

    answer = ask_ai(SYSTEM_PROMPT, user_prompt, max_tokens=1500).strip()
    if answer == NO_INFO_MESSAGE: return answer, []
    sources = [
        {
            "document_id": str(chunk.document_id),
            "chunk_index": chunk.chunk_index,
            "snippet": chunk.content[:200],
            "score": round(score, 4),
        }
        for chunk, score in relevant
    ]

    return answer, sources