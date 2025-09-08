import React, { useEffect, useState } from "react";
import { FaChartLine, FaClock, FaExclamationTriangle, FaServer, FaDatabase, FaChartBar, FaTachometerAlt, FaHistory } from "react-icons/fa";

// Função para converter qualquer valor em string segura
function safeString(value) {
  if (value === null || value === undefined) return "";
  if (typeof value === "object") return JSON.stringify(value);
  return String(value);
}

// Função para formatar timestamp
function formatTimestamp(timestamp) {
  if (!timestamp) return "N/A";
  try {
    const date = new Date(timestamp);
    return date.toLocaleString('pt-BR');
  } catch (e) {
    return timestamp;
  }
}

// Função para formatar números
function formatNumber(num) {
  if (num === null || num === undefined) return "0";
  if (typeof num === 'string') return num;
  return num.toLocaleString('pt-BR');
}

// Função para formatar tempo de resposta
function formatResponseTime(time) {
  if (!time || time === 0) return "0ms";
  if (time < 1000) return `${time}ms`;
  return `${(time / 1000).toFixed(2)}s`;
}

function MetricsCard({ title, value, subtitle, icon, color = "#e6c77d", trend = null }) {
  return (
    <div className="metrics-card" style={{ borderColor: color }}>
      <div className="metrics-icon" style={{ color }}>
        {icon}
      </div>
      <div className="metrics-info">
        <h3>{title}</h3>
        <p className="metrics-value">{value}</p>
        {subtitle && <p className="metrics-subtitle">{subtitle}</p>}
        {trend && (
          <div className={`metrics-trend ${trend > 0 ? 'positive' : 'negative'}`}>
            {trend > 0 ? '↗' : '↘'} {Math.abs(trend)}%
          </div>
        )}
      </div>
    </div>
  );
}

function MetricsGrid({ title, data, icon, emptyMessage = "Nenhum dado disponível" }) {
  if (!data || Object.keys(data).length === 0) {
    return (
      <div className="metrics-grid">
        <div className="metrics-header">
          <div className="metrics-header-icon">{icon}</div>
          <h3>{title}</h3>
        </div>
        <div className="metrics-empty">
          <div className="empty-icon">📊</div>
          <p>{emptyMessage}</p>
        </div>
      </div>
    );
  }

  const metrics = [
    { key: "total_requests", label: "Total de Requisições", icon: <FaServer size={16} />, color: "#17a2b8" },
    { key: "avg_response_time", label: "Tempo Médio", icon: <FaClock size={16} />, color: "#ffc107" },
    { key: "error_rate", label: "Taxa de Erro", icon: <FaExclamationTriangle size={16} />, color: "#dc3545" }
  ];

  return (
    <div className="metrics-grid">
      <div className="metrics-header">
        <div className="metrics-header-icon">{icon}</div>
        <h3>{title}</h3>
        <span className="metrics-timestamp">
          {data.timestamp && formatTimestamp(data.timestamp)}
        </span>
      </div>
      <div className="metrics-cards">
        {metrics.map(metric => (
          <MetricsCard
            key={metric.key}
            title={metric.label}
            value={
              metric.key === "avg_response_time" 
                ? formatResponseTime(data[metric.key])
                : metric.key === "error_rate"
                ? `${formatNumber(data[metric.key] || 0)}%`
                : formatNumber(data[metric.key] || 0)
            }
            icon={metric.icon}
            color={metric.color}
            subtitle={
              metric.key === "total_requests" ? "requisições" :
              metric.key === "avg_response_time" ? "tempo de resposta" :
              "erros por 100 req"
            }
          />
        ))}
      </div>
    </div>
  );
}

function StatusCodesTable({ statusCodes }) {
  if (!statusCodes || Object.keys(statusCodes).length === 0) {
    return (
      <div className="status-codes-section">
        <h4>Status Codes</h4>
        <div className="status-codes-empty">
          <p>Nenhum status code registrado</p>
        </div>
      </div>
    );
  }

  const statusColors = {
    "200": "#28a745",
    "201": "#28a745", 
    "400": "#ffc107",
    "401": "#fd7e14",
    "403": "#fd7e14",
    "404": "#dc3545",
    "500": "#dc3545"
  };

  return (
    <div className="status-codes-section">
      <h4>Status Codes</h4>
      <div className="status-codes-grid">
        {Object.entries(statusCodes).map(([code, count]) => (
          <div key={code} className="status-code-item" style={{ borderColor: statusColors[code] || "#6c757d" }}>
            <span className="status-code">{code}</span>
            <span className="status-count">{formatNumber(count)}</span>
          </div>
        ))}
      </div>
    </div>
  );
}

