from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.user import User
from app.schemas.rag import AskRequest, AskResponse
from app.dependencies import get_current_user
from app.ai.rag import answer_question

router = APIRouter(prefix="/search", tags=["Búsqueda"])


@router.post("/ask", response_model=AskResponse)
def ask_across_documents(
    request: AskRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Responde una pregunta basada en TODOS los documentos del usuario."""
    answer, sources = answer_question(db, request.question, current_user.id, document_id=None)
    return AskResponse(answer=answer, sources=sources)