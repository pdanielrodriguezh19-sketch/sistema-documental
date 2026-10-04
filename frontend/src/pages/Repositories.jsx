import { useState, useEffect } from "react";
import { Link } from "react-router-dom";
import api from "../services/api";

export default function Repositories() {
  const [repos, setRepos] = useState([]);
  const [showForm, setShowForm] = useState(false);
  const [name, setName] = useState("");
  const [editingId, setEditingId] = useState(null);
  const [error, setError] = useState("");

  const load = async () => {
    const { data } = await api.get("/repositories");
    setRepos(data);
  };

  useEffect(() => { load(); }, []);

  const resetForm = () => {
    setShowForm(false);
    setName("");
    setEditingId(null);
    setError("");
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError("");
    try {
      if (editingId) {
        await api.put(`/repositories/${editingId}`, { name });
      } else {
        await api.post("/repositories", { name });
      }
      resetForm();
      load();
    } catch (err) {
      setError(err.response?.data?.detail || "No fue posible guardar el repositorio.");
    }
  };

  const handleEdit = (repo) => {
    setEditingId(repo.id);
    setName(repo.name);
    setShowForm(true);
  };

  const handleDelete = async (id) => {
    if (!confirm("¿Eliminar este repositorio?")) return;
    await api.delete(`/repositories/${id}`);
    load();
  };

  return (
    <div>
      <div className="page-header">
        <div>
          <h1>Repositorios</h1>
          <p style={{ color: "var(--muted)" }}>Espacios donde organizas tus documentos.</p>
        </div>
        <button className="btn btn--primary" onClick={() => setShowForm(true)}>
          + Nuevo repositorio
        </button>
      </div>

      {showForm && (
        <div className="panel" style={{ marginBottom: 20, maxWidth: 400 }}>
          <form onSubmit={handleSubmit}>
            <div className="field">
              <label>Nombre del repositorio</label>
              <input value={name} onChange={(e) => setName(e.target.value)} required />
            </div>
            {error && <div className="error-banner">{error}</div>}
            <div style={{ display: "flex", gap: 8 }}>
              <button type="submit" className="btn btn--primary">
                {editingId ? "Guardar cambios" : "Crear"}
              </button>
              <button type="button" className="btn btn--ghost" onClick={resetForm}>
                Cancelar
              </button>
            </div>
          </form>
        </div>
      )}

      {repos.map((repo) => (
        <div key={repo.id} className="file-card">
          <span className="file-card__tab">Repositorio</span>
          <p className="file-card__title">{repo.name}</p>
          <p className="file-card__meta">
            {repo.document_count ?? 0} documentos
          </p>
          <div className="file-card__actions">
            <Link to={`/documents?repository=${repo.id}`} className="btn btn--ghost">
              Ver documentos
            </Link>
            <button className="btn btn--ghost" onClick={() => handleEdit(repo)}>
              Editar
            </button>
            <button className="btn btn--ghost" onClick={() => handleDelete(repo.id)}>
              Eliminar
            </button>
          </div>
        </div>
      ))}
    </div>
  );
}