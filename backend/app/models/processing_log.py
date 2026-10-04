import uuid
import enum

from sqlalchemy import Column, Text, DateTime, ForeignKey, Enum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func

from app.database import Base


class LogStatus(str, enum.Enum):
    info = "info"
    warning = "warning"
    error = "error"


class ProcessingLog(Base):
    __tablename__ = "processing_logs"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    document_id = Column(UUID(as_uuid=True), ForeignKey("documents.id", ondelete="CASCADE"), nullable=True)
    status = Column(Enum(LogStatus, name="log_status"), nullable=False)
    message = Column(Text, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())