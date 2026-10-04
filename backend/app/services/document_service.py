import os
import re
import uuid
from datetime import datetime, timezone

from sqlalchemy.orm import Session

from app.models.document import Document, DocumentStatus
from app.models.processing_log import ProcessingLog, LogStatus
from app.models.category import Category
from app.models.document_category import DocumentCategory
from app.models.ai_result import AIResult
from app.models.document_chunk import DocumentChunk
from app.services.pdf_service import extract_text_from_pdf
from app.services.docx_service import extract_text_from_docx
from app.services.txt_service import extract_text_from_txt
from app.services.chunking_service import split_into_chunks
from app.ai.classifier import classify_document
from app.ai.summarizer import summarize_document
from app.ai.extractor import extract_information
from app.ai.ai_service import embed_text

ALLOWED_EXTENSIONS = {"pdf", "docx", "txt"}
MAX_FILE_SIZE_BYTES = 20 * 1024 * 1024  # 20 MB

FILE_SIGNATURES = {
    "pdf": [b"%PDF"],
    "docx": [b"PK\x03\x04"],
}

STORAGE_ROOT = os.path.join(os.path.dirname(__file__), "..", "..", "..", "documents")


class DocumentValidationError(Exception):
    """Error de validación de archivo (extensión, tamaño, contenido, etc.)."""


def sanitize_filename(filename: str) -> str:
    filename = os.path.basename(filename)
    filename = re.sub(r"[^A-Za-z0-9._-]", "_", filename)
    return filename or "archivo"


def get_extension(filename: str) -> str:
    return filename.rsplit(".", 1)[-1].lower() if "." in filename else ""


def validate_file(filename: str, content: bytes) -> str:
    if not content:
        raise DocumentValidationError("El archivo está vacío.")

    if len(content) > MAX_FILE_SIZE_BYTES:
        raise DocumentValidationError(f"El archivo supera el tamaño máximo permitido ({MAX_FILE_SIZE_BYTES // (1024*1024)} MB).")

    extension = get_extension(filename)
    if extension not in ALLOWED_EXTENSIONS:
        raise DocumentValidationError(f"Extensión '.{extension}' no permitida. Solo se permiten: {', '.join(ALLOWED_EXTENSIONS)}.")

    if extension in FILE_SIGNATURES:
        valid_signature = any(content.startswith(sig) for sig in FILE_SIGNATURES[extension])
        if not valid_signature:
            raise DocumentValidationError("El contenido del archivo no coincide con su extensión (posible archivo corrupto o renombrado).")

    return extension


def save_file_to_disk(repository_id: uuid.UUID, folder_id: uuid.UUID, filename: str, content: bytes) -> str:
    target_dir = os.path.join(STORAGE_ROOT, str(repository_id), str(folder_id))
    os.makedirs(target_dir, exist_ok=True)

    unique_name = f"{uuid.uuid4()}_{filename}"
    file_path = os.path.join(target_dir, unique_name)

    with open(file_path, "wb") as f:
        f.write(content)

    return file_path


def log_event(db: Session, document_id: uuid.UUID | None, status: LogStatus, message: str) -> None:
    log = ProcessingLog(document_id=document_id, status=status, message=message)
    db.add(log)
    db.commit()


def generate_chunks_and_embeddings(db: Session, document: Document) -> None:
    """Divide el texto extraído en fragmentos, genera su embedding y los guarda.
    Si el documento ya tenía fragmentos (reprocesamiento), los reemplaza."""
    db.query(DocumentChunk).filter(DocumentChunk.document_id == document.id).delete()
    db.commit()

    chunks = split_into_chunks(document.extracted_text or "")

    for index, chunk_text in enumerate(chunks):
        embedding = embed_text(chunk_text)
        db.add(DocumentChunk(
            document_id=document.id,
            chunk_index=index,
            content=chunk_text,
            embedding=embedding,
        ))

    db.commit()


def process_document(db: Session, document: Document) -> None:
    """Extrae el texto, clasifica, resume, extrae información y genera fragmentos/embeddings del documento."""
    document.status = DocumentStatus.procesando
    db.commit()

    try:
        if document.file_type == "pdf":
            text = extract_text_from_pdf(document.file_path)
        elif document.file_type == "docx":
            text = extract_text_from_docx(document.file_path)
        elif document.file_type == "txt":
            text = extract_text_from_txt(document.file_path)
        else:
            raise DocumentValidationError(f"Tipo de archivo no soportado: {document.file_type}")

        document.extracted_text = text
        db.commit()
        log_event(db, document.id, LogStatus.info, "Texto extraído correctamente.")
    except Exception as exc:
        document.status = DocumentStatus.error
        db.commit()
        log_event(db, document.id, LogStatus.error, f"Error al extraer texto: {exc}")
        return

    try:
        categoria, confianza = classify_document(document.extracted_text)
        _save_category(db, document.id, categoria, confianza)

        resumen = summarize_document(document.extracted_text)
        datos_extraidos = extract_information(document.extracted_text, categoria)

        _upsert_ai_result(db, document.id, resumen, categoria, datos_extraidos)

        generate_chunks_and_embeddings(db, document)

        log_event(db, document.id, LogStatus.info, f"Procesamiento IA y RAG completos. Categoría: {categoria}.")
    except Exception as exc:
        log_event(db, document.id, LogStatus.error, f"Error en el procesamiento IA: {exc}")

    document.status = DocumentStatus.procesado
    document.processed_at = datetime.now(timezone.utc)
    db.commit()


def _save_category(db: Session, document_id: uuid.UUID, category_name: str, confidence: float) -> None:
    category = db.query(Category).filter(Category.name == category_name).first()
    if not category:
        category = Category(name=category_name)
        db.add(category)
        db.commit()
        db.refresh(category)

    existing = db.query(DocumentCategory).filter(
        DocumentCategory.document_id == document_id, DocumentCategory.category_id == category.id
    ).first()

    if existing:
        existing.confidence = confidence
    else:
        db.add(DocumentCategory(document_id=document_id, category_id=category.id, confidence=confidence))

    db.commit()


def _upsert_ai_result(db: Session, document_id: uuid.UUID, summary: str, classification: str, extracted_data: dict) -> None:
    existing = db.query(AIResult).filter(AIResult.document_id == document_id).first()
    if existing:
        existing.summary = summary
        existing.classification = classification
        existing.extracted_data = extracted_data
    else:
        db.add(AIResult(
            document_id=document_id,
            summary=summary,
            classification=classification,
            extracted_data=extracted_data,
        ))
    db.commit()