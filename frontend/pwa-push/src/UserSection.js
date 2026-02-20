import React, { useEffect, useState } from "react";
import { FaUserCircle, FaEnvelope, FaCalendar, FaClock, FaServer, FaUsers, FaKey, FaStar, FaTrophy, FaCoins, FaGamepad } from "react-icons/fa";

// Função para converter qualquer valor em string segura
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

// Normaliza resposta da API: backend pode retornar { data: {...} } ou objeto direto
function extractUserData(data) {
  if (!data) return {};
  if (data.data && typeof data.data === "object") return data.data;
  return data;
}

// Dados do usuário: dashboard retorna flat { username, email, date_joined, last_login }; profile idem
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

// Status do servidor: API retorna { success, data: { status, players_online } }
function buildServerStatus(serverStatusRes) {
  const data = serverStatusRes?.data ?? serverStatusRes;
  if (!data) return { online: false, playersOnline: 0 };
  const status = data.status ?? (data.online ? "online" : "offline");
  return {
    online: status === "online",
    playersOnline: data.players_online ?? data.players ?? 0,
  };
}

// Estatísticas do jogo: API user/stats retorna flat { characters_count, total_level, ... }; dashboard pode ter mais
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
        // Buscar dados individualmente para evitar que um erro quebre tudo
        const profileRes = await fetch("/api/v1/user/profile/", { 
          headers: { Authorization: `Bearer ${token}` } 
        });
        const dashboardRes = await fetch("/api/v1/user/dashboard/", { 
          headers: { Authorization: `Bearer ${token}` } 
        });
        const statsRes = await fetch("/api/v1/user/stats/", { 
          headers: { Authorization: `Bearer ${token}` } 
        });
        const serverStatusRes = await fetch("/api/v1/server/status/", { 
          headers: { Authorization: `Bearer ${token}` } 
        });

        let profileData = null;
        let dashboardData = null;

        // Processar cada resposta individualmente
        if (profileRes.ok) {
          profileData = await profileRes.json();
          setProfile(profileData);
        } else {
          setProfile(null);
        }

        if (dashboardRes.ok) {
          dashboardData = await dashboardRes.json();
          setDashboard(dashboardData);
        } else {
          setDashboard(null);
        }

        if (statsRes.ok) {
          setStats(await statsRes.json());
        } else {
          setStats(null);
        }

        if (serverStatusRes.ok) {
          setServerStatus(await serverStatusRes.json());
        } else {
          setServerStatus(null);
        }

        const dashData = dashboardData && !dashboardData.error ? (dashboardData.data || dashboardData) : {};
        const username = profileData?.username || dashData?.username;
        if (username) {
          try {
            const gameDataRes = await fetch(`/api/v1/user/game-data/?username=${encodeURIComponent(username)}`, {
              headers: { Authorization: `Bearer ${token}` },
            });
            if (gameDataRes.ok) {
              const gameDataJson = await gameDataRes.json();
              setGameData(gameDataJson);
            }
          } catch (_) {}
        }

      } catch (e) {
        console.error("Erro ao buscar dados:", e);
        setError("Não foi possível carregar alguns dados. Tente recarregar.");
        setProfile(null);
        setDashboard(null);
        setStats(null);
        setServerStatus(null);
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
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${token}`
        },
        body: JSON.stringify({ new_password: password, new_password2: password2 })
      });
      const data = await res.json();
      if (res.ok) {
        setChangeMsg("Senha alterada com sucesso!");
        setPassword("");
        setPassword2("");
      } else {
        setChangeMsg(data.detail || "Erro ao alterar senha");
      }
    } catch (e) {
      setChangeMsg("Erro ao conectar ao servidor");
    }
    setChanging(false);
  }

  if (loading) return <div className="loading">Carregando dados do usuário...</div>;

  const userInfo = buildUserInfo(dashboard, profile);
  const gameStats = buildGameStats(stats, dashboard);
  const { online: isServerOnline, playersOnline } = buildServerStatus(serverStatus);

  return (
    <div className="user-section">
      {/* Perfil do Usuário */}
      <div className="user-profile-card">
        <div className="user-avatar">
          <FaUserCircle size={80} color="#e6c77d" />
        </div>
        <div className="user-info">
          <h2>{safeString(userInfo.username || "Usuário")}</h2>
          <div className="user-details">
            <div className="user-detail-item">
              <FaEnvelope size={16} color="#e6c77d" />
              <span>{userInfo.email ? safeString(userInfo.email) : "—"}</span>
            </div>
            <div className="user-detail-item">
              <FaCalendar size={16} color="#e6c77d" />
              <span>Membro desde: {formatDate(userInfo.date_joined)}</span>
            </div>
            <div className="user-detail-item">
              <FaClock size={16} color="#e6c77d" />
              <span>Último login: {formatDate(userInfo.last_login)}</span>
            </div>
          </div>
        </div>
      </div>

      {/* Status do Servidor */}
      <div className="user-server-status">
        <div className="server-status-card">
          <div className="server-status-icon">
            <FaServer size={24} color={isServerOnline ? "#28a745" : "#dc3545"} />
          </div>
          <div className="server-status-info">
            <h3>Status do Servidor</h3>
            <p className={`status ${isServerOnline ? 'online' : 'offline'}`}>
              {isServerOnline ? "Online" : "Offline"}
            </p>
            <div className="players-info">
              <FaUsers size={16} color="#e6c77d" />
              <span>{playersOnline} jogadores online</span>
            </div>
          </div>
        </div>
      </div>

      {/* Dados do jogo PDL (XP, conquistas, Battle Pass) */}
      {gameData && (
        <div className="user-game-stats user-game-data-card">
          <h3><FaStar color="#e6c77d" /> Dados do jogo PDL</h3>
          <div className="game-stats-grid">
            <div className="game-stat-item">
              <div className="stat-label">Nível</div>
              <div className="stat-value">{gameData.level ?? "—"}</div>
            </div>
            <div className="game-stat-item">
              <div className="stat-label">XP</div>
              <div className="stat-value">{gameData.xp ?? "—"}</div>
            </div>
            {gameData.xp_for_next_level != null && (
              <div className="game-stat-item">
                <div className="stat-label">XP para próximo nível</div>
                <div className="stat-value">{gameData.xp_for_next_level}</div>
              </div>
            )}
            <div className="game-stat-item">
              <div className="stat-label"><FaTrophy /> Conquistas</div>
              <div className="stat-value">{gameData.achievements_count ?? 0} / {gameData.total_achievements ?? 0}</div>
            </div>
            {(gameData.battle_pass_level != null || gameData.battle_pass_xp != null) && (
              <div className="game-stat-item">
                <div className="stat-label">Battle Pass</div>
                <div className="stat-value">Nível {gameData.battle_pass_level ?? "—"} {gameData.battle_pass_xp != null ? `(${gameData.battle_pass_xp} XP)` : ""}</div>
              </div>
            )}
            {gameData.fichas != null && (
              <div className="game-stat-item">
                <div className="stat-label"><FaCoins /> Fichas</div>
                <div className="stat-value">{gameData.fichas}</div>
              </div>
            )}
            {gameData.games_played != null && gameData.games_played > 0 && (
              <div className="game-stat-item">
                <div className="stat-label"><FaGamepad /> Jogos</div>
                <div className="stat-value">{gameData.games_played}</div>
              </div>
            )}
            {gameData.xp_ranking_position != null && (
              <div className="game-stat-item">
                <div className="stat-label">Posição no ranking XP</div>
                <div className="stat-value">#{gameData.xp_ranking_position}</div>
              </div>
            )}
          </div>
        </div>
      )}

      {/* Estatísticas do Jogo (personagens, nível, PvP, etc.) */}
      <div className="user-game-stats">
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
              <p>Conecte-se ao servidor do jogo para ver personagens e estatísticas aqui, ou elas ainda não foram carregadas.</p>
            </div>
          )}
        </div>
      </div>

      {/* Alterar Senha */}
      <div className="user-password-box">
        <div className="password-header">
          <FaKey size={24} color="#e6c77d" />
          <h3>Alterar Senha</h3>
        </div>
        <form onSubmit={handleChangePassword} className="user-password-form">
          <div className="form-group">
            <label htmlFor="new-password">Nova Senha</label>
            <input
              id="new-password"
              type="password"
              placeholder="Digite sua nova senha"
              value={password}
              onChange={e => setPassword(e.target.value)}
              required
              className="form-input"
            />
          </div>
          <div className="form-group">
            <label htmlFor="confirm-password">Confirmar Nova Senha</label>
            <input
              id="confirm-password"
              type="password"
              placeholder="Confirme sua nova senha"
              value={password2}
              onChange={e => setPassword2(e.target.value)}
              required
              className="form-input"
            />
          </div>
          <button type="submit" disabled={changing} className="btn-primary">
            {changing ? "Alterando..." : "Alterar Senha"}
          </button>
        </form>
        {changeMsg && (
          <div className={`message ${changeMsg.includes("sucesso") ? "success" : "error"}`}>
            {changeMsg}
          </div>
        )}
      </div>

      {error && <div className="error">{error}</div>}
    </div>
  );
} 