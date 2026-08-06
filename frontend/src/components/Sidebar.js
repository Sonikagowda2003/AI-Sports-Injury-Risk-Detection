import { NavLink, useNavigate } from "react-router-dom";
import { useAuth } from "../context/AuthContext";

export default function Sidebar() {
  const { user, logout } = useAuth();
  const navigate = useNavigate();

  const handleLogout = () => {
    logout();
    navigate("/login");
  };

  return (
    <aside className="sidebar">
      <div className="brand">
        <div className="brand-mark">IR</div>
        <div className="brand-title">
          Injury Risk
          <span>Detection Platform</span>
        </div>
      </div>

      <nav className="nav-links">
        <NavLink to="/dashboard" className={({ isActive }) => `nav-link ${isActive ? "active" : ""}`}>
          Athletes
        </NavLink>
        <NavLink to="/athletes/new" className={({ isActive }) => `nav-link ${isActive ? "active" : ""}`}>
          Add athlete
        </NavLink>
      </nav>

      <div className="sidebar-footer">
        <div className="user-chip">
          <span>{user?.email}</span>
          <span className="role">{user?.role}</span>
        </div>
        <button className="logout-btn" onClick={handleLogout}>
          Log out
        </button>
      </div>
    </aside>
  );
}
