from fastapi import Header, HTTPException
from app.config import settings


def verify_service_key(x_service_key: str = Header(...)):
    if x_service_key != settings.n8n_service_key:
        raise HTTPException(status_code=401, detail="Service key inválida")
    return True