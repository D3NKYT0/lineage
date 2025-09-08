import React, { useState } from "react";
import { subscribeUserToPush, unsubscribeUserFromPush } from "./push";
import "./App.css";
import UserSection from "./UserSection";
import ServerSection from "./ServerSection";
import SearchSection from "./SearchSection";
import GameSection from "./GameSection";
import MetricsSection from "./MetricsSection";
import AdminSection from "./AdminSection";
import PushSection from "./PushSection";
import { FaUser, FaServer, FaSearch, FaGamepad, FaChartBar, FaCogs, FaBell, FaSignOutAlt } from "react-icons/fa";

// Error Boundary Component
class ErrorBoundary extends React.Component {
  constructor(props) {
    super(props);
    this.state = { hasError: false, error: null };
  }

  static getDerivedStateFromError(error) {
    return { hasError: true, error };
  }

  componentDidCatch(error, errorInfo) {
    console.error("Erro capturado pelo ErrorBoundary:", error, errorInfo);
  }

  render() {
    if (this.state.hasError) {
      return (
        <div style={{ padding: "20px", color: "red", textAlign: "center" }}>
          <h2>Algo deu errado!</h2>
          <p>Erro: {this.state.error?.message}</p>
          <button onClick={() => window.location.reload()}>Recarregar</button>
        </div>
      );
    }

    return this.props.children;
  }
}

const SECTIONS = [
  { key: "user", label: "Usuário", icon: <FaUser /> },
  { key: "server", label: "Servidor", icon: <FaServer /> },
  { key: "search", label: "Busca", icon: <FaSearch /> },
  { key: "game", label: "Jogo", icon: <FaGamepad /> },
  { key: "metrics", label: "Métricas", icon: <FaChartBar /> },
  { key: "admin", label: "Administração", icon: <FaCogs /> },
  { key: "push", label: "Push", icon: <FaBell /> },
];

function SectionPlaceholder({ section }) {
  return (
    <div className="section-placeholder">
      <h2>{section.label}</h2>
      <p>Funcionalidade "{section.label}" em construção.</p>
    </div>
  );
}

