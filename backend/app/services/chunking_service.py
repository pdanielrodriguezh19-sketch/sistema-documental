def split_into_chunks(text: str, chunk_size: int = 800, overlap: int = 150) -> list[str]:
    """Divide el texto en fragmentos de aproximadamente chunk_size caracteres,
    con overlap caracteres de solapamiento entre fragmentos consecutivos,
    cortando en espacios para no partir palabras a la mitad."""
    text = text.strip()
    if not text:
        return []

    if len(text) <= chunk_size:
        return [text]

    chunks = []
    start = 0
    while start < len(text):
        end = start + chunk_size

        if end < len(text):
            last_space = text.rfind(" ", start, end)
            if last_space > start:
                end = last_space

        chunk = text[start:end].strip()
        if chunk:
            chunks.append(chunk)

        start = end - overlap
        if start <= 0:
            start = end

    return chunks