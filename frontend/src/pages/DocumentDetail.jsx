import { useState, useEffect } from "react";
import { useParams, Link } from "react-router-dom";
import api from "../services/api";

export default function DocumentDetail() {
  const { id } = useParams();
  const [doc, setDoc] = useState(null);

  useEffect(() => {
    api.get(`/documents/${id}`).then((res) => setDoc(res.data));
  }, [id]);

  if (!doc) return <p style={{ color: "var(--muted)" }}>Cargando…</p>;

  return (
    <div>
      <div className="page-header">
        <div>
          <h1>{doc.name}</h1>
          <p style={{ color: "var(--muted)" }}>
            {doc.file_type?.toUpperCase()} — Estado: {doc.status}
          </p>
        </div>
        <div style={{ display: "flex", gap: 8 }}>
          <a href={`${api.defaults.baseURL}/documents/${id}/download`} className="btn btn--ghost">
            Descargar
          </a>
          <Link to={`/chat/${id}`} className="btn btn--primary">
            Preguntar a la IA
          </Link>
        </div>
      </div>

      {doc.ai_result ? (
        <>
          <div className="panel" style={{ marginBottom: 16 }}>
            <h2>Clasificación</h2>
            <p>{doc.ai_result.category} ({Math.round((doc.ai_result.confidence || 0) * 100)}% confianza)</p>
          </div>
          <div className="panel" style={{ marginBottom: 16 }}>
            <h2>Resumen</h2>
            <p>{doc.ai_result.summary}</p>
          </div>
          <div className="panel">
            <h2>Datos extraídos</h2>
            <pre style={{ fontFamily: "monospace", fontSize: 13, whiteSpace: "pre-wrap" }}>
              {JSON.stringify(doc.ai_result.extracted_data, null, 2)}
            </pre>
          </div>
        </>
      ) : (
        <div className="panel">
          <p style={{ color: "var(--muted)" }}>Este documento aún no ha sido procesado por la IA.</p>
        </div>
      )}
    </div>
  );
}