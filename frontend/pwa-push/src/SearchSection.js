import React, { useState } from "react";
import { FaUser, FaSearch, FaGavel, FaShieldAlt, FaCrown } from "react-icons/fa";

function CharacterResults({ data }) {
  if (!Array.isArray(data) || data.length === 0) return <div className="empty">Nenhum personagem encontrado.</div>;
  return (
    <div className="search-results">
      <h3>Personagens Encontrados ({data.length})</h3>
      <div className="character-grid">
        {data.map((char, i) => (
          <div className="character-card" key={i}>
            <div className="character-avatar">
              <FaUser size={32} color="#e6c77d" />
            </div>
            <div className="character-info">
              <div className="character-name">{char.name || char.character_name || "Sem nome"}</div>
              <div className="character-details">
                {char.level && <span>Level: {char.level}</span>}
                {char.clan && <span>Clã: {char.clan}</span>}
                {char.class && <span>Classe: {char.class}</span>}
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}

function ItemResults({ data }) {
  if (!Array.isArray(data) || data.length === 0) return <div className="empty">Nenhum item encontrado.</div>;
  return (
    <div className="search-results">
      <h3>Itens Encontrados ({data.length})</h3>
      <div className="item-grid">
        {data.map((item, i) => (
          <div className="item-card" key={i}>
            <div className="item-icon">
              <FaGavel size={24} color="#e6c77d" />
            </div>
            <div className="item-info">
              <div className="item-name">{item.name || item.item_name || "Sem nome"}</div>
              <div className="item-details">
                {item.type && <span>Tipo: {item.type}</span>}
                {item.grade && <span>Grau: {item.grade}</span>}
                {item.price && <span>Preço: {item.price}</span>}
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}

export default function SearchSection({ token }) {
  const [characterQuery, setCharacterQuery] = useState("");
  const [itemQuery, setItemQuery] = useState("");
  const [characterResults, setCharacterResults] = useState(null);
  const [itemResults, setItemResults] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  async function searchCharacter(e) {
    e.preventDefault();
    if (!characterQuery.trim()) return;
    
    setLoading(true);
    setError("");
    try {
      const res = await fetch(`/api/v1/search/character/?q=${encodeURIComponent(characterQuery)}`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      const data = await res.json();
      setCharacterResults(data);
    } catch (e) {
      setError("Erro ao buscar personagem");
    }
    setLoading(false);
  }

  async function searchItem(e) {
    e.preventDefault();
    if (!itemQuery.trim()) return;
    
    setLoading(true);
    setError("");
    try {
      const res = await fetch(`/api/v1/search/item/?q=${encodeURIComponent(itemQuery)}`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      const data = await res.json();
      setItemResults(data);
    } catch (e) {
      setError("Erro ao buscar item");
    }
    setLoading(false);
  }

  return (
    <div className="search-section">
      <div className="search-character-box">
        <h2>Busca de Personagem</h2>
        <form onSubmit={searchCharacter} className="search-form">
          <input
            type="text"
            placeholder="Nome do personagem"
            value={characterQuery}
            onChange={e => setCharacterQuery(e.target.value)}
            className="input"
            required
          />
          <button className="btn-primary" type="submit" disabled={loading}>
            {loading ? "Buscando..." : "Buscar"}
          </button>
        </form>
        {characterResults && <CharacterResults data={characterResults} />}
      </div>

      <div className="search-item-box">
        <h2>Busca de Item</h2>
        <form onSubmit={searchItem} className="search-form">
          <input
            type="text"
            placeholder="Nome do item"
            value={itemQuery}
            onChange={e => setItemQuery(e.target.value)}
            className="input"
            required
          />
          <button className="btn-primary" type="submit" disabled={loading}>
            {loading ? "Buscando..." : "Buscar"}
          </button>
        </form>
        {itemResults && <ItemResults data={itemResults} />}
      </div>

      {error && <div className="error">{error}</div>}
    </div>
  );
} 