import React, { useState, useEffect } from "react";
import { subscribeUserToPush, unsubscribeUserFromPush } from "./push";
import { setTokens, clearTokens, getToken, apiFetch } from "./api";
import "./App.css";
import { useServer } from "./ServerContext";
import HomeSection from "./HomeSection";
import UserSection from "./UserSection";
import ServerSection from "./ServerSection";
import SearchSection from "./SearchSection";
import GameSection from "./GameSection";
import MetricsSection from "./MetricsSection";
import AdminSection from "./AdminSection";
import PushSection from "./PushSection";
import {
  FaHome, FaUser, FaServer, FaSearch, FaGamepad,
  FaChartBar, FaCogs, FaBell, FaSignOutAlt, FaBars, FaTimes
} from "react-icons/fa";

const SECTIONS = [
  { key: "home", label: "Início", icon: FaHome },
  { key: "user", label: "Usuário", icon: FaUser },
  { key: "server", label: "Servidor", icon: FaServer },
  { key: "search", label: "Busca", icon: FaSearch },
  { key: "game", label: "Jogo", icon: FaGamepad },
  { key: "metrics", label: "Métricas", icon: FaChartBar },
  { key: "admin", label: "Admin", icon: FaCogs },
  { key: "push", label: "Notificações", icon: FaBell },
];

const SECTION_COMPONENTS = {
  home: HomeSection,
  user: UserSection,
  server: ServerSection,
  search: SearchSection,
  game: GameSection,
  metrics: MetricsSection,
  admin: AdminSection,
  push: PushSection,
};

class ErrorBoundary extends React.Component {
  constructor(props) {
    super(props);
    this.state = { hasError: false, error: null };
  }
  static getDerivedStateFromError(error) { return { hasError: true, error }; }
  componentDidCatch(error, info) {
    if (typeof this.props.onError === "function") this.props.onError(error, info);
  }
  render() {
    if (this.state.hasError) {
      return (
        <div className="pwa-error-boundary">
          <div className="pwa-card pwa-card--error">
            <h2>Algo deu errado</h2>
            <p>{this.state.error?.message || "Erro inesperado."}</p>
            <button type="button" className="pwa-btn pwa-btn--primary" onClick={() => window.location.reload()}>
              Recarregar
            </button>
          </div>
        </div>
      );
    }
    return this.props.children;
  }
}

