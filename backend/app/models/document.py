import uuid
import enum

from sqlalchemy import Column, String, BigInteger, Text, DateTime, ForeignKey, Enum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

from app.database import Base


class DocumentStatus(str, enum.Enum):
    pendiente = "pendiente"
    procesando = "procesando"
    procesado = "procesado"
    error = "error"


class Document(Base):
    __tablename__ = "documents"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False)
    filename = Column(String(255), nullable=False)
    file_type = Column(String(10), nullable=False)
    file_path = Column(String(500), nullable=False)
    size = Column(BigInteger, nullable=False)
    folder_id = Column(UUID(as_uuid=True), ForeignKey("folders.id", ondelete="CASCADE"), nullable=False)
    uploaded_by = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="RESTRICT"), nullable=False)
    status = Column(Enum(DocumentStatus, name="document_status"), nullable=False, default=DocumentStatus.pendiente)
    extracted_text = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    processed_at = Column(DateTime(timezone=True), nullable=True)

    folder = relationship("Folder", back_populates="documents")