import React, { useState, useEffect } from "react";
import { FaServer, FaUsers, FaCrown, FaTrophy, FaDragon, FaSkull, FaCoins, FaClock, FaMedal, FaCode } from "react-icons/fa";

// Função para converter qualquer valor em string segura
function safeString(value) {
  if (value === null || value === undefined) return "N/A";
  if (typeof value === "object") return JSON.stringify(value);
  return String(value);
}

// Função para formatar uptime
function formatUptime(uptime) {
  if (!uptime) return "0h";
  if (typeof uptime === 'string') return uptime;
  if (typeof uptime === 'number') {
    const hours = Math.floor(uptime / 3600);
    const days = Math.floor(hours / 24);
    if (days > 0) return `${days}d ${hours % 24}h`;
    return `${hours}h`;
  }
  return uptime;
}

// Função para formatar números
function formatNumber(num) {
  if (!num || num === 0) return "0";
  if (num >= 1000000000) return `${(num / 1000000000).toFixed(1)}B`;
  if (num >= 1000000) return `${(num / 1000000).toFixed(1)}M`;
  if (num >= 1000) return `${(num / 1000).toFixed(1)}K`;
  return num.toString();
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

function RankingTable({ title, data, icon, emptyMessage = "Nenhum ranking disponível" }) {
  if (!Array.isArray(data) || data.length === 0) {
    return (
      <div className="ranking-table">
        <div className="ranking-header">
          <div className="ranking-icon">{icon}</div>
          <h3>{title}</h3>
        </div>
        <div className="ranking-empty">
          <div className="empty-icon">🏆</div>
          <p>{emptyMessage}</p>
        </div>
      </div>
    );
  }

  const getPositionClass = (index) => {
    if (index === 0) return "gold";
    if (index === 1) return "silver";
    if (index === 2) return "bronze";
    return "other";
  };

  const formatValue = (item, title) => {
    if (title.includes("Level")) return item.level;
    if (title.includes("PvP")) return item.pvp_count;
    if (title.includes("PK")) return item.pk_count;
    if (title.includes("Rico")) return formatNumber(item.adena);
    if (title.includes("Online")) return formatUptime(item.online_time);
    if (title.includes("Olimpíada")) return item.points;
    if (title.includes("Guild")) return item.member_count;
    if (title.includes("Heróis")) return item.hero_count;
    return item.level || item.pvp_count || item.pk_count || item.adena || item.online_time || item.points || item.member_count || item.hero_count || "N/A";
  };

  const getDetails = (item, title) => {
    if (title.includes("Level") || title.includes("PvP") || title.includes("PK")) {
      return `${safeString(item.class_name || "N/A")} • ${safeString(item.clan_name || "Sem Clã")}`;
    }
    if (title.includes("Rico")) {
      return `${safeString(item.class_name || "N/A")} • ${safeString(item.clan_name || "Sem Clã")}`;
    }
    if (title.includes("Online")) {
      return `${safeString(item.class_name || "N/A")} • ${safeString(item.clan_name || "Sem Clã")}`;
    }
    if (title.includes("Olimpíada")) {
      return `${safeString(item.class_name || "N/A")} • Rank #${item.rank}`;
    }
    if (title.includes("Heróis")) {
      return `${safeString(item.class_name || "N/A")} • ${safeString(item.hero_type || "N/A")}`;
    }
    if (title.includes("Guild")) {
      return `Líder: ${safeString(item.leader_name)} • Reputação: ${item.reputation}`;
    }
    return "";
  };

  return (
    <div className="ranking-table">
      <div className="ranking-header">
        <div className="ranking-icon">{icon}</div>
        <h3>{title}</h3>
      </div>
      <div className="ranking-content">
        {data.slice(0, 10).map((item, index) => (
          <div key={index} className="ranking-item">
            <div className={`ranking-position ${getPositionClass(index)}`}>
              {index + 1}
            </div>
            <div className="ranking-info">
              <div className="ranking-name">{safeString(item.char_name || item.clan_name)}</div>
              <div className="ranking-details">{getDetails(item, title)}</div>
            </div>
            <div className="ranking-value">
              {formatValue(item, title)}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}

function StatusCard({ title, value, icon, color = "#e6c77d", subtitle = "" }) {
  return (
    <div className="status-card" style={{ borderLeftColor: color }}>
      <div className="icon" style={{ color }}>
        {icon}
      </div>
      <div className="status-info">
        <h3>{title}</h3>
        <div className="value">{safeString(value)}</div>
        {subtitle && <div className="subtitle">{subtitle}</div>}
      </div>
    </div>
  );
}

function BossGrid({ bosses }) {
  if (!Array.isArray(bosses) || bosses.length === 0) {
    return (
      <div className="boss-grid">
        <div className="boss-header">
          <FaDragon size={24} color="#e6c77d" />
          <h3>Status dos Bosses</h3>
        </div>
        <div className="boss-empty">
          <div className="empty-icon">🐉</div>
          <p>Nenhum boss disponível</p>
        </div>
      </div>
    );
  }

  return (
    <div className="boss-grid">
      <div className="boss-header">
        <FaDragon size={24} color="#e6c77d" />
        <h3>Status dos Bosses</h3>
        <span className="boss-count">{bosses.length} bosses</span>
      </div>
      <div className="boss-cards">
        {bosses.map((boss, i) => (
          <div key={i} className={`boss-card ${boss.alive ? 'alive' : 'dead'}`}>
            <div className="boss-status">
              {boss.alive ? <FaCheck color="green" size={20} /> : <FaTimes color="red" size={20} />}
            </div>
            <div className="boss-info">
              <h4>{safeString(boss.name || "Boss")}</h4>
              <p className={`boss-state ${boss.alive ? 'alive' : 'dead'}`}>
                {boss.alive ? "Vivo" : "Morto"}
              </p>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}

function SiegeInfo({ siege }) {
  if (!siege) return null;

  return (
    <div className="siege-info">
      <div className="siege-header">
        <FaCrown size={24} color="#e6c77d" />
        <h3>Informações do Siege</h3>
      </div>
      <div className="siege-card">
        <div className="siege-status">
          <div className="siege-item">
            <span className="siege-label">Status:</span>
            <span className={`siege-value ${siege.active ? 'active' : 'inactive'}`}>
              {siege.active ? "Ativo" : "Inativo"}
            </span>
          </div>
          <div className="siege-item">
            <span className="siege-label">Castle:</span>
            <span className="siege-value">{safeString(siege.castle || "Nenhum")}</span>
          </div>
          <div className="siege-item">
            <span className="siege-label">Guild:</span>
            <span className="siege-value">{safeString(siege.guild || "Nenhuma")}</span>
          </div>
        </div>
      </div>
    </div>
  );
}

export default function ServerSection({ token }) {
  const [loading, setLoading] = useState(true);
  const [status, setStatus] = useState({ online: false, players: 0, uptime: 0, version: "1.0.0" });
  const [rankings, setRankings] = useState({ 
    level: [], 
    pvp: [], 
    guild: [], 
    pk: [], 
    rich: [], 
    online: [], 
    olympiad: [], 
    olympiadHeroes: [] 
  });
  const [bosses, setBosses] = useState({ grand: [] });
  const [siege, setSiege] = useState([]);
  const [error, setError] = useState("");

  useEffect(() => {
    async function fetchData() {
      setLoading(true);
      setError("");
      try {
        console.log("Buscando dados do servidor...");
        
        // Buscar dados individualmente
        const statusRes = await fetch("/api/v1/server/status/", { 
          headers: { Authorization: `Bearer ${token}` } 
        });
        const topLevelRes = await fetch("/api/v1/server/top-level/", { 
          headers: { Authorization: `Bearer ${token}` } 
        });
        const topPvpRes = await fetch("/api/v1/server/top-pvp/", { 
          headers: { Authorization: `Bearer ${token}` } 
        });
        const topPkRes = await fetch("/api/v1/server/top-pk/", { 
          headers: { Authorization: `Bearer ${token}` } 
        });
        const topRichRes = await fetch("/api/v1/server/top-rich/", { 
          headers: { Authorization: `Bearer ${token}` } 
        });
        const topOnlineRes = await fetch("/api/v1/server/top-online/", { 
          headers: { Authorization: `Bearer ${token}` } 
        });
        const topClanRes = await fetch("/api/v1/server/top-clan/", { 
          headers: { Authorization: `Bearer ${token}` } 
        });
        const olympiadRankingRes = await fetch("/api/v1/server/olympiad-ranking/", { 
          headers: { Authorization: `Bearer ${token}` } 
        });
        const olympiadHeroesRes = await fetch("/api/v1/server/olympiad-heroes/", { 
          headers: { Authorization: `Bearer ${token}` } 
        });
        const grandBossRes = await fetch("/api/v1/server/grandboss-status/", { 
          headers: { Authorization: `Bearer ${token}` } 
        });
        const siegeRes = await fetch("/api/v1/server/siege/", { 
          headers: { Authorization: `Bearer ${token}` } 
        });

        // Processar cada resposta
        if (statusRes.ok) {
          const statusData = await statusRes.json();
          console.log("Status data:", statusData);
          setStatus(statusData);
        } else {
          console.log("Status API não disponível:", statusRes.status);
          setStatus({ 
            online: false, 
            players: 0, 
            uptime: 0, 
            version: "1.0.0" 
          });
        }

        // Processar rankings
        if (topLevelRes.ok) {
          const topLevelData = await topLevelRes.json();
          console.log("Top level data:", topLevelData);
          setRankings(prev => ({ ...prev, level: topLevelData.results || topLevelData }));
        } else {
          console.log("Top level API não disponível:", topLevelRes.status);
          setRankings(prev => ({ ...prev, level: [] }));
        }

        if (topPvpRes.ok) {
          const topPvpData = await topPvpRes.json();
          console.log("Top PvP data:", topPvpData);
          setRankings(prev => ({ ...prev, pvp: topPvpData.results || topPvpData }));
        } else {
          console.log("Top PvP API não disponível:", topPvpRes.status);
          setRankings(prev => ({ ...prev, pvp: [] }));
        }

        if (topPkRes.ok) {
          const topPkData = await topPkRes.json();
          console.log("Top PK data:", topPkData);
          setRankings(prev => ({ ...prev, pk: topPkData.results || topPkData }));
        } else {
          console.log("Top PK API não disponível:", topPkRes.status);
          setRankings(prev => ({ ...prev, pk: [] }));
        }

        if (topRichRes.ok) {
          const topRichData = await topRichRes.json();
          console.log("Top Rich data:", topRichData);
          setRankings(prev => ({ ...prev, rich: topRichData.results || topRichData }));
        } else {
          console.log("Top Rich API não disponível:", topRichRes.status);
          setRankings(prev => ({ ...prev, rich: [] }));
        }

        if (topOnlineRes.ok) {
          const topOnlineData = await topOnlineRes.json();
          console.log("Top Online data:", topOnlineData);
          setRankings(prev => ({ ...prev, online: topOnlineData.results || topOnlineData }));
        } else {
          console.log("Top Online API não disponível:", topOnlineRes.status);
          setRankings(prev => ({ ...prev, online: [] }));
        }

        if (topClanRes.ok) {
          const topClanData = await topClanRes.json();
          console.log("Top clan data:", topClanData);
          setRankings(prev => ({ ...prev, guild: topClanData.results || topClanData }));
        } else {
          console.log("Top clan API não disponível:", topClanRes.status);
          setRankings(prev => ({ ...prev, guild: [] }));
        }

        // Processar dados da Olimpíada
        if (olympiadRankingRes.ok) {
          const olympiadRankingData = await olympiadRankingRes.json();
          console.log("Olympiad ranking data:", olympiadRankingData);
          setRankings(prev => ({ ...prev, olympiad: olympiadRankingData.results || olympiadRankingData }));
        } else {
          console.log("Olympiad ranking API não disponível:", olympiadRankingRes.status);
          setRankings(prev => ({ ...prev, olympiad: [] }));
        }

        if (olympiadHeroesRes.ok) {
          const olympiadHeroesData = await olympiadHeroesRes.json();
          console.log("Olympiad heroes data:", olympiadHeroesData);
          setRankings(prev => ({ ...prev, olympiadHeroes: olympiadHeroesData.results || olympiadHeroesData }));
        } else {
          console.log("Olympiad heroes API não disponível:", olympiadHeroesRes.status);
          setRankings(prev => ({ ...prev, olympiadHeroes: [] }));
        }

        // Buscar status dos bosses
        try {
          if (grandBossRes.ok) {
            const grandBossData = await grandBossRes.json();
            console.log("Grand boss data:", grandBossData);
            setBosses(prev => ({ ...prev, grand: grandBossData.results || grandBossData }));
          } else {
            console.log("Grand boss API não disponível:", grandBossRes.status);
            setBosses(prev => ({ ...prev, grand: [] }));
          }
        } catch (error) {
          console.log("Erro ao processar grand boss:", error.message);
          setBosses(prev => ({ ...prev, grand: [] }));
        }



        try {
          if (siegeRes.ok) {
            const siegeData = await siegeRes.json();
            console.log("Siege data:", siegeData);
            setSiege(siegeData.results || siegeData);
          } else {
            console.log("Siege API não disponível:", siegeRes.status);
            setSiege([]);
          }
        } catch (error) {
          console.log("Erro ao processar siege:", error.message);
          setSiege([]);
        }

      } catch (e) {
        console.log("Erro geral ao buscar dados do servidor:", e.message);
        setError("Erro ao buscar dados do servidor");
        // Dados padrão
        setStatus({ online: false, players: 0, uptime: 0, version: "1.0.0" });
        setRankings({ level: [], pvp: [], guild: [], pk: [], rich: [], online: [], olympiad: [], olympiadHeroes: [] });
        setBosses({ grand: [] });
        setSiege([]);
      }
      setLoading(false);
    }
    fetchData();
  }, [token]);

  if (loading) return <div className="loading">Carregando dados do servidor...</div>;

  return (
    <div className="server-section">
      {/* Status Cards */}
      <div className="server-status">
        <h2>Status do Servidor</h2>
        <div className="server-status-grid">
          <StatusCard
            title="Status"
            value={status?.online ? "Online" : "Offline"}
            icon={<FaServer size={24} />}
            color={status?.online ? "#28a745" : "#dc3545"}
            subtitle={status?.online ? "Servidor funcionando" : "Servidor indisponível"}
          />
          <StatusCard
            title="Jogadores"
            value={status?.players || "0"}
            icon={<FaUsers size={24} />}
            color="#17a2b8"
            subtitle="jogadores online"
          />
          <StatusCard
            title="Uptime"
            value={formatUptime(status?.uptime)}
            icon={<FaClock size={24} />}
            color="#ffc107"
            subtitle="tempo ativo"
          />
          <StatusCard
            title="Versão"
            value={status?.version || "1.0.0"}
            icon={<FaCode size={24} />}
            color="#6c757d"
            subtitle="versão atual"
          />
        </div>
      </div>

      {/* Rankings */}
      <div className="server-rankings">
        <RankingTable
          title="Ranking de Level"
          data={rankings.level || []}
          icon={<FaCrown />}
          emptyMessage="Nenhum ranking de level disponível"
        />
        <RankingTable
          title="Ranking PvP"
          data={rankings.pvp || []}
          icon={<FaTrophy />}
          emptyMessage="Nenhum ranking PvP disponível"
        />
        <RankingTable
          title="Ranking de Guild"
          data={rankings.guild || []}
          icon={<FaUsers />}
          emptyMessage="Nenhum ranking de guild disponível"
        />
        <RankingTable
          title="Ranking PK"
          data={rankings.pk || []}
          icon={<FaSkull />}
          emptyMessage="Nenhum ranking PK disponível"
        />
        <RankingTable
          title="Ranking Rico"
          data={rankings.rich || []}
          icon={<FaCoins />}
          emptyMessage="Nenhum ranking Rico disponível"
        />
        <RankingTable
          title="Ranking Online"
          data={rankings.online || []}
          icon={<FaClock />}
          emptyMessage="Nenhum ranking Online disponível"
        />
        <RankingTable
          title="Ranking da Olimpíada"
          data={rankings.olympiad || []}
          icon={<FaMedal />}
          emptyMessage="Nenhum ranking da Olimpíada disponível"
        />
        <RankingTable
          title="Heróis da Olimpíada"
          data={rankings.olympiadHeroes || []}
          icon={<FaDragon />}
          emptyMessage="Nenhum herói da Olimpíada disponível"
        />
      </div>

      {/* Bosses */}
      <div className="server-bosses">
        <h3>Status dos Bosses</h3>
        <div className="boss-grid">
          {(bosses.grand || []).map((boss, index) => (
            <div key={index} className="boss-card">
              <div className="boss-header">
                <FaDragon size={16} color={boss.is_alive ? "#28a745" : "#dc3545"} />
                <h4>{safeString(boss.boss_name)}</h4>
              </div>
              <div className="boss-status">
                <span className={`status ${boss.is_alive ? 'alive' : 'dead'}`}>
                  {boss.is_alive ? 'Vivo' : 'Morto'}
                </span>
                {boss.respawn_time && (
                  <div className="respawn-time">
                    Respawn: {formatDate(boss.respawn_time)}
                  </div>
                )}
                {boss.location && (
                  <div className="boss-location">
                    Local: {safeString(boss.location)}
                  </div>
                )}
              </div>
            </div>
          ))}

        </div>
      </div>

      {/* Siege */}
      <div className="server-siege">
        <h3>Informações do Siege</h3>
        <div className="siege-info">
          {(siege || []).map((castle, index) => (
            <div key={index} className="castle-card">
              <div className="castle-header">
                <FaCrown size={16} color="#e6c77d" />
                <h4>{safeString(castle.castle_name)}</h4>
              </div>
              <div className="castle-details">
                <div className="castle-owner">
                  <strong>Proprietário:</strong> {safeString(castle.owner_clan) || "Nenhum"}
                </div>
                <div className="castle-status">
                  <span className={`status ${castle.is_under_siege ? 'under-siege' : 'peace'}`}>
                    {castle.is_under_siege ? 'Sob Cerco' : 'Em Paz'}
                  </span>
                </div>
                {castle.siege_date && (
                  <div className="siege-date">
                    Próximo Cerco: {formatDate(castle.siege_date)}
                  </div>
                )}
              </div>
            </div>
          ))}
        </div>
      </div>

      {error && <div className="error">{error}</div>}
    </div>
  );
} 