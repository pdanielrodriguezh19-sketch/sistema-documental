import { useState } from "react";
import { useParams } from "react-router-dom";
import api from "../services/api";

export default function Chat() {
  const { documentId } = useParams();
  const [messages, setMessages] = useState([]);
  const [question, setQuestion] = useState("");
  const [loading, setLoading] = useState(false);

  const handleAsk = async (e) => {
    e.preventDefault();
    const userMessage = { role: "user", text: question };
    setMessages((prev) => [...prev, userMessage]);
    setQuestion("");
    setLoading(true);
    try {
      const { data } = await api.post(`/documents/${documentId}/ask`, { question });
      setMessages((prev) => [...prev, { role: "ai", text: data.answer, sources: data.sources }]);
    } catch (err) {
      setMessages((prev) => [...prev, { role: "ai", text: "Ocurrió un error al responder." }]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={{ display: "flex", flexDirection: "column", height: "calc(100vh - 64px)" }}>
      <h1>Preguntas sobre el documento</h1>

      <div className="panel" style={{ flex: 1, overflowY: "auto", marginBottom: 16 }}>
        {messages.length === 0 && (
          <p style={{ color: "var(--muted)" }}>Escribe una pregunta sobre este documento.</p>
        )}
        {messages.map((m, i) => (
          <div key={i} style={{ marginBottom: 12 }}>
            <strong style={{ color: m.role === "user" ? "var(--ink)" : "var(--accent-ink)" }}>
              {m.role === "user" ? "Tú" : "Asistente"}
            </strong>
            <p style={{ margin: "4px 0" }}>{m.text}</p>
            {m.sources?.map((s, j) => (
              <p key={j} className="file-card__meta">Fuente: {s.document_name}</p>
            ))}
          </div>
        ))}
      </div>

      <form onSubmit={handleAsk} style={{ display: "flex", gap: 8 }}>
        <input
          style={{ flex: 1, padding: "9px 11px", border: "1px solid var(--line)" }}
          value={question}
          onChange={(e) => setQuestion(e.target.value)}
          placeholder="Escribe tu pregunta…"
          required
        />
        <button type="submit" className="btn btn--primary" disabled={loading}>
          {loading ? "Enviando…" : "Enviar"}
        </button>
      </form>
    </div>
  );
}