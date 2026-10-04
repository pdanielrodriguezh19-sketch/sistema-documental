import uuid
from datetime import datetime

from pydantic import BaseModel


class DocumentOut(BaseModel):
    id: uuid.UUID
    name: str
    filename: str
    file_type: str
    size: int
    folder_id: uuid.UUID
    uploaded_by: uuid.UUID
    status: str
    created_at: datetime
    processed_at: datetime | None

    class Config:
        from_attributes = True


class AIResultOut(BaseModel):
    summary: str | None
    classification: str | None
    extracted_data: dict | None

    class Config:
        from_attributes = True


class DocumentDetailOut(DocumentOut):
    extracted_text: str | None
    ai_result: AIResultOut | None = None