function EndpointsTable({ endpoints }) {
  if (!endpoints || Object.keys(endpoints).length === 0) {
    return (
      <div className="endpoints-section">
        <h4>Endpoints Mais Acessados</h4>
        <div className="endpoints-empty">
          <p>Nenhum endpoint registrado</p>
        </div>
      </div>
    );
  }

  const sortedEndpoints = Object.entries(endpoints)
    .sort(([,a], [,b]) => b - a)
    .slice(0, 10);

  return (
    <div className="endpoints-section">
      <h4>Endpoints Mais Acessados</h4>
      <div className="endpoints-list">
        {sortedEndpoints.map(([endpoint, count], index) => (
          <div key={endpoint} className="endpoint-item">
            <div className="endpoint-rank">#{index + 1}</div>
            <div className="endpoint-path">{endpoint}</div>
            <div className="endpoint-count">{formatNumber(count)}</div>
          </div>
        ))}
      </div>
    </div>
  );
}

function SlowQueriesTable({ slowQueries }) {
  if (!slowQueries || slowQueries.length === 0) {
    return (
      <div className="slow-queries-section">
        <div className="slow-queries-header">
          <FaDatabase size={20} color="#e6c77d" />
          <h4>Queries Lentas</h4>
        </div>
        <div className="slow-queries-empty">
          <div className="empty-icon">🐌</div>
          <p>Nenhuma query lenta registrada</p>
        </div>
      </div>
    );
  }

  return (
    <div className="slow-queries-section">
      <div className="slow-queries-header">
        <FaDatabase size={20} color="#e6c77d" />
        <h4>Queries Lentas</h4>
        <span className="slow-queries-count">{slowQueries.length} queries</span>
      </div>
      <div className="slow-queries-list">
        {slowQueries.map((query, index) => (
          <div key={index} className="slow-query-item">
            <div className="query-header">
              <span className="query-number">#{index + 1}</span>
              <span className="query-time">{formatResponseTime(query.execution_time || query.time)}</span>
            </div>
            <div className="query-sql">{safeString(query.sql || query.query)}</div>
            {query.count && (
              <div className="query-count">Executada {formatNumber(query.count)} vezes</div>
            )}
          </div>
        ))}
      </div>
    </div>
  );
}

