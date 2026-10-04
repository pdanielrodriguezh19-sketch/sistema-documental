import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.folder import Folder
from app.models.repository import Repository
from app.models.user import User
from app.schemas.folder import FolderCreate, FolderOut
from app.dependencies import get_current_user

router = APIRouter(prefix="/folders", tags=["Carpetas"])


@router.post("", response_model=FolderOut, status_code=status.HTTP_201_CREATED)
def create_folder(
    folder_in: FolderCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    repo = db.query(Repository).filter(
        Repository.id == folder_in.repository_id, Repository.owner_id == current_user.id
    ).first()
    if not repo:
        raise HTTPException(status_code=404, detail="Repositorio no encontrado")

    folder = Folder(name=folder_in.name, repository_id=folder_in.repository_id, parent_id=folder_in.parent_id)
    db.add(folder)
    db.commit()
    db.refresh(folder)
    return folder


@router.get("", response_model=list[FolderOut])
def list_folders(
    repository_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    repo = db.query(Repository).filter(
        Repository.id == repository_id, Repository.owner_id == current_user.id
    ).first()
    if not repo:
        raise HTTPException(status_code=404, detail="Repositorio no encontrado")

    return db.query(Folder).filter(Folder.repository_id == repository_id).all()


@router.delete("/{folder_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_folder(
    folder_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    folder = db.query(Folder).join(Repository).filter(
        Folder.id == folder_id, Repository.owner_id == current_user.id
    ).first()
    if not folder:
        raise HTTPException(status_code=404, detail="Carpeta no encontrada")

    db.delete(folder)
    db.commit()