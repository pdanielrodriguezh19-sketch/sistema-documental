import uuid

from pydantic import BaseModel


class AskRequest(BaseModel):
    question: str


class SourceOut(BaseModel):
    document_id: uuid.UUID
    chunk_index: int
    snippet: str
    score: float


class AskResponse(BaseModel):
    answer: str
    sources: list[SourceOut]