export default function MetricsSection({ token }) {
  const [health, setHealth] = useState(null);
  const [hourly, setHourly] = useState(null);
  const [daily, setDaily] = useState(null);
  const [performance, setPerformance] = useState(null);
  const [slowQueries, setSlowQueries] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    async function fetchData() {
      setLoading(true);
      setError("");
      try {
        console.log("Buscando dados de métricas...");
        
        // Buscar dados individualmente
        const healthRes = await fetch("/api/v1/health/", { 
          headers: { Authorization: `Bearer ${token}` } 
        });
        const hourlyRes = await fetch("/api/v1/metrics/hourly/", { 
          headers: { Authorization: `Bearer ${token}` } 
        });
        const dailyRes = await fetch("/api/v1/metrics/daily/", { 
          headers: { Authorization: `Bearer ${token}` } 
        });
        const performanceRes = await fetch("/api/v1/metrics/performance/", { 
          headers: { Authorization: `Bearer ${token}` } 
        });
        const slowQueriesRes = await fetch("/api/v1/metrics/slow-queries/", { 
          headers: { Authorization: `Bearer ${token}` } 
        });

        // Processar cada resposta
        if (healthRes.ok) {
          const healthData = await healthRes.json();
          console.log("Health data:", healthData);
          setHealth(healthData);
        } else {
          console.warn("Erro ao buscar health:", healthRes.status);
          setHealth({ status: "healthy", uptime: 0 });
        }

        if (hourlyRes.ok) {
          const hourlyData = await hourlyRes.json();
          console.log("Hourly data:", hourlyData);
          setHourly(hourlyData);
        } else {
          console.warn("Erro ao buscar hourly:", hourlyRes.status);
          setHourly({ success: true, data: {}, timestamp: new Date().toISOString() });
        }

        if (dailyRes.ok) {
          const dailyData = await dailyRes.json();
          console.log("Daily data:", dailyData);
          setDaily(dailyData);
        } else {
          console.warn("Erro ao buscar daily:", dailyRes.status);
          setDaily({ success: true, data: {}, timestamp: new Date().toISOString() });
        }

        if (performanceRes.ok) {
          const performanceData = await performanceRes.json();
          console.log("Performance data:", performanceData);
          setPerformance(performanceData);
        } else {
          console.warn("Erro ao buscar performance:", performanceRes.status);
          setPerformance({ success: true, data: {} });
        }

        if (slowQueriesRes.ok) {
          const slowQueriesData = await slowQueriesRes.json();
          console.log("Slow queries data:", slowQueriesData);
          setSlowQueries(slowQueriesData);
        } else {
          console.warn("Erro ao buscar slow queries:", slowQueriesRes.status);
          setSlowQueries({ success: true, data: { slow_queries: [], count: 0 } });
        }

      } catch (e) {
        console.error("Erro ao buscar dados de métricas:", e);
        setError("Erro ao buscar dados de métricas");
        // Dados padrão
        setHealth({ status: "healthy", uptime: 0 });
        setHourly({ success: true, data: {}, timestamp: new Date().toISOString() });
        setDaily({ success: true, data: {}, timestamp: new Date().toISOString() });
        setPerformance({ success: true, data: {} });
        setSlowQueries({ success: true, data: { slow_queries: [], count: 0 } });
      }
      setLoading(false);
    }
    fetchData();
  }, [token]);

  if (loading) return <div className="loading">Carregando métricas...</div>;

  return (
    <div className="metrics-section">
      {/* Health Check */}
      {health && (
        <div className="health-check">
          <div className="health-header">
            <FaTachometerAlt size={24} color="#e6c77d" />
            <h3>Status do Sistema</h3>
          </div>
          <div className="health-cards">
            <MetricsCard
              title="Status"
              value={health.status === "healthy" ? "Saudável" : "Problemas"}
              icon={<FaServer size={24} />}
              color={health.status === "healthy" ? "#28a745" : "#dc3545"}
              subtitle="estado atual"
            />
            <MetricsCard
              title="Uptime"
              value={formatResponseTime(health.uptime * 1000)}
              icon={<FaHistory size={24} />}
              color="#17a2b8"
              subtitle="tempo ativo"
            />
          </div>
        </div>
      )}

      {/* Métricas por Hora */}
      <MetricsGrid
        title="Métricas por Hora"
        data={hourly?.data || {}}
        icon={<FaChartLine size={24} color="#e6c77d" />}
        emptyMessage="Nenhuma métrica horária disponível"
      />

      {/* Métricas Diárias */}
      <MetricsGrid
        title="Métricas Diárias"
        data={daily?.data || {}}
        icon={<FaChartBar size={24} color="#e6c77d" />}
        emptyMessage="Nenhuma métrica diária disponível"
      />

      {/* Status Codes e Endpoints */}
      {(hourly?.data?.status_codes || daily?.data?.status_codes || hourly?.data?.endpoints || daily?.data?.endpoints) && (
        <div className="metrics-details">
          <div className="metrics-details-grid">
            <StatusCodesTable statusCodes={hourly?.data?.status_codes || daily?.data?.status_codes} />
            <EndpointsTable endpoints={hourly?.data?.endpoints || daily?.data?.endpoints} />
          </div>
        </div>
      )}

      {/* Performance por Endpoint */}
      {performance && (
        <div className="performance-section">
          <div className="performance-header">
            <FaTachometerAlt size={24} color="#e6c77d" />
            <h3>Performance por Endpoint</h3>
          </div>
          <div className="performance-content">
            {performance.data && Object.keys(performance.data).length > 0 ? (
              <div className="performance-list">
                {Object.entries(performance.data).map(([endpoint, data]) => (
                  <div key={endpoint} className="performance-item">
                    <div className="performance-endpoint">{endpoint}</div>
                    <div className="performance-metrics">
                      <span className="performance-time">{formatResponseTime(data.avg_time || 0)}</span>
                      <span className="performance-count">{formatNumber(data.count || 0)} req</span>
                    </div>
                  </div>
                ))}
              </div>
            ) : (
              <div className="performance-empty">
                <div className="empty-icon">⚡</div>
                <p>Nenhum dado de performance disponível</p>
              </div>
            )}
          </div>
        </div>
      )}

      {/* Queries Lentas */}
      <SlowQueriesTable slowQueries={slowQueries?.data?.slow_queries || []} />

      {error && <div className="error">{error}</div>}
    </div>
  );
} 