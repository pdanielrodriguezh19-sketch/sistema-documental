def extract_text_from_txt(file_path: str) -> str:
    """Lee un archivo de texto plano, intentando UTF-8 y cayendo a latin-1 si falla."""
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            return f.read().strip()
    except UnicodeDecodeError:
        with open(file_path, "r", encoding="latin-1") as f:
            return f.read().strip()