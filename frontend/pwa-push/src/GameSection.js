import React, { useState, useEffect, useCallback } from "react";
import {
  FaCoins, FaShoppingCart, FaTrophy, FaUsers, FaSearch,
  FaGavel, FaSync, FaStar, FaGamepad, FaBoxOpen,
  FaShieldAlt, FaDice, FaCrown, FaClock, FaTag
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
function fmtDate(d) {
  if (!d) return "—";
  try { return new Date(d).toLocaleString("pt-BR"); } catch { return d; }
}

/* ===== WALLET CARD ===== */
function WalletCard({ wallet, fichas }) {
  return (
    <div className="game-wallet-card pwa-card">
      <div className="game-section-header">
        <FaCoins size={20} color="var(--pdl-gold)" />
        <h3>Carteira PDL</h3>
      </div>
      <div className="game-wallet-grid">
        <div className="game-wallet-item">
          <span className="wallet-label">Saldo</span>
          <span className="wallet-value gold">{fmtBRL(wallet?.saldo)}</span>
        </div>
        <div className="game-wallet-item">
          <span className="wallet-label">Bônus</span>
          <span className="wallet-value green">{fmtBRL(wallet?.saldo_bonus)}</span>
        </div>
        <div className="game-wallet-item">
          <span className="wallet-label">Total</span>
          <span className="wallet-value highlight">{fmtBRL(wallet?.total)}</span>
        </div>
        <div className="game-wallet-item">
          <span className="wallet-label"><FaTag size={11} /> Fichas</span>
          <span className="wallet-value blue">{fmt(fichas)}</span>
        </div>
      </div>
    </div>
  );
}

/* ===== ACHIEVEMENTS ===== */
function AchievementsCard({ achievements }) {
  if (!achievements) return null;
  const pct = achievements.pct || 0;
  return (
    <div className="game-achievements-card pwa-card">
      <div className="game-section-header">
        <FaTrophy size={20} color="var(--pdl-gold)" />
        <h3>Conquistas</h3>
        <span className="game-badge">{achievements.count} / {achievements.total}</span>
      </div>
      <div className="game-progress-track">
        <div className="game-progress-fill" style={{ width: `${pct}%` }} />
      </div>
      <div className="game-progress-label">{pct}% concluídas</div>
    </div>
  );
}

/* ===== BATTLE PASS ===== */
function BattlePassCard({ battlePass }) {
  if (!battlePass) return null;
  return (
    <div className="game-bp-card pwa-card">
      <div className="game-section-header">
        <FaCrown size={20} color="var(--pdl-gold)" />
        <h3>Battle Pass</h3>
        <span className="game-badge active">Ativo</span>
      </div>
      <div className="game-bp-body">
        <div className="game-bp-season">{battlePass.season_name}</div>
        <div className="game-bp-stats">
          <div className="game-bp-stat">
            <span className="label">Nível</span>
            <span className="value">{battlePass.level}</span>
          </div>
          <div className="game-bp-stat">
            <span className="label">XP</span>
            <span className="value">{fmt(battlePass.xp)}</span>
          </div>
        </div>
      </div>
    </div>
  );
}

/* ===== GAMES CARD ===== */
function GamesCard({ games }) {
  if (!games) return null;
  return (
    <div className="game-games-card pwa-card">
      <div className="game-section-header">
        <FaGamepad size={20} color="var(--pdl-gold)" />
        <h3>Jogos & Atividades</h3>
      </div>
      <div className="game-wallet-grid">
        <div className="game-wallet-item">
          <span className="wallet-label"><FaDice size={11} /> Giros</span>
          <span className="wallet-value purple">{fmt(games.spins)}</span>
        </div>
        <div className="game-wallet-item">
          <span className="wallet-label"><FaBoxOpen size={11} /> Boxes</span>
          <span className="wallet-value blue">{fmt(games.boxes_opened)}</span>
        </div>
        <div className="game-wallet-item full">
          <span className="wallet-label">Total de Jogos</span>
          <span className="wallet-value gold">{fmt(games.total)}</span>
        </div>
      </div>
    </div>
  );
}

/* ===== SHOP ===== */
function ShopGrid({ items }) {
  if (!items || items.length === 0) {
    return (
      <div className="game-empty">
        <div style={{ fontSize: "2rem" }}>🏪</div>
        <p>Nenhum item disponível na loja.</p>
      </div>
    );
  }
  return (
    <div className="game-shop-grid">
      {items.map((item) => (
        <div key={item.id} className="game-shop-item">
          <div className="shop-item-icon"><FaShoppingCart size={18} color="var(--pdl-gold)" /></div>
          <div className="shop-item-info">
            <div className="shop-item-name">{item.nome}</div>
            <div className="shop-item-qty">x{item.quantidade}</div>
          </div>
          <div className="shop-item-price">{fmtBRL(item.preco)}</div>
        </div>
      ))}
    </div>
  );
}

/* ===== LEADERBOARD ===== */
function LeaderboardList({ ranking }) {
  if (!ranking || ranking.length === 0) {
    return (
      <div className="game-empty">
        <div style={{ fontSize: "2rem" }}>🏆</div>
        <p>Nenhum ranking disponível.</p>
      </div>
    );
  }
  const medals = ["🥇", "🥈", "🥉"];
  return (
    <div className="game-leaderboard-list">
      {ranking.map((p) => (
        <div key={p.position} className={`game-lb-item ${p.position <= 3 ? "game-lb-item--top" : ""}`}>
          <div className="lb-pos">
            {p.position <= 3 ? medals[p.position - 1] : `#${p.position}`}
          </div>
          <div className="lb-name">{p.username}</div>
          <div className="lb-stats">
            <span className="lb-level">Nv. {p.level}</span>
            <span className="lb-xp">{fmt(p.xp)} XP</span>
          </div>
        </div>
      ))}
    </div>
  );
}

/* ===== CLAN SEARCH ===== */
function ClanCard({ data }) {
  if (!data) return null;
  return (
    <div className="game-clan-result pwa-card">
      <div className="game-section-header">
        <FaShieldAlt size={18} color="var(--pdl-gold)" />
        <h4>{data.clan_name || "Clã"}</h4>
      </div>
      <div className="game-clan-grid">
        {[
          { label: "Líder", value: data.leader_name },
          { label: "Nível", value: data.level },
          { label: "Membros", value: data.member_count },
          { label: "Reputação", value: fmt(data.reputation) },
          data.ally_name && { label: "Aliança", value: data.ally_name },
          data.description && { label: "Descrição", value: data.description },
        ].filter(Boolean).map((f) => (
          <div key={f.label} className="clan-stat">
            <span className="stat-label">{f.label}</span>
            <span className="stat-value">{f.value ?? "—"}</span>
          </div>
        ))}
      </div>
    </div>
  );
}

/* ===== AUCTION ===== */
function AuctionGrid({ items }) {
  if (!items || items.length === 0) {
    return (
      <div className="game-empty">
        <div style={{ fontSize: "2rem" }}>🏷️</div>
        <p>Nenhum item no leilão.</p>
      </div>
    );
  }
  function gradeBadge(grade) {
    const map = { S: "#b44fd4", A: "#4f7fd4", B: "#4fad4f", C: "#a0a0a0", D: "#c88040", NG: "#888" };
    return map[grade?.toUpperCase?.()] || "#888";
  }
  return (
    <div className="game-auction-grid">
      {items.slice(0, 16).map((item, i) => (
        <div key={i} className="game-auction-card">
          <div className="auction-card-top">
            <span className="auction-item-name">{item.item_name}</span>
            {item.item_grade && (
              <span className="auction-grade-badge" style={{ background: gradeBadge(item.item_grade) }}>
                {item.item_grade}
              </span>
            )}
            {item.item_enchant > 0 && (
              <span className="auction-enchant">+{item.item_enchant}</span>
            )}
          </div>
          <div className="auction-card-mid">
            <span className="auction-seller">{item.seller_name}</span>
            {item.item_count > 1 && <span className="auction-count">x{item.item_count}</span>}
          </div>
          <div className="auction-card-bot">
            <div className="auction-bid-row">
              <FaGavel size={11} color="var(--pdl-gold)" />
              <span className="auction-bid">{fmt(item.current_bid)}</span>
            </div>
            <div className="auction-time">
              <FaClock size={10} color="#888" />
              <span>{fmtDate(item.end_time)}</span>
            </div>
          </div>
        </div>
      ))}
    </div>
  );
}

/* ===== TABS ===== */
const TABS = [
  { key: "overview", label: "Visão Geral", icon: <FaStar size={14} /> },
  { key: "shop", label: "Loja", icon: <FaShoppingCart size={14} /> },
  { key: "clan", label: "Busca de Clã", icon: <FaShieldAlt size={14} /> },
  { key: "auction", label: "Leilão", icon: <FaGavel size={14} /> },
  { key: "ranking", label: "Ranking PDL", icon: <FaTrophy size={14} /> },
];

export default function GameSection({ token }) {
  const [tab, setTab] = useState("overview");
  const [summary, setSummary] = useState(null);
  const [leaderboard, setLeaderboard] = useState([]);
  const [auction, setAuction] = useState([]);
  const [clanName, setClanName] = useState("");
  const [clanData, setClanData] = useState(null);
  const [loading, setLoading] = useState({});
  const [error, setError] = useState({});

  const load = useCallback(async (key, url) => {
    setLoading(p => ({ ...p, [key]: true }));
    try {
      const r = await apiFetch(url);
      if (r.ok) {
        const d = await r.json();
        return d;
      }
    } catch (_) { }
    setLoading(p => ({ ...p, [key]: false }));
    return null;
  }, []);

  // Load summary on mount
  useEffect(() => {
    load("summary", "/api/v1/game/summary/").then(d => {
      if (d?.data) setSummary(d.data);
      setLoading(p => ({ ...p, summary: false }));
    });
  }, [token]);

  // Load per tab
  useEffect(() => {
    if (tab === "ranking" && leaderboard.length === 0) {
      load("ranking", "/api/v1/game/leaderboard/").then(d => {
        if (d?.data) setLeaderboard(d.data);
        setLoading(p => ({ ...p, ranking: false }));
      });
    }
    if (tab === "auction" && auction.length === 0) {
      load("auction", "/api/v1/auction/items/").then(d => {
        if (Array.isArray(d)) setAuction(d);
        else if (d?.results) setAuction(d.results);
        setLoading(p => ({ ...p, auction: false }));
      });
    }
  }, [tab]);

  async function searchClan(e) {
    e.preventDefault();
    if (!clanName.trim()) return;
    setLoading(p => ({ ...p, clan: true }));
    setError(p => ({ ...p, clan: "" }));
    setClanData(null);
    const r = await apiFetch(`/api/v1/clan/${encodeURIComponent(clanName)}/`);
    if (r?.ok) {
      const d = await r.json();
      setClanData(d);
    } else {
      setError(p => ({ ...p, clan: "Clã não encontrado." }));
    }
    setLoading(p => ({ ...p, clan: false }));
  }

  return (
    <div className="game-section">
      {/* Tabs */}
      <div className="game-tabs">
        {TABS.map(t => (
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

      {/* Overview */}
      {tab === "overview" && (
        <div className="game-overview">
          {loading.summary ? (
            <div className="loading">Carregando dados</div>
          ) : (
            <>
              <WalletCard wallet={summary?.wallet} fichas={summary?.fichas} />
              <AchievementsCard achievements={summary?.achievements} />
              {summary?.battle_pass && <BattlePassCard battlePass={summary.battle_pass} />}
              <GamesCard games={summary?.games} />
            </>
          )}
        </div>
      )}

      {/* Shop */}
      {tab === "shop" && (
        <div className="pwa-card">
          <div className="game-section-header">
            <FaShoppingCart size={20} color="var(--pdl-gold)" />
            <h3>Itens da Loja</h3>
          </div>
          {loading.summary ? <div className="loading">Carregando</div> : (
            <ShopGrid items={summary?.shop_items} />
          )}
        </div>
      )}

      {/* Clan search */}
      {tab === "clan" && (
        <div className="game-clan-section pwa-card">
          <div className="game-section-header">
            <FaShieldAlt size={20} color="var(--pdl-gold)" />
            <h3>Busca de Clã</h3>
          </div>
          <form className="game-search-form" onSubmit={searchClan}>
            <input
              type="text"
              placeholder="Nome do clã..."
              value={clanName}
              onChange={e => setClanName(e.target.value)}
              className="pwa-input"
              required
            />
            <button type="submit" className="pwa-btn pwa-btn--primary" disabled={loading.clan}>
              <FaSearch size={13} />
              {loading.clan ? "Buscando..." : "Buscar"}
            </button>
          </form>
          {error.clan && <div className="error">{error.clan}</div>}
          {clanData && <ClanCard data={clanData} />}
        </div>
      )}

      {/* Auction */}
      {tab === "auction" && (
        <div className="pwa-card">
          <div className="game-section-header">
            <FaGavel size={20} color="var(--pdl-gold)" />
            <h3>Leilão do Servidor</h3>
            <button className="pwa-btn pwa-btn--secondary" style={{ marginLeft: "auto", padding: "4px 10px", fontSize: "0.8rem" }}
              onClick={() => { setAuction([]); load("auction", "/api/v1/auction/items/").then(d => { if (Array.isArray(d)) setAuction(d); setLoading(p => ({ ...p, auction: false })); }); }}
              disabled={loading.auction}>
              <FaSync size={11} />
            </button>
          </div>
          {loading.auction ? <div className="loading">Carregando leilão</div> : <AuctionGrid items={auction} />}
        </div>
      )}

      {/* Ranking PDL */}
      {tab === "ranking" && (
        <div className="pwa-card">
          <div className="game-section-header">
            <FaTrophy size={20} color="var(--pdl-gold)" />
            <h3>Ranking PDL — XP</h3>
          </div>
          {loading.ranking ? <div className="loading">Carregando ranking</div> : <LeaderboardList ranking={leaderboard} />}
        </div>
      )}
    </div>
  );
}