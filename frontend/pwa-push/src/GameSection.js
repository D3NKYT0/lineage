import React, { useState, useEffect } from "react";
import { FaUsers, FaSearch, FaSync, FaGavel, FaClock, FaTag, FaShieldAlt } from "react-icons/fa";

// Função para converter qualquer valor em string segura
function safeString(value) {
  if (value === null || value === undefined) return "N/A";
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

// Função para formatar números
function formatNumber(num) {
  if (!num || num === 0) return "0";
  if (num >= 1000000000) return `${(num / 1000000000).toFixed(1)}B`;
  if (num >= 1000000) return `${(num / 1000000).toFixed(1)}M`;
  if (num >= 1000) return `${(num / 1000).toFixed(1)}K`;
  return num.toString();
}

function ClanCard({ data }) {
  if (!data) return null;

  const fields = [
    { key: "clan_name", label: "Nome", icon: <FaUsers size={16} />, color: "#e6c77d" },
    { key: "leader_name", label: "Líder", icon: <FaUsers size={16} />, color: "#28a745" },
    { key: "level", label: "Nível", icon: <FaUsers size={16} />, color: "#007bff" },
    { key: "member_count", label: "Membros", icon: <FaUsers size={16} />, color: "#17a2b8" },
    { key: "reputation", label: "Reputação", icon: <FaShieldAlt size={16} />, color: "#28a745" }
  ];

  return (
    <div className="clan-card">
      <div className="clan-header">
        <FaUsers size={20} color="#e6c77d" />
        <h4>{safeString(data.clan_name)}</h4>
      </div>
      <div className="clan-details">
        {fields.map((field) => (
          <div key={field.key} className="clan-field">
            <div className="field-icon" style={{ color: field.color }}>
              {field.icon}
            </div>
            <div className="field-info">
              <div className="field-label">{field.label}</div>
              <div className="field-value">{safeString(data[field.key])}</div>
            </div>
          </div>
        ))}
        {data.ally_name && (
          <div className="clan-field">
            <div className="field-icon" style={{ color: "#ffc107" }}>
              <FaUsers size={16} />
            </div>
            <div className="field-info">
              <div className="field-label">Aliança</div>
              <div className="field-value">{safeString(data.ally_name)}</div>
            </div>
          </div>
        )}
        {data.creation_date && (
          <div className="clan-field">
            <div className="field-icon" style={{ color: "#6c757d" }}>
              <FaClock size={16} />
            </div>
            <div className="field-info">
              <div className="field-label">Criado em</div>
              <div className="field-value">{formatDate(data.creation_date)}</div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}

function AuctionGrid({ items }) {
  if (!Array.isArray(items) || items.length === 0) {
    return (
      <div className="auction-empty">
        <div className="empty-icon">🏷️</div>
        <p>Nenhum item disponível no leilão</p>
      </div>
    );
  }

  return (
    <div className="auction-grid">
      {items.slice(0, 20).map((item, index) => (
        <div key={index} className="auction-card">
          <div className="auction-header">
            <FaTag size={16} color="#e6c77d" />
            <h4>{safeString(item.item_name)}</h4>
          </div>
          <div className="auction-details">
            <div className="auction-field">
              <span className="field-label">Vendedor:</span>
              <span className="field-value">{safeString(item.seller_name)}</span>
            </div>
            <div className="auction-field">
              <span className="field-label">Lance Atual:</span>
              <span className="field-value">{formatNumber(item.current_bid)}</span>
            </div>
            <div className="auction-field">
              <span className="field-label">Lance Mínimo:</span>
              <span className="field-value">{formatNumber(item.min_bid)}</span>
            </div>
            <div className="auction-field">
              <span className="field-label">Quantidade:</span>
              <span className="field-value">{safeString(item.item_count)}</span>
            </div>
            {item.item_grade && (
              <div className="auction-field">
                <span className="field-label">Grau:</span>
                <span className="field-value">{safeString(item.item_grade)}</span>
              </div>
            )}
            {item.item_enchant && (
              <div className="auction-field">
                <span className="field-label">Encantamento:</span>
                <span className="field-value">+{safeString(item.item_enchant)}</span>
              </div>
            )}
            <div className="auction-field">
              <span className="field-label">Termina em:</span>
              <span className="field-value">{formatDate(item.end_time)}</span>
            </div>
          </div>
        </div>
      ))}
    </div>
  );
}

export default function GameSection({ token }) {
  const [loading, setLoading] = useState(true);
  const [auctionItems, setAuctionItems] = useState([]);
  const [clanName, setClanName] = useState("");
  const [clanData, setClanData] = useState(null);
  const [searching, setSearching] = useState(false);
  const [error, setError] = useState("");

  useEffect(() => {
    if (token) {
      fetchGameData();
    }
  }, [token]);

  async function fetchGameData() {
    if (!token) return;
    
    setLoading(true);
    setError("");
    
    try {
      console.log("Buscando dados do jogo...");

      // Buscar dados individualmente
      const auctionRes = await fetch("/api/v1/auction/items/", {
        headers: { Authorization: `Bearer ${token}` }
      });

      // Processar cada resposta
      if (auctionRes.ok) {
        const auctionData = await auctionRes.json();
        console.log("Auction data:", auctionData);
        setAuctionItems(auctionData);
      } else {
        console.warn("Erro ao buscar leilão:", auctionRes.status);
        setAuctionItems([]);
      }

    } catch (e) {
      console.error("Erro ao buscar dados do jogo:", e);
      setError("Erro ao carregar dados do jogo");
      setAuctionItems([]);
    }
    setLoading(false);
  }

  async function searchClan() {
    if (!clanName.trim() || !token) return;
    
    setSearching(true);
    setError("");
    
    try {
      console.log("Buscando clã:", clanName);
      
      const res = await fetch(`/api/v1/clan/${encodeURIComponent(clanName)}/`, {
        headers: { Authorization: `Bearer ${token}` }
      });

      if (res.ok) {
        const data = await res.json();
        console.log("Clan data:", data);
        setClanData(data);
      } else {
        console.warn("Erro ao buscar clã:", res.status);
        setClanData(null);
        setError("Clã não encontrado");
      }
    } catch (e) {
      console.error("Erro ao buscar clã:", e);
      setError("Erro ao buscar clã");
      setClanData(null);
    }
    setSearching(false);
  }

  if (loading) {
    return (
      <div className="game-section">
        <h2>Dados do Jogo</h2>
        <div className="loading">Carregando dados do jogo...</div>
      </div>
    );
  }

  return (
    <div className="game-section">
      <h2>Dados do Jogo</h2>

      {error && <div className="error">{error}</div>}

      {/* Busca de Clã */}
      <div className="game-clan-section">
        <div className="clan-header">
          <FaUsers size={20} color="#e6c77d" />
          <h3>Busca de Clã</h3>
        </div>
        <div className="clan-search">
          <input
            type="text"
            placeholder="Digite o nome do clã..."
            value={clanName}
            onChange={e => setClanName(e.target.value)}
            className="clan-input"
          />
          <button 
            onClick={searchClan} 
            disabled={searching}
            className="btn-primary"
          >
            <FaSearch size={14} />
            {searching ? "Buscando..." : "Buscar"}
          </button>
        </div>
        {clanData && (
          <ClanCard data={clanData} />
        )}
      </div>

      {/* Leilão */}
      <div className="game-auction-section">
        <div className="auction-header">
          <FaGavel size={20} color="#e6c77d" />
          <h3>Itens do Leilão</h3>
          <button className="btn-secondary refresh-btn" onClick={fetchGameData} disabled={loading}>
            <FaSync size={14} />
            {loading ? "Carregando..." : "Atualizar"}
          </button>
        </div>
        <AuctionGrid items={auctionItems} />
      </div>
    </div>
  );
} 