export default function App() {
  const { info } = useServer();

  const [permission, setPermission] = useState(() =>
    typeof Notification !== "undefined" ? Notification.permission : "default"
  );
  const [subscribed, setSubscribed] = useState(false);
  const [token, setToken] = useState(() => getToken());
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [loginError, setLoginError] = useState("");
  const [loading, setLoading] = useState(false);
  const [pushError, setPushError] = useState("");
  const [activeSection, setActiveSection] = useState("home");
  const [sidebarOpen, setSidebarOpen] = useState(false);

  // Atualiza título do documento com nome dinâmico do servidor
  useEffect(() => {
    const section = SECTIONS.find((s) => s.key === activeSection);
    const label = section?.label || "Início";
    document.title = `${label} — ${info.name || "PDL"}`;
  }, [activeSection, info.name]);

  const handleLogin = async (e) => {
    e.preventDefault();
    setLoading(true);
    setLoginError("");
    try {
      const res = await fetch("/api/v1/auth/login/", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ username, password }),
      });
      const data = await res.json().catch(() => ({}));
      if (res.ok && data.access) {
        setTokens(data.access, data.refresh);
        setToken(data.access);
      } else {
        setLoginError(data.detail || data.error || "Usuário ou senha inválidos.");
      }
    } catch (_) {
      setLoginError("Erro ao conectar ao servidor.");
    }
    setLoading(false);
  };

  const handleSubscribe = async () => {
    setPushError("");
    const result = await subscribeUserToPush(token);
    if (result?.success) {
      setSubscribed(true);
      setPermission("granted");
    } else if (result?.error) {
      setPushError(result.error);
    }
  };

  const handleUnsubscribe = async () => {
    if (!("serviceWorker" in navigator)) return;
    try {
      const reg = await navigator.serviceWorker.ready;
      const sub = await reg.pushManager.getSubscription();
      if (sub) {
        await sub.unsubscribe();
        await unsubscribeUserFromPush(token, sub);
        setSubscribed(false);
        setPermission(typeof Notification !== "undefined" ? Notification.permission : "default");
      }
    } catch (_) { }
  };

  const handleLogout = async () => {
    try {
      await fetch("/api/v1/auth/logout/", {
        method: "POST",
        headers: { "Content-Type": "application/json", Authorization: `Bearer ${token}` },
      });
    } catch (_) { }
    clearTokens();
    setToken("");
    setSubscribed(false);
    setUsername("");
    setPassword("");
    setSidebarOpen(false);
    setActiveSection("home");
  };

  const navigate = (key) => {
    setActiveSection(key);
    setSidebarOpen(false);
  };

  // ---- LOGIN SCREEN ----
  if (!token) {
    return (
      <ErrorBoundary>
        <div className="pwa-app pwa-app--login">
          <div className="pwa-login">
            <div className="pwa-login__card pwa-card">
              <div className="pwa-login__header">
                <img
                  src={info.logo_url || "/static/pwa/icons/logo.png"}
                  alt=""
                  className="pwa-login__logo"
                />
                <h1>{info.name || "PDL"}</h1>
                <p className="pwa-login__tip">
                  {info.description || "Acesse sua conta para gerenciar notificações e configurações."}
                </p>
                {info.chronicle && <span className="pwa-login__badge">{info.chronicle}</span>}
              </div>
              <form className="pwa-login__form" onSubmit={handleLogin} noValidate>
                <input
                  type="text"
                  placeholder="Usuário"
                  value={username}
                  onChange={(e) => setUsername(e.target.value)}
                  className="pwa-input"
                  autoComplete="username"
                  autoFocus
                  required
                  aria-label="Usuário"
                />
                <input
                  type="password"
                  placeholder="Senha"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  className="pwa-input"
                  autoComplete="current-password"
                  required
                  aria-label="Senha"
                />
                <button
                  className="pwa-btn pwa-btn--primary pwa-btn--block"
                  type="submit"
                  disabled={loading}
                >
                  {loading ? "Entrando…" : "Entrar"}
                </button>
              </form>
              {loginError && (
                <p className="pwa-login__error" role="alert">{loginError}</p>
              )}
            </div>
          </div>
        </div>
      </ErrorBoundary>
    );
  }

  // ---- MAIN APP ----
  const ActiveComponent = SECTION_COMPONENTS[activeSection];
  const ActiveIcon = SECTIONS.find((s) => s.key === activeSection)?.icon;

  return (
    <ErrorBoundary>
      <div className={`pwa-app ${sidebarOpen ? "pwa-app--sidebar-open" : ""}`}>

        {/* Overlay para mobile */}
        {sidebarOpen && (
          <div
            className="pwa-sidebar-overlay"
            onClick={() => setSidebarOpen(false)}
            aria-hidden="true"
          />
        )}

        {/* Sidebar */}
        <aside className="pwa-sidebar" role="navigation" aria-label="Menu principal">
          <div className="pwa-sidebar__brand" onClick={() => navigate("home")}>
            <img
              src={info.logo_url || "/static/pwa/icons/logo.png"}
              alt=""
              className="pwa-sidebar__logo"
            />
            <span className="pwa-sidebar__title">{info.short_name || info.name || "PDL"}</span>
          </div>

          <nav className="pwa-sidebar__nav">
            {SECTIONS.map((section) => {
              const Icon = section.icon;
              const isActive = activeSection === section.key;
              return (
                <button
                  key={section.key}
                  type="button"
                  className={`pwa-sidebar__item ${isActive ? "pwa-sidebar__item--active" : ""}`}
                  onClick={() => navigate(section.key)}
                  aria-current={isActive ? "page" : undefined}
                >
                  <span className="pwa-sidebar__item-icon">
                    <Icon size={18} />
                  </span>
                  <span className="pwa-sidebar__item-label">{section.label}</span>
                  {isActive && <span className="pwa-sidebar__item-indicator" />}
                </button>
              );
            })}
          </nav>

          <div className="pwa-sidebar__footer">
            <button
              type="button"
              className="pwa-sidebar__logout"
              onClick={handleLogout}
              aria-label="Sair"
            >
              <FaSignOutAlt size={16} />
              <span>Sair</span>
            </button>
          </div>
        </aside>

        {/* Main area */}
        <div className="pwa-main-wrap">
          {/* Top bar (mobile) */}
          <header className="pwa-topbar" role="banner">
            <button
              type="button"
              className="pwa-topbar__hamburger"
              onClick={() => setSidebarOpen(!sidebarOpen)}
              aria-expanded={sidebarOpen}
              aria-label={sidebarOpen ? "Fechar menu" : "Abrir menu"}
            >
              {sidebarOpen ? <FaTimes /> : <FaBars />}
            </button>
            <div className="pwa-topbar__brand" onClick={() => navigate("home")}>
              {ActiveIcon && React.createElement(ActiveIcon, { size: 16 })}
              <span>
                {SECTIONS.find((s) => s.key === activeSection)?.label || "PDL"}
              </span>
            </div>
            <button
              type="button"
              className="pwa-topbar__logout"
              onClick={handleLogout}
              aria-label="Sair"
            >
              <FaSignOutAlt size={16} />
            </button>
          </header>

          <main className="pwa-content" role="main">
            {ActiveComponent ? (
              <ActiveComponent
                key={activeSection}
                token={token}
                onNavigate={navigate}
                activeSection={activeSection}
                subscribed={subscribed}
                permission={permission}
                onSubscribe={handleSubscribe}
                onUnsubscribe={handleUnsubscribe}
                pushError={pushError}
              />
            ) : (
              <div className="pwa-card" style={{ padding: "2rem", textAlign: "center" }}>
                <p style={{ color: "var(--pdl-text-muted)" }}>Seção não encontrada.</p>
              </div>
            )}
          </main>
        </div>
      </div>
    </ErrorBoundary>
  );
}
