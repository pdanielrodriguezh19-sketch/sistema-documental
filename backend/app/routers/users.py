from fastapi import APIRouter, Depends

from app.models.user import User
from app.schemas.user import UserOut
from app.dependencies import get_current_user

router = APIRouter(prefix="/users", tags=["Usuarios"])


@router.get("/me", response_model=UserOut)
def read_current_user(current_user: User = Depends(get_current_user)):
    """Endpoint protegido: retorna el usuario autenticado. Sirve para probar el JWT."""
    return current_user