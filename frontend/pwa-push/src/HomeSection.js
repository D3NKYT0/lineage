import React, { useEffect, useState } from "react";
import {
    FaServer, FaUsers, FaClock, FaCode, FaUser, FaSearch,
    FaGamepad, FaChartBar, FaCogs, FaBell, FaDiscord,
    FaStar, FaTrophy, FaSkull, FaShieldAlt
} from "react-icons/fa";
import { apiFetch } from "./api";
import { useServer } from "./ServerContext";

function formatUptime(uptime) {
    if (!uptime) return "—";
    if (typeof uptime === "string") return uptime;
    if (typeof uptime === "number") {
        const h = Math.floor(uptime / 3600);
        const d = Math.floor(h / 24);
        if (d > 0) return `${d}d ${h % 24}h`;
        return `${h}h`;
    }
    return uptime;
}

function StatWidget({ icon, label, value, color = "var(--pdl-gold)", pulse = false }) {
    return (
        <div className="home-stat-widget">
            <div className="home-stat-icon" style={{ color }}>
                {pulse && <span className="pulse-ring" style={{ borderColor: color }}></span>}
                {icon}
            </div>
            <div className="home-stat-body">
                <div className="home-stat-value">{value ?? "—"}</div>
                <div className="home-stat-label">{label}</div>
            </div>
        </div>
    );
}

function QuickCard({ icon, label, description, onClick, active }) {
    return (
        <button
            type="button"
            className={`home-quick-card ${active ? "home-quick-card--active" : ""}`}
            onClick={onClick}
            aria-label={label}
        >
            <span className="home-quick-card-icon">{icon}</span>
            <span className="home-quick-card-label">{label}</span>
            <span className="home-quick-card-desc">{description}</span>
        </button>
    );
}

function TopMiniList({ title, icon, items, valueKey, nameKey = "char_name" }) {
    if (!Array.isArray(items) || items.length === 0) return null;
    const medals = ["🥇", "🥈", "🥉"];
    return (
        <div className="home-mini-ranking">
            <div className="home-mini-ranking-header">
                {icon}
                <span>{title}</span>
            </div>
            <ul className="home-mini-ranking-list">
                {items.slice(0, 3).map((item, i) => (
                    <li key={i} className="home-mini-ranking-item">
                        <span className="home-mini-medal">{medals[i]}</span>
                        <span className="home-mini-name">{item[nameKey] || "—"}</span>
                        <span className="home-mini-value">{item[valueKey] ?? "—"}</span>
                    </li>
                ))}
            </ul>
        </div>
    );
}

const QUICK_SECTIONS = [
    { key: "user", icon: <FaUser />, label: "Usuário", description: "Perfil e stats" },
    { key: "server", icon: <FaServer />, label: "Servidor", description: "Rankings e bosses" },
    { key: "search", icon: <FaSearch />, label: "Busca", description: "Personagens e itens" },
    { key: "game", icon: <FaGamepad />, label: "Jogo", description: "Clã e leilão" },
    { key: "metrics", icon: <FaChartBar />, label: "Métricas", description: "Performance da API" },
    { key: "admin", icon: <FaCogs />, label: "Admin", description: "Configurações" },
    { key: "push", icon: <FaBell />, label: "Notificações", description: "Push e alertas" },
];

