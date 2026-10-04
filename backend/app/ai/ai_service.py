import json

import google.generativeai as genai

from app.config import settings

_configured = False


def _ensure_configured() -> None:
    global _configured
    if not _configured:
        if not settings.ai_api_key:
            raise RuntimeError("AI_API_KEY no está configurada en el .env")
        genai.configure(api_key=settings.ai_api_key)
        _configured = True


def ask_ai(system_prompt: str, user_prompt: str, max_tokens: int = 1024) -> str:
    _ensure_configured()
    model = genai.GenerativeModel(
        model_name=settings.ai_model,
        system_instruction=system_prompt,
    )
    response = model.generate_content(
        user_prompt,
        generation_config=genai.types.GenerationConfig(max_output_tokens=max_tokens),
    )
    return response.text


def ask_ai_json(system_prompt: str, user_prompt: str, max_tokens: int = 1024) -> dict:
    raw = ask_ai(system_prompt, user_prompt, max_tokens=max_tokens)
    raw = raw.strip()

    if raw.startswith("```"):
        raw = raw.strip("`")
        if raw.startswith("json"):
            raw = raw[4:]
        raw = raw.strip()

    return json.loads(raw)


def embed_text(text: str) -> list[float]:
    """Genera el embedding (vector numérico) de un texto, usado para RAG."""
    _ensure_configured()
    result = genai.embed_content(
        model="models/gemini-embedding-001",
        content=text,
        task_type="retrieval_document",
    )
    return result["embedding"]