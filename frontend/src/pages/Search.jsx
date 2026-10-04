import { useState } from "react";
import { Link } from "react-router-dom";
import api from "../services/api";

export default function Search() {
  const [query, setQuery] = useState("");
  const [mode, setMode] = useState("simple");
  const [results, setResults] = useState(null);
  const [loading, setLoading] = useState(false);

  const handleSearch = async (e) => {
    e.preventDefault();
    setLoading(true);
    try {
      if (mode === "simple") {
        const { data } = await api.get("/search", { params: { q: query } });
        setResults(data);
      } else {
        const { data } = await api.post("/search/ask", { question: query });
        setResults(data);
      }
    } finally {
      setLoading(false);
    }
  };

  return (
    <div>
      <h1>Buscar</h1>
      <p style={{ color: "var(--muted)" }}>Busca por texto exacto o pregunta con lenguaje natural.</p>

      <form onSubmit={handleSearch} className="panel" style={{ display: "flex", gap: 8, marginBottom: 20 }}>
        <input
          style={{ flex: 1, padding: "9px 11px", border: "1px solid var(--line)" }}
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          placeholder="Escribe tu búsqueda…"
          required
        />
        <select value={mode} onChange={(e) => setMode(e.target.value)} style={{ border: "1px solid var(--line)" }}>
          <option value="simple">Texto simple</option>
          <option value="semantic">Pregunta (IA)</option>
        </select>
        <button type="submit" className="btn btn--primary" disabled={loading}>
          {loading ? "Buscando…" : "Buscar"}
        </button>
      </form>

      {mode === "simple" && results?.map((doc) => (
        <div key={doc.id} className="file-card">
          <p className="file-card__title">{doc.name}</p>
          <p className="file-card__meta">{doc.snippet}</p>
          <Link to={`/documents/${doc.id}`} className="btn btn--ghost">Ver documento</Link>
        </div>
      ))}

      {mode === "semantic" && results && (
        <div className="panel">
          <p>{results.answer}</p>
          {results.sources?.length > 0 && (
            <>
              <h3>Fuentes</h3>
              {results.sources.map((s, i) => (
                <p key={i} className="file-card__meta">— {s.document_name}</p>
              ))}
            </>
          )}
        </div>
      )}
    </div>
  );
}