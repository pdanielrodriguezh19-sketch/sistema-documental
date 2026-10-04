import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.repository import Repository
from app.models.user import User
from app.schemas.repository import RepositoryCreate, RepositoryOut
from app.dependencies import get_current_user

router = APIRouter(prefix="/repositories", tags=["Repositorios"])


@router.post("", response_model=RepositoryOut, status_code=status.HTTP_201_CREATED)
def create_repository(
    repo_in: RepositoryCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    repo = Repository(name=repo_in.name, description=repo_in.description, owner_id=current_user.id)
    db.add(repo)
    db.commit()
    db.refresh(repo)
    return repo


@router.get("", response_model=list[RepositoryOut])
def list_repositories(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return db.query(Repository).filter(Repository.owner_id == current_user.id).all()


@router.put("/{repository_id}", response_model=RepositoryOut)
def update_repository(
    repository_id: uuid.UUID,
    repo_in: RepositoryCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    repo = db.query(Repository).filter(Repository.id == repository_id, Repository.owner_id == current_user.id).first()
    if not repo:
        raise HTTPException(status_code=404, detail="Repositorio no encontrado")

    repo.name = repo_in.name
    repo.description = repo_in.description
    db.commit()
    db.refresh(repo)
    return repo


@router.delete("/{repository_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_repository(
    repository_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    repo = db.query(Repository).filter(Repository.id == repository_id, Repository.owner_id == current_user.id).first()
    if not repo:
        raise HTTPException(status_code=404, detail="Repositorio no encontrado")

    db.delete(repo)
    db.commit()