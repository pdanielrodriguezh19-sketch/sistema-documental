import { NavLink, useNavigate } from "react-router-dom";
import { useAuth } from "../context/AuthContext";

export default function Layout({ children }) {
  const { logout } = useAuth();
  const navigate = useNavigate();

  const handleLogout = () => {
    logout();
    navigate("/login");
  };

  const linkClass = ({ isActive }) =>
    isActive ? "nav-link nav-link--active" : "nav-link";

  return (
    <div className="app-shell">
      <aside className="sidebar">
        <div className="sidebar__brand">Gestión Documental</div>
        <nav className="sidebar__nav">
          <NavLink to="/" end className={linkClass}>Panel</NavLink>
          <NavLink to="/repositories" className={linkClass}>Repositorios</NavLink>
          <NavLink to="/documents" className={linkClass}>Documentos</NavLink>
          <NavLink to="/search" className={linkClass}>Buscar</NavLink>
        </nav>
        <div className="sidebar__footer">
          <button className="btn btn--ghost" onClick={handleLogout}>
            Cerrar sesión
          </button>
        </div>
      </aside>
      <main className="main">{children}</main>
    </div>
  );
}