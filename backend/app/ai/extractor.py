from app.ai.ai_service import ask_ai_json

# Campos esperados por categoría, definidos en la Fase 1
FIELDS_BY_CATEGORY = {
    "Facturas": ["numero", "fecha", "proveedor", "cliente", "subtotal", "impuestos", "total"],
    "Contratos": ["partes", "fecha", "objeto", "duracion", "valor", "obligaciones"],
    "Informes": ["titulo", "autor", "fecha", "area", "resumen", "conclusiones", "palabras_clave"],
}


def extract_information(text: str, category: str) -> dict:
    """Extrae los campos estructurados correspondientes a la categoría del documento.
    Si un campo no aparece en el texto, su valor debe ser null (no se inventa información)."""
    fields = FIELDS_BY_CATEGORY.get(category, FIELDS_BY_CATEGORY["Informes"])

    if not text or not text.strip():
        return {field: None for field in fields}

    fields_json_example = ", ".join(f'"{f}": null' for f in fields)

    system_prompt = (
        f"Eres un extractor de información de documentos tipo '{category}'. "
        f"A partir del texto del usuario, extrae ÚNICAMENTE estos campos: {', '.join(fields)}. "
        "Si un campo no aparece explícitamente en el texto, su valor debe ser null. "
        "NUNCA inventes datos que no estén en el texto. "
        f'Responde SOLO con un JSON válido con esta forma exacta: {{{fields_json_example}}}'
    )

    excerpt = text[:8000]

    try:
        result = ask_ai_json(system_prompt, excerpt, max_tokens=2000)
        return {field: result.get(field) for field in fields}
    except Exception:
        return {field: None for field in fields}