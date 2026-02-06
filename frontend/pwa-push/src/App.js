import React, { useState, useEffect } from "react";
import { subscribeUserToPush, unsubscribeUserFromPush } from "./push";
import { setTokens, clearTokens, getToken, apiFetch } from "./api";
import "./App.css";
import UserSection from "./UserSection";
import ServerSection from "./ServerSection";
import SearchSection from "./SearchSection";
import GameSection from "./GameSection";
import MetricsSection from "./MetricsSection";
import AdminSection from "./AdminSection";
import PushSection from "./PushSection";
import { FaUser, FaServer, FaSearch, FaGamepad, FaChartBar, FaCogs, FaBell, FaSignOutAlt, FaBars, FaTimes } from "react-icons/fa";

const SECTIONS = [
  { key: "user", label: "Usuário", icon: FaUser },
  { key: "server", label: "Servidor", icon: FaServer },
  { key: "search", label: "Busca", icon: FaSearch },
  { key: "game", label: "Jogo", icon: FaGamepad },
  { key: "metrics", label: "Métricas", icon: FaChartBar },
  { key: "admin", label: "Administração", icon: FaCogs },
  { key: "push", label: "Push", icon: FaBell },
];

const SECTION_COMPONENTS = {
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

  static getDerivedStateFromError(error) {
    return { hasError: true, error };
  }

  componentDidCatch(error, errorInfo) {
    if (typeof this.props.onError === "function") {
      this.props.onError(error, errorInfo);
    }
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

function SectionPlaceholder({ section }) {
  return (
    <div className="pwa-section-placeholder">
      <div className="pwa-card">
        <h2>{section.label}</h2>
        <p>Esta seção estará disponível em breve.</p>
      </div>
    </div>
  );
}

export default function App() {
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
  const [activeSection, setActiveSection] = useState(SECTIONS[0].key);
  const [menuOpen, setMenuOpen] = useState(false);
  const [discordServer, setDiscordServer] = useState(null);

  useEffect(() => {
    const title = SECTIONS.find((s) => s.key === activeSection)?.label || "PDL";
    document.title = activeSection ? `${title} — PDL` : "PDL — Notificações e Painel";
  }, [activeSection]);

  useEffect(() => {
    if (!token) return;
    let cancelled = false;
    apiFetch("/api/v1/discord/server/by-domain/")
      .then((res) => res.ok ? res.json() : null)
      .then((data) => { if (!cancelled && data) setDiscordServer(data); })
      .catch(() => {});
    return () => { cancelled = true; };
  }, [token]);

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
        setLoginError(data.detail || "Usuário ou senha inválidos.");
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
      const registration = await navigator.serviceWorker.ready;
      const subscription = await registration.pushManager.getSubscription();
      if (subscription) {
        await subscription.unsubscribe();
        await unsubscribeUserFromPush(token, subscription);
        setSubscribed(false);
        setPermission(typeof Notification !== "undefined" ? Notification.permission : "default");
      }
    } catch (_) {}
  };

  const handleLogout = async () => {
    try {
      await fetch("/api/v1/auth/logout/", {
        method: "POST",
        headers: { "Content-Type": "application/json", Authorization: `Bearer ${token}` },
      });
    } catch (_) {}
    clearTokens();
    setToken("");
    setSubscribed(false);
    setUsername("");
    setPassword("");
    setMenuOpen(false);
  };

  const setSection = (key) => {
    setActiveSection(key);
    setMenuOpen(false);
  };

  const ActiveComponent = SECTION_COMPONENTS[activeSection];

  if (!token) {
    return (
      <ErrorBoundary>
        <div className="pwa-app pwa-app--login">
          <div className="pwa-login">
            <div className="pwa-card pwa-login__card">
              <div className="pwa-login__header">
                <img src="/static/pwa/icons/logo.png" alt="" className="pwa-login__logo" />
                <h1>Entrar</h1>
                <p className="pwa-login__tip">
                  Acesse sua conta para gerenciar notificações e configurações.
                </p>
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
                <button className="pwa-btn pwa-btn--primary pwa-btn--block" type="submit" disabled={loading}>
                  {loading ? "Entrando…" : "Entrar"}
                </button>
              </form>
              {loginError && <p className="pwa-login__error" role="alert">{loginError}</p>}
            </div>
          </div>
        </div>
      </ErrorBoundary>
    );
  }

  return (
    <ErrorBoundary>
      <div className="pwa-app">
        <header className="pwa-nav" role="banner">
          <div className="pwa-nav__inner">
            <a href="/" className="pwa-nav__brand" aria-label="Ir para o site">
              <img src="/static/pwa/icons/logo.png" alt="" className="pwa-nav__logo" />
              <span className="pwa-nav__title">PDL</span>
            </a>

            <button
              type="button"
              className="pwa-nav__toggle"
              onClick={() => setMenuOpen(!menuOpen)}
              aria-expanded={menuOpen}
              aria-label={menuOpen ? "Fechar menu" : "Abrir menu"}
            >
              {menuOpen ? <FaTimes /> : <FaBars />}
            </button>

            <nav className={`pwa-nav__menu ${menuOpen ? "pwa-nav__menu--open" : ""}`} aria-label="Navegação">
              <ul className="pwa-nav__list">
                {SECTIONS.map((section) => (
                  <li key={section.key}>
                    <button
                      type="button"
                      className={`pwa-nav__link ${activeSection === section.key ? "pwa-nav__link--active" : ""}`}
                      onClick={() => setSection(section.key)}
                      aria-current={activeSection === section.key ? "page" : undefined}
                    >
                      <span className="pwa-nav__icon">{React.createElement(section.icon)}</span>
                      <span>{section.label}</span>
                    </button>
                  </li>
                ))}
              </ul>
              <button
                type="button"
                className="pwa-nav__link pwa-nav__link--logout"
                onClick={handleLogout}
                aria-label="Sair"
              >
                <span className="pwa-nav__icon"><FaSignOutAlt /></span>
                <span>Sair</span>
              </button>
            </nav>
          </div>
        </header>

        <main className="pwa-main" role="main">
          <div className="pwa-main__inner">
            {ActiveComponent ? (
              <ActiveComponent key={activeSection} token={token} />
            ) : (
              <SectionPlaceholder section={SECTIONS.find((s) => s.key === activeSection) || SECTIONS[0]} />
            )}
          </div>
          {discordServer && discordServer.server_name && (
            <footer className="pwa-footer">
              <span className="pwa-footer-discord">
                Comunidade Discord: <strong>{discordServer.server_name}</strong>
              </span>
            </footer>
          )}
        </main>
      </div>
    </ErrorBoundary>
  );
}
