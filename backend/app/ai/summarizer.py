from app.ai.ai_service import ask_ai

SYSTEM_PROMPT = (
    "Eres un asistente que resume documentos empresariales en español, de forma clara y comprensible. "
    "Genera un resumen de máximo 5 líneas que capture el propósito y los puntos clave del documento. "
    "No inventes información que no esté en el texto. Responde solo con el resumen, sin encabezados ni comentarios."
)


def summarize_document(text: str) -> str:
    """Genera un resumen del texto. Si falla o el texto está vacío, retorna un mensaje indicándolo."""
    if not text or not text.strip():
        return "No hay texto suficiente para generar un resumen."

    excerpt = text[:8000]

    try:
        return ask_ai(SYSTEM_PROMPT, excerpt, max_tokens=2000).strip()
    except Exception as exc:
        return f"No se pudo generar el resumen automáticamente ({exc})."