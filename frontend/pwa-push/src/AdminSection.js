import React, { useState, useEffect } from "react";
import {
  FaCogs, FaUsers, FaBell, FaWallet, FaServer, FaToggleOn, FaToggleOff,
  FaSync, FaCode, FaShieldAlt, FaCheckCircle, FaTimesCircle, FaDesktop
} from "react-icons/fa";
import { apiFetch } from "./api";

function fmt(n) {
  if (n == null) return "—";
  if (typeof n === "number") return n.toLocaleString("pt-BR");
  return String(n);
}
function fmtBRL(n) {
  if (n == null) return "R$ —";
  return `R$ ${Number(n).toLocaleString("pt-BR", { minimumFractionDigits: 2 })}`;
}

/* ===== STAT CARD ===== */
function AdminStat({ icon, label, value, color = "var(--pdl-gold)", sub }) {
  return (
    <div className="admin-stat-card">
      <div className="admin-stat-icon" style={{ color }}>{icon}</div>
      <div className="admin-stat-body">
        <div className="admin-stat-value">{value ?? "—"}</div>
        <div className="admin-stat-label">{label}</div>
        {sub && <div className="admin-stat-sub">{sub}</div>}
      </div>
    </div>
  );
}

/* ===== USERS PANEL ===== */
function UsersPanel({ users }) {
  if (!users || Object.keys(users).length === 0) return (
    <div className="admin-empty">Nenhum dado de usuários disponível.</div>
  );
  return (
    <div className="admin-stats-grid">
      <AdminStat icon={<FaUsers size={20} />} label="Total" value={fmt(users.total)} color="#29b6f6" />
      <AdminStat icon={<FaCheckCircle size={20} />} label="Ativos" value={fmt(users.active)} color="#4caf50" />
      <AdminStat icon={<FaShieldAlt size={20} />} label="Staff" value={fmt(users.staff)} color="var(--pdl-gold)" />
      <AdminStat icon={<FaDesktop size={20} />} label="Online Hoje" value={fmt(users.online_today)} color="#ce93d8" />
      <AdminStat icon={<FaUsers size={20} />} label="Novos (7d)" value={fmt(users.last_7_days)} color="#ffb300" />
      <AdminStat icon={<FaUsers size={20} />} label="Novos (30d)" value={fmt(users.last_30_days)} color="#ff8a65" />
    </div>
  );
}

/* ===== PUSH PANEL ===== */
function PushPanel({ push }) {
  if (!push) return null;
  return (
    <div className="admin-stats-grid">
      <AdminStat icon={<FaBell size={20} />} label="Total de Inscr." value={fmt(push.total_subscriptions)} color="#ce93d8" />
      <AdminStat icon={<FaBell size={20} />} label="Inscr. Ativas" value={fmt(push.active_subscriptions)} color="#4caf50" />
    </div>
  );
}

/* ===== WALLET PANEL ===== */
function WalletPanel({ wallet }) {
  if (!wallet || Object.keys(wallet).length === 0) return null;
  return (
    <div className="admin-stats-grid">
      <AdminStat icon={<FaWallet size={20} />} label="Carteiras" value={fmt(wallet.total_wallets)} color="#ffb300" />
      <AdminStat icon={<FaWallet size={20} />} label="Saldo Total" value={fmtBRL(wallet.total_saldo)} color="#4caf50" />
      <AdminStat icon={<FaWallet size={20} />} label="Bônus Total" value={fmtBRL(wallet.total_bonus)} color="var(--pdl-gold)" />
    </div>
  );
}

/* ===== SYSTEM PANEL ===== */
function SystemPanel({ system }) {
  if (!system) return null;
  return (
    <div className="admin-system-grid">
      <div className="admin-sys-item">
        <span className="admin-sys-label">Versão</span>
        <span className="admin-sys-value">{system.version}</span>
      </div>
      <div className="admin-sys-item">
        <span className="admin-sys-label">Python</span>
        <span className="admin-sys-value">{system.python_version}</span>
      </div>
      <div className="admin-sys-item">
        <span className="admin-sys-label">Plataforma</span>
        <span className="admin-sys-value">{system.platform}</span>
      </div>
      <div className="admin-sys-item">
        <span className="admin-sys-label">Modo Debug</span>
        <span className={`admin-sys-badge ${system.debug ? "warn" : "good"}`}>
          {system.debug ? "DEBUG" : "Produção"}
        </span>
      </div>
    </div>
  );
}

