import uuid
from datetime import datetime

from pydantic import BaseModel, Field


class RepositoryCreate(BaseModel):
    name: str = Field(min_length=2, max_length=150)
    description: str | None = None


class RepositoryOut(BaseModel):
    id: uuid.UUID
    name: str
    description: str | None
    owner_id: uuid.UUID
    created_at: datetime

    class Config:
        from_attributes = True