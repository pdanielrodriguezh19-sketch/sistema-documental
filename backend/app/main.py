from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routers import auth, users, repositories, folders, documents, search

app = FastAPI(
    title="Sistema Inteligente de Gestión y Análisis Documental",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(users.router)
app.include_router(repositories.router)
app.include_router(folders.router)
app.include_router(documents.router)
app.include_router(search.router)


@app.get("/")
def health_check():
    return {"status": "ok", "service": "sistema-documental-backend"}