import { useAuth } from "../context/AuthContext";
import Avatar from "./Avatar";
import Icon from "./Icon";

function Navbar({ onMenuClick, collapsed, onAccountClick, title }) {
  const { user, logout } = useAuth();

  if (!user) return null;

  return (
    <header className="topbar">
      <button
        className="btn btn-ghost btn-icon topbar-menu"
        onClick={onMenuClick}
        aria-label={collapsed ? "Déplier le menu" : "Réduire le menu"}
        title={collapsed ? "Déplier le menu" : "Réduire le menu"}
      >
        <Icon name="menu" size={20} />
      </button>

      {/* Titre de la page affichée */}
      <h1 className="topbar-title">{title}</h1>

      <div className="topbar-right">
        <button
          type="button"
          className="user-chip user-chip-button"
          onClick={onAccountClick}
          title="Mon compte"
        >
          <Avatar
            key={user.photo || "none"}
            src={user.photo}
            prenom={user.prenom}
            nom={user.nom}
            size={34}
            online
          />
          <div className="user-chip-info">
            <span className="user-chip-name">
              {user.prenom} {user.nom}
            </span>
            <span className="user-chip-role">{user.role}</span>
          </div>
        </button>

        <button
          onClick={logout}
          className="btn btn-danger-ghost btn-icon"
          title="Déconnexion"
          aria-label="Déconnexion"
        >
          <Icon name="logout" size={18} />
        </button>
      </div>
    </header>
  );
}

export default Navbar;