export default function HomeSection({ token, onNavigate, activeSection }) {
    const { info } = useServer();
    const [serverStatus, setServerStatus] = useState(null);
    const [topPvp, setTopPvp] = useState([]);
    const [topLevel, setTopLevel] = useState([]);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        let cancelled = false;
        async function load() {
            try {
                const [statusRes, pvpRes, levelRes] = await Promise.allSettled([
                    apiFetch("/api/v1/server/status/"),
                    apiFetch("/api/v1/server/top-pvp/?limit=3"),
                    apiFetch("/api/v1/server/top-level/?limit=3"),
                ]);

                if (!cancelled) {
                    if (statusRes.status === "fulfilled" && statusRes.value.ok) {
                        setServerStatus(await statusRes.value.json());
                    }
                    if (pvpRes.status === "fulfilled" && pvpRes.value.ok) {
                        const d = await pvpRes.value.json();
                        setTopPvp(Array.isArray(d) ? d : (d.results || []));
                    }
                    if (levelRes.status === "fulfilled" && levelRes.value.ok) {
                        const d = await levelRes.value.json();
                        setTopLevel(Array.isArray(d) ? d : (d.results || []));
                    }
                }
            } catch (_) { }
            if (!cancelled) setLoading(false);
        }
        load();
        return () => { cancelled = true; };
    }, [token]);

    const isOnline = serverStatus?.online ?? serverStatus?.status === "online";

    return (
        <div className="home-section">
            {/* Hero */}
            <div className="home-hero">
                <div className="home-hero-logo-wrap">
                    <img src={info.logo_url || "/static/pwa/icons/logo.png"} alt="" className="home-hero-logo" />
                </div>
                <div className="home-hero-text">
                    <h1 className="home-hero-title">{info.name}</h1>
                    {info.chronicle && <span className="home-hero-badge">{info.chronicle}</span>}
                    {info.description && <p className="home-hero-desc">{info.description}</p>}
                </div>
            </div>

            {/* Status widgets */}
            <div className="home-stats-row">
                <StatWidget
                    icon={<FaServer size={22} />}
                    label="Status"
                    value={loading ? "…" : isOnline ? "Online" : "Offline"}
                    color={loading ? "var(--pdl-gold)" : isOnline ? "#4caf50" : "#e57373"}
                    pulse={!loading && isOnline}
                />
                <StatWidget
                    icon={<FaUsers size={22} />}
                    label="Jogadores"
                    value={loading ? "…" : serverStatus?.players ?? serverStatus?.players_online ?? "—"}
                    color="#29b6f6"
                />
                <StatWidget
                    icon={<FaClock size={22} />}
                    label="Uptime"
                    value={loading ? "…" : formatUptime(serverStatus?.uptime)}
                    color="#ffb300"
                />
                <StatWidget
                    icon={<FaCode size={22} />}
                    label="Versão"
                    value={info.version || "—"}
                    color="#ce93d8"
                />
            </div>

            {/* Quick navigation cards */}
            <div className="home-section-block">
                <h2 className="home-section-title">Navegação Rápida</h2>
                <div className="home-quick-grid">
                    {QUICK_SECTIONS.map((s) => (
                        <QuickCard
                            key={s.key}
                            icon={s.icon}
                            label={s.label}
                            description={s.description}
                            onClick={() => onNavigate(s.key)}
                            active={activeSection === s.key}
                        />
                    ))}
                </div>
            </div>

            {/* Mini rankings */}
            {(topPvp.length > 0 || topLevel.length > 0) && (
                <div className="home-section-block">
                    <h2 className="home-section-title">Top Rankings</h2>
                    <div className="home-rankings-row">
                        <TopMiniList
                            title="Top PvP"
                            icon={<FaShieldAlt size={14} color="var(--pdl-gold)" />}
                            items={topPvp}
                            valueKey="pvp_count"
                        />
                        <TopMiniList
                            title="Top Level"
                            icon={<FaStar size={14} color="var(--pdl-gold)" />}
                            items={topLevel}
                            valueKey="level"
                        />
                    </div>
                </div>
            )}

            {/* Social links */}
            {info.discord_url && info.discord_url !== "https://discord.gg/seu-link-aqui" && (
                <div className="home-section-block home-social-row">
                    <a href={info.discord_url} target="_blank" rel="noopener noreferrer" className="home-social-link home-social-link--discord">
                        <FaDiscord size={18} />
                        <span>Discord</span>
                    </a>
                </div>
            )}
        </div>
    );
}
