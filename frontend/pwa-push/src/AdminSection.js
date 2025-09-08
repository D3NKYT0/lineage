import React, { useEffect, useState } from "react";
import { FaCogs, FaExternalLinkAlt, FaCheck, FaTimes, FaServer, FaUser, FaSearch, FaChartBar, FaShieldAlt } from "react-icons/fa";

function ConfigEndpoints({ data }) {
  if (!data || !data.endpoints) return null;
  
  const categories = {
    server: { icon: <FaServer />, label: "Servidor", color: "#e6c77d" },
    user: { icon: <FaUser />, label: "Usuário", color: "#28a745" },
    search: { icon: <FaSearch />, label: "Busca", color: "#17a2b8" },
    metrics: { icon: <FaChartBar />, label: "Métricas", color: "#ffc107" },
    admin: { icon: <FaShieldAlt />, label: "Administração", color: "#dc3545" }
  };

  return (
    <div className="admin-config-endpoints">
      {Object.entries(data.endpoints).map(([endpoint, status]) => {
        const category = Object.keys(categories).find(cat => endpoint.includes(cat)) || 'server';
        const catInfo = categories[category];
        
        return (
          <div key={endpoint} className="endpoint-config-item">
            <div className="endpoint-info">
              <div className="endpoint-icon" style={{ color: catInfo.color }}>
                {catInfo.icon}
              </div>
              <div className="endpoint-details">
                <div className="endpoint-name">{endpoint}</div>
                <div className="endpoint-category">{catInfo.label}</div>
              </div>
            </div>
            <div className={`endpoint-status ${status ? 'active' : 'inactive'}`}>
              {status ? <FaCheck /> : <FaTimes />}
              <span>{status ? 'Ativo' : 'Inativo'}</span>
            </div>
          </div>
        );
      })}
    </div>
  );
}

function ConfigCategories({ data }) {
  if (!data || !data.categories) return null;
  
  return (
    <div className="admin-config-categories">
      <h3>Categorias de Endpoints</h3>
      <div className="categories-grid">
        {Object.entries(data.categories).map(([category, count]) => (
          <div key={category} className="category-card">
            <div className="category-name">{category}</div>
            <div className="category-count">{count} endpoints</div>
          </div>
        ))}
      </div>
    </div>
  );
}

export default function AdminSection({ token }) {
  const [config, setConfig] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    fetchConfig();
  }, []);

  async function fetchConfig() {
    setLoading(true);
    setError("");
    try {
      const res = await fetch("/api/v1/admin/config/", {
        headers: { Authorization: `Bearer ${token}` }
      });
      const data = await res.json();
      setConfig(data);
    } catch (e) {
      setError("Erro ao buscar configurações");
    }
    setLoading(false);
  }

  function openConfigPanel() {
    window.open("/api/v1/admin/config/panel/", "_blank");
  }

  if (loading) return <div>Carregando configurações...</div>;
  if (error) return <div className="error">{error}</div>;

  return (
    <div className="admin-section">
      <div className="admin-config-box">
        <div className="admin-config-header">
          <div className="admin-config-icon">
            <FaCogs size={28} color="#e6c77d" />
          </div>
          <h2>Configurações da API</h2>
        </div>
        {config && (
          <div className="admin-config-content">
            <ConfigCategories data={config} />
            <ConfigEndpoints data={config} />
            {config.last_updated && (
              <div className="config-last-updated">
                Última atualização: {new Date(config.last_updated).toLocaleString()}
              </div>
            )}
          </div>
        )}
      </div>

      <div className="admin-panel-box">
        <h2>Painel de Configuração</h2>
        <p>Clique no botão abaixo para abrir o painel de configuração em uma nova aba:</p>
        <button className="btn-primary admin-panel-btn" onClick={openConfigPanel}>
          <FaExternalLinkAlt />
          Abrir Painel de Configuração
        </button>
      </div>
    </div>
  );
} 