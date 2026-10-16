import { useState } from "react";
import { useAuth } from "./context/AuthContext";
import Login from "./pages/Login";
import Navbar from "./components/Navbar";
import Sidebar from "./components/Sidebar";
import Dashboard from "./pages/Dashboard";
import Stagiaires from "./pages/Stagiaires";
import Tuteurs from "./pages/Tuteurs";
import Stages from "./pages/Stages";
import Services from "./pages/Services";
import Utilisateurs from "./pages/Utilisateurs";
import Documents from "./pages/Documents";
import MonCompte from "./pages/MonCompte";
import PremiereConnexion from "./pages/PremiereConnexion";

function App() {
  const { user, can, accessReady } = useAuth();
  const [activeTab, setActiveTab] = useState("dashboard");
  const [sidebarOpen, setSidebarOpen] = useState(false); // mobile : menu ouvert par-dessus
  const [collapsed, setCollapsed] = useState(() => {
    try {
      return localStorage.getItem("sidebar_collapsed") === "1";
    } catch {
      return false;
    }
  }); // ordinateur : barre réduite aux icônes

  if (!user) {
    return <Login />;
  }

  // Compte créé avec un mot de passe provisoire : identité + nouveau mot de passe d'abord
  if (user.doit_changer_mdp) {
    return <PremiereConnexion />;
  }

  if (!accessReady) {
    return (
      <div className="app-loading">
        <span className="spinner spinner-dark" />
        Chargement de votre espace…
      </div>
    );
  }

  // Si l'onglet demandé n'est pas autorisé, on affiche le premier onglet accessible
  const tabs = ["dashboard", "stagiaires", "tuteurs", "stages", "services", "utilisateurs", "documents", "compte"];
  // Titre affiché dans la barre du haut pour chaque onglet
  const titles = {
    dashboard: "Tableau de bord",
    stagiaires: user.role === "TUTEUR" ? "Mes Stagiaires" : "Gestion des Stagiaires",
    tuteurs: "Liste des Encadrants",
    stages: "Affectations & Stages",
    services: "Services & Établissements",
    utilisateurs: "Gestion des Utilisateurs",
    documents: "Documents & Attestations",
    compte: "Mon compte",
  };
  const currentTab = can(activeTab) ? activeTab : tabs.find((t) => can(t));

  // Le bouton menu ouvre le tiroir sur mobile, et réduit/déplie la barre sur ordinateur
  const handleMenuClick = () => {
    if (window.matchMedia("(max-width: 960px)").matches) {
      setSidebarOpen(true);
      return;
    }
    const next = !collapsed;
    setCollapsed(next);
    try {
      localStorage.setItem("sidebar_collapsed", next ? "1" : "0");
    } catch {
      // stockage indisponible : l'état ne sera simplement pas mémorisé
    }
  };

  return (
    <div className="app-shell">
      <Sidebar
        activeTab={currentTab}
        setActiveTab={setActiveTab}
        open={sidebarOpen}
        collapsed={collapsed}
        onClose={() => setSidebarOpen(false)}
      />

      <div className="app-main">
        <Navbar
          onMenuClick={handleMenuClick}
          collapsed={collapsed}
          onAccountClick={() => setActiveTab("compte")}
          title={titles[currentTab]}
        />

        <main className="app-content">
          {currentTab === "dashboard" && <Dashboard />}
          {currentTab === "stagiaires" && <Stagiaires />}
          {currentTab === "tuteurs" && <Tuteurs />}
          {currentTab === "stages" && <Stages />}
          {currentTab === "services" && <Services />}
          {currentTab === "utilisateurs" && <Utilisateurs />}
          {currentTab === "documents" && <Documents />}
          {currentTab === "compte" && <MonCompte />}
        </main>
      </div>
    </div>
  );
}

export default App;