export default function App() {
  console.log("App component iniciando...");
  
  const [permission, setPermission] = useState(Notification.permission);
  const [subscribed, setSubscribed] = useState(false);
  const [token, setToken] = useState(localStorage.getItem("jwt_token") || "");
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [loginError, setLoginError] = useState("");
  const [loading, setLoading] = useState(false);
  const [pushError, setPushError] = useState("");
  const [activeSection, setActiveSection] = useState(SECTIONS[0].key);
  const [sidebarExpanded, setSidebarExpanded] = useState(() => {
    const saved = localStorage.getItem('sidebar_expanded');
    return saved !== null ? JSON.parse(saved) : true;
  });

  console.log("Estado inicial:", { token: !!token, activeSection });

  const toggleSidebar = () => {
    const newState = !sidebarExpanded;
    setSidebarExpanded(newState);
    localStorage.setItem('sidebar_expanded', JSON.stringify(newState));
  };

  const handleLogin = async (e) => {
    e.preventDefault();
    setLoading(true);
    setLoginError("");
    try {
      const res = await fetch("/api/v1/auth/login/", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ username, password })
      });
      const data = await res.json();
      if (res.ok && data.access) {
        setToken(data.access);
        localStorage.setItem("jwt_token", data.access);
      } else {
        setLoginError(data.detail || "Usuário ou senha inválidos");
      }
    } catch (err) {
      setLoginError("Erro ao conectar ao servidor");
    }
    setLoading(false);
  };

  const handleSubscribe = async () => {
    console.log("Clicou em Ativar Push");
    setPushError("");
    const result = await subscribeUserToPush(token);
    console.log("Resultado subscribeUserToPush:", result);
    if (result && result.success) {
      setSubscribed(true);
      setPermission("granted");
    } else if (result && result.error) {
      setPushError(result.error);
    }
  };

  const handleUnsubscribe = async () => {
    if (!('serviceWorker' in navigator)) return;
    const registration = await navigator.serviceWorker.ready;
    const subscription = await registration.pushManager.getSubscription();
    if (subscription) {
      await subscription.unsubscribe();
      await unsubscribeUserFromPush(token, subscription);
      setSubscribed(false);
      setPermission(Notification.permission);
    }
  };

  const handleLogout = () => {
    setToken("");
    localStorage.removeItem("jwt_token");
    setSubscribed(false);
    setUsername("");
    setPassword("");
  };

  console.log("Renderizando App, token:", !!token);

  if (!token) {
    console.log("Renderizando tela de login");
    return (
      <ErrorBoundary>
        <div className="pwa-container">
          <div className="login-content">
            <div className="login-info">
              <img src="/static/pwa/icons/logo.png" alt="Logo" className="logo" />
              <h1>Login</h1>
              <p className="install-tip">
                Acesse sua conta para gerenciar notificações e configurações do sistema.
              </p>
            </div>
            <div className="login-form">
              <form onSubmit={handleLogin}>
                <input
                  type="text"
                  placeholder="Usuário"
                  value={username}
                  onChange={e => setUsername(e.target.value)}
                  className="input"
                  autoFocus
                  required
                />
                <input
                  type="password"
                  placeholder="Senha"
                  value={password}
                  onChange={e => setPassword(e.target.value)}
                  className="input"
                  required
                />
                <button className="btn-primary" type="submit" disabled={loading}>
                  {loading ? "Entrando..." : "Entrar"}
                </button>
              </form>
              {loginError && <p className="error">{loginError}</p>}
            </div>
          </div>
        </div>
      </ErrorBoundary>
    );
  }

  // Menu/dashboard principal
  console.log("Renderizando dashboard principal");
  return (
    <ErrorBoundary>
      <div className="pwa-root">
        <aside className={`sidebar ${sidebarExpanded ? 'expanded' : 'collapsed'}`}>
          <div className="sidebar-header">
            <div className="sidebar-logo">
              <img src="/static/pwa/icons/logo.png" alt="Logo" className="logo" />
            </div>
            <button className="sidebar-toggle" onClick={toggleSidebar} title={sidebarExpanded ? "Recolher menu" : "Expandir menu"}>
              <span className="toggle-icon">{sidebarExpanded ? '◀' : '▶'}</span>
            </button>
          </div>
          <nav className="sidebar-menu">
            {SECTIONS.map(section => (
              <button
                key={section.key}
                className={
                  "sidebar-btn" + (activeSection === section.key ? " active" : "")
                }
                onClick={() => setActiveSection(section.key)}
                title={section.label}
              >
                <span className="sidebar-icon">{section.icon}</span>
                <span className="sidebar-label">{section.label}</span>
              </button>
            ))}
            <button className="sidebar-btn sidebar-logout" onClick={handleLogout} title="Sair">
              <span className="sidebar-icon"><FaSignOutAlt /></span>
              <span className="sidebar-label">Sair</span>
            </button>
          </nav>
        </aside>
        <main className="main-content">
          <div className="section-content">
            {SECTIONS.map(section => (
              activeSection === section.key && (
                section.key === "user"
                  ? <UserSection key={section.key} token={token} />
                : section.key === "server"
                  ? <ServerSection key={section.key} token={token} />
                : section.key === "search"
                  ? <SearchSection key={section.key} token={token} />
                : section.key === "game"
                  ? <GameSection key={section.key} token={token} />
                : section.key === "metrics"
                  ? <MetricsSection key={section.key} token={token} />
                : section.key === "admin"
                  ? <AdminSection key={section.key} token={token} />
                : section.key === "push"
                  ? <PushSection key={section.key} token={token} />
                  : <SectionPlaceholder key={section.key} section={section} />
              )
            ))}
          </div>
        </main>
      </div>
    </ErrorBoundary>
  );
} 