import { useState, useEffect } from "react";
import { Link, useSearchParams } from "react-router-dom";
import api from "../services/api";

export default function Documents() {
  const [searchParams] = useSearchParams();
  const repositoryId = searchParams.get("repository");

  const [docs, setDocs] = useState([]);
  const [file, setFile] = useState(null);
  const [uploading, setUploading] = useState(false);
  const [error, setError] = useState("");

  const load = async () => {
    const { data } = await api.get("/documents", {
      params: repositoryId ? { repository_id: repositoryId } : {},
    });
    setDocs(data);
  };

  useEffect(() => { load(); }, [repositoryId]);

  const handleUpload = async (e) => {
    e.preventDefault();
    if (!file) return;
    setError("");
    setUploading(true);
    try {
      const formData = new FormData();
      formData.append("file", file);
      if (repositoryId) formData.append("repository_id", repositoryId);
      await api.post("/documents/upload", formData, {
        headers: { "Content-Type": "multipart/form-data" },
      });
      setFile(null);
      load();
    } catch (err) {
      setError(err.response?.data?.detail || "No fue posible subir el documento.");
    } finally {
      setUploading(false);
    }
  };

  const handleProcess = async (id) => {
    await api.post(`/documents/${id}/process`);
    load();
  };

  const handleDelete = async (id) => {
    if (!confirm("¿Eliminar este documento?")) return;
    await api.delete(`/documents/${id}`);
    load();
  };

  return (
    <div>
      <div className="page-header">
        <div>
          <h1>Documentos</h1>
          <p style={{ color: "var(--muted)" }}>Carga, procesa y consulta tus documentos.</p>
        </div>
      </div>

      <form onSubmit={handleUpload} className="panel" style={{ marginBottom: 20, display: "flex", gap: 12, alignItems: "center" }}>
        <input type="file" onChange={(e) => setFile(e.target.files[0])} />
        <button type="submit" className="btn btn--primary" disabled={uploading || !file}>
          {uploading ? "Subiendo…" : "Subir documento"}
        </button>
      </form>
      {error && <div className="error-banner">{error}</div>}

      {docs.map((doc) => (
        <div key={doc.id} className="file-card">
          <span className={`file-card__tab file-card__tab--${doc.status}`}>{doc.status}</span>
          <p className="file-card__title">{doc.name}</p>
          <p className="file-card__meta">
            {doc.file_type?.toUpperCase()} — {new Date(doc.created_at).toLocaleDateString()}
          </p>
          <div className="file-card__actions">
            <Link to={`/documents/${doc.id}`} className="btn btn--ghost">Ver detalle</Link>
            {doc.status !== "procesado" && (
              <button className="btn btn--ghost" onClick={() => handleProcess(doc.id)}>
                Procesar
              </button>
            )}
            <button className="btn btn--ghost" onClick={() => handleDelete(doc.id)}>
              Eliminar
            </button>
          </div>
        </div>
      ))}
    </div>
  );
}