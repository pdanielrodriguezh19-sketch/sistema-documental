from app.ai.ai_service import ask_ai_json

CATEGORIES = ["Facturas", "Contratos", "Informes"]

SYSTEM_PROMPT = (
    "Eres un clasificador de documentos empresariales. "
    "Debes clasificar el texto del usuario en EXACTAMENTE una de estas categorías: "
    f"{', '.join(CATEGORIES)}. "
    "Responde SOLO con un JSON válido, sin texto adicional, con este formato exacto: "
    '{"categoria": "<una de las categorías>", "confianza": <número entre 0 y 1>}'
)


def classify_document(text: str) -> tuple[str, float]:
    """Clasifica el texto y retorna (categoria, confianza). Si la IA falla o responde algo inesperado, retorna ('Informes', 0.0) como categoría por defecto."""
    if not text or not text.strip():
        return "Informes", 0.0

    # Truncamos para no enviar textos gigantes innecesariamente
    excerpt = text[:6000]

    try:
        result = ask_ai_json(SYSTEM_PROMPT, excerpt)
        categoria = result.get("categoria", "Informes")
        confianza = float(result.get("confianza", 0.0))

        if categoria not in CATEGORIES:
            categoria = "Informes"

        return categoria, max(0.0, min(1.0, confianza))
    except Exception:
        return "Informes", 0.0