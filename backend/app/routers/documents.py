import uuid

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, status
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from app.schemas.rag import AskRequest, AskResponse
from app.ai.rag import answer_question

from app.database import get_db
from app.models.document import Document
from app.models.folder import Folder
from app.models.repository import Repository
from app.models.ai_result import AIResult
from app.models.user import User
from app.models.processing_log import LogStatus
from app.schemas.document import DocumentOut, DocumentDetailOut
from app.dependencies import get_current_user
from app.utils.service_auth import verify_service_key
from app.services.document_service import (
    validate_file,
    save_file_to_disk,
    process_document,
    log_event,
    sanitize_filename,
    DocumentValidationError,
)

router = APIRouter(prefix="/documents", tags=["Documentos"])


def _get_owned_document(db: Session, document_id: uuid.UUID, user: User) -> Document:
    doc = (
        db.query(Document)
        .join(Folder)
        .join(Repository)
        .filter(Document.id == document_id, Repository.owner_id == user.id)
        .first()
    )
    if not doc:
        raise HTTPException(status_code=404, detail="Documento no encontrado")
    return doc


@router.post("/upload", response_model=DocumentOut, status_code=status.HTTP_201_CREATED)
async def upload_document(
    folder_id: uuid.UUID = Form(...),
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    folder = db.query(Folder).join(Repository).filter(
        Folder.id == folder_id, Repository.owner_id == current_user.id
    ).first()
    if not folder:
        raise HTTPException(status_code=404, detail="Carpeta no encontrada")

    safe_filename = sanitize_filename(file.filename or "archivo")
    content = await file.read()

    try:
        extension = validate_file(safe_filename, content)
    except DocumentValidationError as exc:
        log_event(db, None, LogStatus.error, f"Carga rechazada ({safe_filename}): {exc}")
        raise HTTPException(status_code=400, detail=str(exc))

    file_path = save_file_to_disk(folder.repository_id, folder.id, safe_filename, content)

    document = Document(
        name=safe_filename,
        filename=safe_filename,
        file_type=extension,
        file_path=file_path,
        size=len(content),
        folder_id=folder.id,
        uploaded_by=current_user.id,
    )
    db.add(document)
    db.commit()
    db.refresh(document)

    process_document(db, document)
    db.refresh(document)

    return document


@router.post("/upload-service", response_model=DocumentOut, status_code=status.HTTP_201_CREATED)
async def upload_document_service(
    folder_id: uuid.UUID = Form(...),
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    _: bool = Depends(verify_service_key),
):
    """Igual que /upload, pero para automatizaciones (n8n): no requiere JWT de usuario.
    El 'dueño' del documento se infiere del dueño del repositorio al que pertenece la carpeta."""
    folder = db.query(Folder).join(Repository).filter(Folder.id == folder_id).first()
    if not folder:
        raise HTTPException(status_code=404, detail="Carpeta no encontrada")

    safe_filename = sanitize_filename(file.filename or "archivo")
    content = await file.read()

    try:
        extension = validate_file(safe_filename, content)
    except DocumentValidationError as exc:
        log_event(db, None, LogStatus.error, f"Carga rechazada ({safe_filename}): {exc}")
        raise HTTPException(status_code=400, detail=str(exc))

    file_path = save_file_to_disk(folder.repository_id, folder.id, safe_filename, content)

    document = Document(
        name=safe_filename,
        filename=safe_filename,
        file_type=extension,
        file_path=file_path,
        size=len(content),
        folder_id=folder.id,
        uploaded_by=folder.repository.owner_id,
    )
    db.add(document)
    db.commit()
    db.refresh(document)

    process_document(db, document)
    db.refresh(document)

    return document


@router.get("", response_model=list[DocumentOut])
def list_documents(
    folder_id: uuid.UUID | None = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    query = db.query(Document).join(Folder).join(Repository).filter(Repository.owner_id == current_user.id)
    if folder_id:
        query = query.filter(Document.folder_id == folder_id)
    return query.all()


@router.get("/{document_id}", response_model=DocumentDetailOut)
def get_document(
    document_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    doc = _get_owned_document(db, document_id, current_user)
    ai_result = db.query(AIResult).filter(AIResult.document_id == doc.id).first()

    result = DocumentDetailOut.model_validate(doc)
    if ai_result:
        result.ai_result = ai_result
    return result


@router.get("/{document_id}/download")
def download_document(
    document_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    doc = _get_owned_document(db, document_id, current_user)
    return FileResponse(path=doc.file_path, filename=doc.filename)


@router.delete("/{document_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_document(
    document_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    doc = _get_owned_document(db, document_id, current_user)
    db.delete(doc)
    db.commit()


@router.post("/{document_id}/process", response_model=DocumentOut)
def reprocess_document(
    document_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Vuelve a ejecutar el pipeline completo (extracción + IA) sobre un documento ya subido."""
    doc = _get_owned_document(db, document_id, current_user)
    process_document(db, doc)
    db.refresh(doc)
    return doc

@router.post("/{document_id}/ask", response_model=AskResponse)
def ask_about_document(
    document_id: uuid.UUID,
    request: AskRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Responde una pregunta basada únicamente en el contenido de ESE documento."""
    _get_owned_document(db, document_id, current_user)  # valida que el documento exista y sea del usuario
    answer, sources = answer_question(db, request.question, current_user.id, document_id=document_id)
    return AskResponse(answer=answer, sources=sources)