/* ===== API ENDPOINTS PANEL ===== */
function ApiConfigPanel({ apiConfig, token, onRefresh }) {
  const [saving, setSaving] = useState(false);
  const [toggling, setToggling] = useState({});
  const [localEndpoints, setLocalEndpoints] = useState({});

  useEffect(() => {
    if (apiConfig?.endpoints) setLocalEndpoints({ ...apiConfig.endpoints });
  }, [apiConfig]);

  async function toggleEndpoint(key, current) {
    setToggling(p => ({ ...p, [key]: true }));
    try {
      const r = await apiFetch("/api/v1/admin/config/", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ [key]: !current }),
      });
      if (r.ok) {
        setLocalEndpoints(p => ({ ...p, [key]: !current }));
      }
    } catch (_) { }
    setToggling(p => ({ ...p, [key]: false }));
  }

  if (!apiConfig || Object.keys(localEndpoints).length === 0) return (
    <div className="admin-empty">Configuração de endpoints não disponível (requer superuser).</div>
  );

  const total = Object.keys(localEndpoints).length;
  const active = Object.values(localEndpoints).filter(Boolean).length;

  return (
    <div className="admin-endpoints-wrap">
      <div className="admin-endpoints-summary">
        <span className="ep-total">{total} endpoints</span>
        <span className="ep-active">{active} ativos</span>
        <span className="ep-inactive">{total - active} inativos</span>
      </div>
      <div className="admin-endpoints-list">
        {Object.entries(localEndpoints).map(([key, enabled]) => (
          <div key={key} className={`admin-ep-item ${enabled ? "" : "admin-ep-item--off"}`}>
            <div className="admin-ep-key">{key.replace(/_/g, " ")}</div>
            <button
              type="button"
              className={`admin-ep-toggle ${enabled ? "on" : "off"}`}
              onClick={() => toggleEndpoint(key, enabled)}
              disabled={!!toggling[key]}
              title={enabled ? "Desativar" : "Ativar"}
            >
              {toggling[key] ? "…" : enabled ? <FaToggleOn size={22} /> : <FaToggleOff size={22} />}
            </button>
          </div>
        ))}
      </div>
    </div>
  );
}

/* ===== TABS ===== */
const ADMIN_TABS = [
  { key: "users", label: "Usuários", icon: <FaUsers size={13} /> },
  { key: "push", label: "Push", icon: <FaBell size={13} /> },
  { key: "wallet", label: "Financeiro", icon: <FaWallet size={13} /> },
  { key: "api", label: "Endpoints", icon: <FaServer size={13} /> },
  { key: "system", label: "Sistema", icon: <FaDesktop size={13} /> },
];

export default function AdminSection({ token }) {
  const [tab, setTab] = useState("users");
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  async function fetchDashboard() {
    setLoading(true);
    setError("");
    try {
      const r = await apiFetch("/api/v1/admin/dashboard/");
      if (r.ok) {
        const d = await r.json();
        setData(d.data || d);
      } else if (r.status === 403) {
        setError("Acesso negado. Esta seção requer permissões de staff.");
      } else {
        setError("Erro ao carregar painel de administração.");
      }
    } catch (_) {
      setError("Erro ao conectar ao servidor.");
    }
    setLoading(false);
  }

  useEffect(() => { fetchDashboard(); }, [token]);

  if (loading) return <div className="loading">Carregando painel admin</div>;

  if (error) {
    return (
      <div className="admin-section">
        <div className="pwa-card" style={{ textAlign: "center", padding: "2.5rem 1.5rem" }}>
          <FaShieldAlt size={40} color="var(--pdl-gold)" style={{ marginBottom: "1rem" }} />
          <h3 style={{ color: "var(--pdl-gold)", margin: "0 0 0.5rem" }}>Acesso Restrito</h3>
          <p style={{ color: "var(--pdl-text-muted)", margin: 0 }}>{error}</p>
        </div>
      </div>
    );
  }

  return (
    <div className="admin-section">
      {/* Header */}
      <div className="admin-header pwa-card">
        <div className="admin-header-left">
          <FaCogs size={28} color="var(--pdl-gold)" />
          <div>
            <h2>Painel de Administração</h2>
            <p>Visibilidade das estatísticas e configurações do sistema.</p>
          </div>
        </div>
        <button type="button" className="pwa-btn pwa-btn--secondary admin-refresh-btn" onClick={fetchDashboard}>
          <FaSync size={13} />
          Atualizar
        </button>
      </div>

      {/* Tabs */}
      <div className="game-tabs">
        {ADMIN_TABS.map(t => (
          <button
            key={t.key}
            type="button"
            className={`game-tab ${tab === t.key ? "game-tab--active" : ""}`}
            onClick={() => setTab(t.key)}
          >
            {t.icon}
            <span>{t.label}</span>
          </button>
        ))}
      </div>

      {/* Tab content */}
      <div className="pwa-card admin-tab-content">
        {tab === "users" && (
          <>
            <div className="game-section-header">
              <FaUsers size={18} color="var(--pdl-gold)" />
              <h3>Usuários do Sistema</h3>
            </div>
            <UsersPanel users={data?.users} />
          </>
        )}

        {tab === "push" && (
          <>
            <div className="game-section-header">
              <FaBell size={18} color="var(--pdl-gold)" />
              <h3>Notificações Push</h3>
            </div>
            <PushPanel push={data?.push} />
          </>
        )}

        {tab === "wallet" && (
          <>
            <div className="game-section-header">
              <FaWallet size={18} color="var(--pdl-gold)" />
              <h3>Resumo Financeiro</h3>
            </div>
            <WalletPanel wallet={data?.wallet} />
          </>
        )}

        {tab === "api" && (
          <>
            <div className="game-section-header">
              <FaServer size={18} color="var(--pdl-gold)" />
              <h3>Gerenciar Endpoints</h3>
            </div>
            <ApiConfigPanel apiConfig={data?.api_config} token={token} onRefresh={fetchDashboard} />
          </>
        )}

        {tab === "system" && (
          <>
            <div className="game-section-header">
              <FaCode size={18} color="var(--pdl-gold)" />
              <h3>Informações do Sistema</h3>
            </div>
            <SystemPanel system={data?.system} />
          </>
        )}
      </div>
    </div>
  );
}