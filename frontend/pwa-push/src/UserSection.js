import React, { useEffect, useState } from "react";
import { FaUserCircle, FaEnvelope, FaCalendar, FaClock, FaServer, FaUsers, FaKey, FaStar, FaTrophy, FaCoins, FaGamepad } from "react-icons/fa";

function safeString(value) {
  if (value === null || value === undefined) return "";
  if (typeof value === "object") return JSON.stringify(value);
  return String(value);
}

function formatDate(dateString) {
  if (dateString == null || dateString === "") return "—";
  try {
    const date = new Date(dateString);
    if (Number.isNaN(date.getTime())) return "—";
    return date.toLocaleDateString("pt-BR", { day: "2-digit", month: "2-digit", year: "numeric", hour: "2-digit", minute: "2-digit" });
  } catch (e) {
    return "—";
  }
}

function extractUserData(data) {
  if (!data) return {};
  if (data.data && typeof data.data === "object") return data.data;
  return data;
}

function buildUserInfo(dashboard, profile) {
  const fromDashboard = extractUserData(dashboard);
  const userInfo = fromDashboard?.user_info || (fromDashboard && !fromDashboard.error ? {
    username: fromDashboard.username,
    email: fromDashboard.email,
    date_joined: fromDashboard.date_joined,
    last_login: fromDashboard.last_login,
  } : {});
  if (profile && !profile.error) {
    return {
      username: profile.username ?? userInfo.username,
      email: profile.email ?? userInfo.email,
      date_joined: profile.date_joined ?? userInfo.date_joined,
      last_login: profile.last_login ?? userInfo.last_login,
    };
  }
  return userInfo;
}

function buildServerStatus(serverStatusRes) {
  const data = serverStatusRes?.data ?? serverStatusRes;
  if (!data) return { online: false, playersOnline: 0 };
  const status = data.status ?? (data.online ? "online" : "offline");
  return {
    online: status === "online",
    playersOnline: data.players_online ?? data.players ?? 0,
  };
}

function buildGameStats(statsRes, dashboardRes) {
  const stats = statsRes && !statsRes.error ? statsRes : {};
  const dash = extractUserData(dashboardRes) || {};
  const skipKeys = ["username", "email", "date_joined", "last_login", "server_online", "players_online", "error"];
  const fromDash = {};
  Object.keys(dash).forEach((k) => {
    if (skipKeys.includes(k)) return;
    const v = dash[k];
    if (v !== undefined && v !== null && typeof v !== "object") fromDash[k] = v;
  });
  const labels = {
    characters_count: "Personagens",
    total_level: "Nível total",
    total_online_time: "Tempo online",
    total_pvp: "PvP",
    total_pk: "PK",
  };
  const result = {};
  [...Object.entries(stats), ...Object.entries(fromDash)].forEach(([key, value]) => {
    if (value === undefined || value === null) return;
    const label = labels[key] || key.replace(/_/g, " ");
    result[label] = typeof value === "number" ? value.toLocaleString("pt-BR") : String(value);
  });
  return result;
}

// Componente de Avatar com iniciais
function UserAvatar({ username }) {
  const initials = username
    ? username.substring(0, 2).toUpperCase()
    : "??";
  return <div className="user-avatar-placeholder">{initials}</div>;
}

// Barra de XP
function XpBar({ xp, xpForNext, level }) {
  if (xp == null) return null;
  const total = (xp ?? 0) + (xpForNext ?? 0);
  const pct = total > 0 ? Math.min(100, Math.round((xp / total) * 100)) : 0;
  return (
    <div className="xp-bar-container">
      <div className="xp-bar-header">
        <span className="xp-bar-label">⭐ Nível {level ?? "—"}</span>
        <span className="xp-bar-value">{xp?.toLocaleString("pt-BR")} XP</span>
      </div>
      <div className="xp-bar-track">
        <div className="xp-bar-fill" style={{ width: `${pct}%` }} />
      </div>
      <div className="xp-bar-sub">{pct}% para o próximo nível · Falta {xpForNext?.toLocaleString("pt-BR") ?? "—"} XP</div>
    </div>
  );
}

