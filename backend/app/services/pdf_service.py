import fitz  # PyMuPDF


def extract_text_from_pdf(file_path: str) -> str:
    """Extrae todo el texto de un PDF, página por página."""
    text_parts = []
    with fitz.open(file_path) as pdf:
        for page in pdf:
            text_parts.append(page.get_text())
    return "\n".join(text_parts).strip()