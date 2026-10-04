import uuid

from sqlalchemy import Column, Numeric, ForeignKey, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID

from app.database import Base


class DocumentCategory(Base):
    __tablename__ = "document_categories"
    __table_args__ = (UniqueConstraint("document_id", "category_id"),)

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    document_id = Column(UUID(as_uuid=True), ForeignKey("documents.id", ondelete="CASCADE"), nullable=False)
    category_id = Column(UUID(as_uuid=True), ForeignKey("categories.id", ondelete="CASCADE"), nullable=False)
    confidence = Column(Numeric(5, 4), nullable=True)