export default function UserSection({ token }) {
  const [profile, setProfile] = useState(null);
  const [dashboard, setDashboard] = useState(null);
  const [stats, setStats] = useState(null);
  const [serverStatus, setServerStatus] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [password, setPassword] = useState("");
  const [password2, setPassword2] = useState("");
  const [changeMsg, setChangeMsg] = useState("");
  const [changing, setChanging] = useState(false);
  const [gameData, setGameData] = useState(null);

  useEffect(() => {
    async function fetchData() {
      setLoading(true);
      setError("");
      try {
        const profileRes = await fetch("/api/v1/user/profile/", { headers: { Authorization: `Bearer ${token}` } });
        const dashboardRes = await fetch("/api/v1/user/dashboard/", { headers: { Authorization: `Bearer ${token}` } });
        const statsRes = await fetch("/api/v1/user/stats/", { headers: { Authorization: `Bearer ${token}` } });
        const serverStatusRes = await fetch("/api/v1/server/status/", { headers: { Authorization: `Bearer ${token}` } });

        let profileData = null, dashboardData = null;

        if (profileRes.ok) { profileData = await profileRes.json(); setProfile(profileData); } else { setProfile(null); }
        if (dashboardRes.ok) { dashboardData = await dashboardRes.json(); setDashboard(dashboardData); } else { setDashboard(null); }
        if (statsRes.ok) { setStats(await statsRes.json()); } else { setStats(null); }
        if (serverStatusRes.ok) { setServerStatus(await serverStatusRes.json()); } else { setServerStatus(null); }

        const dashData = dashboardData && !dashboardData.error ? (dashboardData.data || dashboardData) : {};
        const username = profileData?.username || dashData?.username;
        if (username) {
          try {
            const gameDataRes = await fetch(`/api/v1/user/game-data/?username=${encodeURIComponent(username)}`, {
              headers: { Authorization: `Bearer ${token}` },
            });
            if (gameDataRes.ok) setGameData(await gameDataRes.json());
          } catch (_) { }
        }
      } catch (e) {
        setError("Não foi possível carregar alguns dados. Tente recarregar.");
        setProfile(null); setDashboard(null); setStats(null); setServerStatus(null);
      }
      setLoading(false);
    }
    fetchData();
  }, [token]);

  async function handleChangePassword(e) {
    e.preventDefault();
    setChanging(true);
    setChangeMsg("");
    try {
      const res = await fetch("/api/v1/user/change-password/", {
        method: "POST",
        headers: { "Content-Type": "application/json", Authorization: `Bearer ${token}` },
        body: JSON.stringify({ new_password: password, new_password2: password2 }),
      });
      const data = await res.json();
      if (res.ok) { setChangeMsg("Senha alterada com sucesso!"); setPassword(""); setPassword2(""); }
      else { setChangeMsg(data.detail || "Erro ao alterar senha"); }
    } catch (e) { setChangeMsg("Erro ao conectar ao servidor"); }
    setChanging(false);
  }

  if (loading) return <div className="loading">Carregando dados do usuário</div>;

  const userInfo = buildUserInfo(dashboard, profile);
  const gameStats = buildGameStats(stats, dashboard);
  const { online: isServerOnline, playersOnline } = buildServerStatus(serverStatus);

  return (
    <div className="user-section">
      {/* Perfil */}
      <div className="user-profile-card pwa-card">
        <UserAvatar username={userInfo.username} />
        <div className="user-info">
          <h2>{safeString(userInfo.username || "Usuário")}</h2>
          <div className="user-details">
            <div className="user-detail-item">
              <FaEnvelope size={14} color="var(--pdl-gold)" />
              <span>{userInfo.email ? safeString(userInfo.email) : "—"}</span>
            </div>
            <div className="user-detail-item">
              <FaCalendar size={14} color="var(--pdl-gold)" />
              <span>Membro desde {formatDate(userInfo.date_joined)}</span>
            </div>
            <div className="user-detail-item">
              <FaClock size={14} color="var(--pdl-gold)" />
              <span>Último login {formatDate(userInfo.last_login)}</span>
            </div>
          </div>
        </div>
      </div>

      {/* XP bar */}
      {gameData && gameData.xp != null && (
        <XpBar xp={gameData.xp} xpForNext={gameData.xp_for_next_level} level={gameData.level} />
      )}

      {/* Status do Servidor */}
      <div className="user-server-status pwa-card">
        <div className="server-status-card">
          <div className="server-status-icon">
            <FaServer size={22} color={isServerOnline ? "var(--c-online)" : "var(--c-offline)"} />
          </div>
          <div className="server-status-info">
            <h3>Status do Servidor</h3>
            <p className={`status ${isServerOnline ? "online" : "offline"}`}>
              {isServerOnline ? "Online" : "Offline"}
            </p>
            <div className="players-info">
              <FaUsers size={13} color="var(--pdl-gold)" />
              <span>{playersOnline} jogadores online</span>
            </div>
          </div>
        </div>
      </div>

      {/* Dados do jogo PDL */}
      {gameData && (
        <div className="user-game-stats pwa-card">
          <h3><FaStar size={15} /> Dados PDL</h3>
          <div className="game-stats-grid">
            {gameData.achievements_count != null && (
              <div className="game-stat-item">
                <div className="stat-label"><FaTrophy size={11} /> Conquistas</div>
                <div className="stat-value">{gameData.achievements_count} / {gameData.total_achievements ?? "?"}</div>
              </div>
            )}
            {(gameData.battle_pass_level != null || gameData.battle_pass_xp != null) && (
              <div className="game-stat-item">
                <div className="stat-label">Battle Pass</div>
                <div className="stat-value">Nível {gameData.battle_pass_level ?? "—"}</div>
              </div>
            )}
            {gameData.fichas != null && (
              <div className="game-stat-item">
                <div className="stat-label"><FaCoins size={11} /> Fichas</div>
                <div className="stat-value">{gameData.fichas}</div>
              </div>
            )}
            {gameData.games_played != null && gameData.games_played > 0 && (
              <div className="game-stat-item">
                <div className="stat-label"><FaGamepad size={11} /> Jogos</div>
                <div className="stat-value">{gameData.games_played}</div>
              </div>
            )}
            {gameData.xp_ranking_position != null && (
              <div className="game-stat-item">
                <div className="stat-label">Ranking XP</div>
                <div className="stat-value">#{gameData.xp_ranking_position}</div>
              </div>
            )}
          </div>
        </div>
      )}

      {/* Estatísticas do Jogo */}
      <div className="user-game-stats pwa-card">
        <h3>Estatísticas do Jogo</h3>
        <div className="game-stats-grid">
          {Object.keys(gameStats).length > 0 ? (
            Object.entries(gameStats).map(([key, value]) => (
              <div key={key} className="game-stat-item">
                <div className="stat-label">{safeString(key)}</div>
                <div className="stat-value">{safeString(value)}</div>
              </div>
            ))
          ) : (
            <div className="no-stats">
              <p>Conecte-se ao servidor para ver suas estatísticas de personagens.</p>
            </div>
          )}
        </div>
      </div>

      {/* Alterar Senha */}
      <div className="user-password-box pwa-card">
        <div className="password-header">
          <FaKey size={16} color="var(--pdl-gold)" />
          <h3>Alterar Senha</h3>
        </div>
        <form onSubmit={handleChangePassword} className="user-password-form">
          <div className="form-group">
            <label htmlFor="new-password">Nova Senha</label>
            <input id="new-password" type="password" placeholder="Nova senha" value={password}
              onChange={e => setPassword(e.target.value)} required className="form-input" />
          </div>
          <div className="form-group">
            <label htmlFor="confirm-password">Confirmar Nova Senha</label>
            <input id="confirm-password" type="password" placeholder="Confirme a senha" value={password2}
              onChange={e => setPassword2(e.target.value)} required className="form-input" />
          </div>
          <button type="submit" disabled={changing} className="pwa-btn pwa-btn--primary">
            {changing ? "Alterando..." : "Alterar Senha"}
          </button>
        </form>
        {changeMsg && (
          <div className={`message ${changeMsg.includes("sucesso") ? "success" : "error"}`}>{changeMsg}</div>
        )}
      </div>

      {error && <div className="error">{error}</div>}
    </div>
  );
}