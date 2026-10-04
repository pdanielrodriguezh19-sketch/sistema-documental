import { useState } from "react";
import { useNavigate, Link } from "react-router-dom";
import { useAuth } from "../context/AuthContext";

export default function Login() {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);
  const { login } = useAuth();
  const navigate = useNavigate();

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError("");
    setLoading(true);
    try {
      await login(email, password);
      navigate("/");
    } catch (err) {
      setError(err.response?.data?.detail || "No fue posible iniciar sesión.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="auth-layout">
      <div className="panel" style={{ width: 360 }}>
        <h1>Gestión Documental</h1>
        <p style={{ color: "var(--muted)", marginBottom: 24 }}>
          Ingresa para consultar y analizar tus documentos.
        </p>
        <form onSubmit={handleSubmit}>
          <div className="field">
            <label>Correo electrónico</label>
            <input
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              required
            />
          </div>
          <div className="field">
            <label>Contraseña</label>
            <input
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              required
            />
          </div>
          {error && <div className="error-banner">{error}</div>}
          <button type="submit" className="btn btn--primary" disabled={loading} style={{ width: "100%" }}>
            {loading ? "Ingresando…" : "Ingresar"}
          </button>
        </form>
        <p style={{ marginTop: 16, fontSize: 13 }}>
          ¿No tienes cuenta? <Link to="/register">Regístrate</Link>
        </p>
      </div>
    </div>
  );
}