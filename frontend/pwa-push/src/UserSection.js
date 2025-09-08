import React, { useEffect, useState } from "react";
import { FaUserCircle, FaEnvelope, FaCalendar, FaClock, FaServer, FaUsers, FaKey } from "react-icons/fa";

// Função para converter qualquer valor em string segura
function safeString(value) {
  if (value === null || value === undefined) return "";
  if (typeof value === "object") return JSON.stringify(value);
  return String(value);
}

// Função para formatar data
function formatDate(dateString) {
  if (!dateString) return "N/A";
  try {
    const date = new Date(dateString);
    return date.toLocaleString('pt-BR');
  } catch (e) {
    return dateString;
  }
}

// Função para extrair dados do JSON
function extractUserData(data) {
  if (!data) return {};
  
  // Se data é um objeto com 'data' dentro
  if (data.data && typeof data.data === 'object') {
    return data.data;
  }
  
  // Se data é diretamente o objeto
  return data;
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

  useEffect(() => {
    async function fetchData() {
      setLoading(true);
      setError("");
      try {
        console.log("Buscando dados do usuário...");
        
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

        // Processar cada resposta individualmente
        if (profileRes.ok) {
          const profileData = await profileRes.json();
          console.log("Profile data:", profileData);
          setProfile(profileData);
        } else {
          console.warn("Erro ao buscar perfil:", profileRes.status);
          setProfile({ 
            username: "admin", 
            email: "admin@exemplo.com",
            first_name: "Administrador",
            last_name: "Sistema"
          });
        }

        if (dashboardRes.ok) {
          const dashboardData = await dashboardRes.json();
          console.log("Dashboard data:", dashboardData);
          setDashboard(dashboardData);
        } else {
          console.warn("Erro ao buscar dashboard:", dashboardRes.status);
          setDashboard({ 
            success: true,
            data: {
              user_info: {
                username: "admin",
                email: "admin@exemplo.com",
                date_joined: new Date().toISOString(),
                last_login: new Date().toISOString()
              },
              game_stats: {},
              server_status: { online: true, players_online: 0 }
            }
          });
        }

        if (statsRes.ok) {
          const statsData = await statsRes.json();
          console.log("Stats data:", statsData);
          setStats(statsData);
        } else {
          console.warn("Erro ao buscar estatísticas:", statsRes.status);
          setStats({ 
            success: true,
            data: {},
            timestamp: new Date().toISOString()
          });
        }

        // Buscar status real do servidor
        if (serverStatusRes.ok) {
          const serverStatusData = await serverStatusRes.json();
          console.log("Server status data:", serverStatusData);
          setServerStatus(serverStatusData);
        } else {
          console.warn("Erro ao buscar status do servidor:", serverStatusRes.status);
          setServerStatus({ online: false, players: 0 });
        }

      } catch (e) {
        console.error("Erro ao buscar dados:", e);
        setError("Erro ao buscar dados do usuário");
        // Definir dados padrão em caso de erro
        setProfile({ username: "admin", email: "admin@exemplo.com" });
        setDashboard({ success: true, data: { user_info: {}, game_stats: {}, server_status: {} } });
        setStats({ success: true, data: {} });
        setServerStatus({ online: false, players: 0 });
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

  // Extrair dados estruturados
  const userInfo = extractUserData(dashboard)?.user_info || {};
  const gameStats = extractUserData(dashboard)?.game_stats || {};
  
  // Usar status real do servidor em vez do dashboard
  const isServerOnline = serverStatus?.online || false;
  const playersOnline = serverStatus?.players || serverStatus?.players_online || 0;

  return (
    <div className="user-section">
      {/* Perfil do Usuário */}
      <div className="user-profile-card">
        <div className="user-avatar">
          <FaUserCircle size={80} color="#e6c77d" />
        </div>
        <div className="user-info">
          <h2>{safeString(userInfo.username || profile?.username || "Usuário")}</h2>
          <div className="user-details">
            <div className="user-detail-item">
              <FaEnvelope size={16} color="#6c757d" />
              <span>{safeString(userInfo.email || profile?.email || "email@exemplo.com")}</span>
            </div>
            <div className="user-detail-item">
              <FaCalendar size={16} color="#6c757d" />
              <span>Membro desde: {formatDate(userInfo.date_joined)}</span>
            </div>
            <div className="user-detail-item">
              <FaClock size={16} color="#6c757d" />
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
              <FaUsers size={16} color="#6c757d" />
              <span>{playersOnline} jogadores online</span>
            </div>
          </div>
        </div>
      </div>

      {/* Estatísticas do Jogo */}
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
              <p>Nenhuma estatística disponível</p>
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