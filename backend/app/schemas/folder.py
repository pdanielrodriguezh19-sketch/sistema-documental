import uuid
from datetime import datetime

from pydantic import BaseModel, Field


class FolderCreate(BaseModel):
    name: str = Field(min_length=1, max_length=150)
    repository_id: uuid.UUID
    parent_id: uuid.UUID | None = None


class FolderOut(BaseModel):
    id: uuid.UUID
    name: str
    repository_id: uuid.UUID
    parent_id: uuid.UUID | None
    created_at: datetime

    class Config:
        from_attributes = True