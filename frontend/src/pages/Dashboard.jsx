import { useState, useEffect } from "react";
import api from "../services/api";

export default function Dashboard() {
  const [stats, setStats] = useState(null);

  useEffect(() => {
    async function load() {
      const [reposRes, docsRes] = await Promise.all([
        api.get("/repositories"),
        api.get("/documents"),
      ]);
      const docs = docsRes.data;

      const byStatus = {};
      const byType = {};
      docs.forEach((d) => {
        byStatus[d.status] = (byStatus[d.status] || 0) + 1;
        byType[d.file_type] = (byType[d.file_type] || 0) + 1;
      });

      setStats({
        totalRepos: reposRes.data.length,
        totalDocs: docs.length,
        byStatus,
        byType,
        recent: [...docs].sort((a, b) => new Date(b.created_at) - new Date(a.created_at)).slice(0, 5),
      });
    }
    load();
  }, []);

  if (!stats) return <p style={{ color: "var(--muted)" }}>Cargando…</p>;

  const statCard = (label, value, color = "var(--ink)") => (
    <div className="panel" style={{ flex: 1 }}>
      <h3 style={{ color: "var(--muted)", fontWeight: 500, fontSize: 13 }}>{label}</h3>
      <p style={{ fontFamily: "var(--font-display)", fontSize: 32, margin: 0, color }}>
        {value}
      </p>
    </div>
  );

  return (
    <div>
      <h1>Panel</h1>
      <p style={{ color: "var(--muted)" }}>Resumen general de tus repositorios y documentos.</p>

      <div style={{ display: "flex", gap: 16, margin: "24px 0" }}>
        {statCard("Repositorios", stats.totalRepos)}
        {statCard("Documentos", stats.totalDocs)}
        {statCard("Procesados", stats.byStatus.procesado || 0, "var(--accent)")}
        {statCard("Con error", stats.byStatus.error || 0, "var(--danger)")}
      </div>

      <div style={{ display: "flex", gap: 16 }}>
        <div className="panel" style={{ flex: 1 }}>
          <h2>Documentos por formato</h2>
          {Object.entries(stats.byType).map(([tipo, count]) => (
            <div
              key={tipo}
              style={{
                display: "flex",
                justifyContent: "space-between",
                padding: "8px 0",
                borderBottom: "1px solid var(--line)",
                fontSize: 14,
              }}
            >
              <span>{tipo.toUpperCase()}</span>
              <span style={{ color: "var(--muted)" }}>{count}</span>
            </div>
          ))}
        </div>

        <div className="panel" style={{ flex: 2 }}>
          <h2>Últimos documentos cargados</h2>
          {stats.recent.map((d) => (
            <div
              key={d.id}
              style={{
                display: "flex",
                justifyContent: "space-between",
                padding: "10px 0",
                borderBottom: "1px solid var(--line)",
                fontSize: 14,
              }}
            >
              <span>{d.name}</span>
              <span style={{ color: "var(--muted)" }}>
                {d.status} — {new Date(d.created_at).toLocaleString()}
              </span>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}