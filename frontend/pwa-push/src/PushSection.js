import React, { useEffect, useState } from "react";
import { FaBell, FaCheck, FaTimes, FaDownload, FaMobileAlt, FaDesktop, FaInfoCircle, FaChrome, FaFirefoxBrowser, FaSafari } from "react-icons/fa";

const IS_IOS = typeof navigator !== "undefined" && /iPad|iPhone|iPod/.test(navigator.userAgent);
const IS_ANDROID = typeof navigator !== "undefined" && /Android/.test(navigator.userAgent);
const IS_SAFARI = typeof navigator !== "undefined" && /^((?!chrome|android).)*safari/i.test(navigator.userAgent);

function StatusBadge({ ok, label }) {
  return (
    <span className={`push-status-badge ${ok ? "push-status-badge--ok" : "push-status-badge--warn"}`}>
      {ok ? <FaCheck size={10} /> : <FaTimes size={10} />}
      {label}
    </span>
  );
}

function FeatureCheck({ label, ok }) {
  return (
    <div className="push-feature-item">
      <span className={`push-feature-icon ${ok ? "ok" : "warn"}`}>
        {ok ? <FaCheck size={12} /> : <FaTimes size={12} />}
      </span>
      <span className={`push-feature-label ${ok ? "" : "push-feature-label--off"}`}>{label}</span>
    </div>
  );
}

/* instrução por plataforma */
function PlatformGuide() {
  const [platform, setPlatform] = useState("android");

  const guides = {
    android: {
      icon: <FaMobileAlt size={20} />,
      label: "Android (Chrome)",
      steps: [
        'Abra este site no <strong>Chrome</strong>.',
        'Toque no menu <strong>⋮</strong> (três pontos) no canto superior direito.',
        'Toque em <strong>"Adicionar à tela inicial"</strong> ou <strong>"Instalar app"</strong>.',
        'Confirme tocando em <strong>"Instalar"</strong>.',
        'O app aparecerá na sua tela inicial. Abra-o e ative as notificações.',
      ],
    },
    ios: {
      icon: <FaMobileAlt size={20} />,
      label: "iPhone / iPad (Safari)",
      steps: [
        'Abra este site no <strong>Safari</strong> (obrigatório no iOS).',
        'Toque no botão de <strong>Compartilhar</strong> (ícone de quadrado com seta ↑).',
        'Role a lista e toque em <strong>"Adicionar à Tela de Início"</strong>.',
        'Confirme tocando em <strong>"Adicionar"</strong>.',
        'Abra o app pela tela inicial e permita as notificações quando solicitado (iOS 16.4+).',
      ],
    },
    desktop_chrome: {
      icon: <FaChrome size={20} />,
      label: "Desktop — Chrome",
      steps: [
        'Clique no ícone <strong>⊕</strong> (instalar) na barra de endereço do Chrome.',
        'Ou acesse o menu <strong>⋮</strong> → <strong>"Salvar e compartilhar"</strong> → <strong>"Instalar página como app"</strong>.',
        'Clique em <strong>"Instalar"</strong> na janela que aparecer.',
        'O app abrirá em janela separada. Clique em <strong>"Permitir"</strong> para notificações.',
      ],
    },
    desktop_firefox: {
      icon: <FaFirefoxBrowser size={20} />,
      label: "Desktop — Firefox",
      steps: [
        'O Firefox não suporta instalação de PWA como app.',
        'Use Chrome, Edge ou Opera para a melhor experiência.',
        'Notificações web funcionam normalmente no Firefox — clique em <strong>"Ativar Notificações"</strong> abaixo.',
      ],
    },
    desktop_edge: {
      icon: <FaDesktop size={20} />,
      label: "Desktop — Edge",
      steps: [
        'Clique no ícone <strong>⊕</strong> (app disponível) na barra de endereço.',
        'Ou acesse o menu <strong>⋯</strong> → <strong>"Apps"</strong> → <strong>"Instalar este site como um aplicativo"</strong>.',
        'Clique em <strong>"Instalar"</strong>.',
        'Permita notificações quando solicitado.',
      ],
    },
  };

  const PLAT_TABS = [
    { key: "android", label: "Android", icon: <FaMobileAlt size={12} /> },
    { key: "ios", label: "iOS", icon: <FaMobileAlt size={12} /> },
    { key: "desktop_chrome", label: "Chrome PC", icon: <FaChrome size={12} /> },
    { key: "desktop_edge", label: "Edge PC", icon: <FaDesktop size={12} /> },
    { key: "desktop_firefox", label: "Firefox", icon: <FaFirefoxBrowser size={12} /> },
  ];

  const guide = guides[platform];

  return (
    <div className="push-guide-card pwa-card">
      <div className="push-guide-header">
        <FaDownload size={18} color="var(--pdl-gold)" />
        <h3>Como instalar e ativar notificações</h3>
      </div>

      {/* Platform selector */}
      <div className="push-plat-tabs">
        {PLAT_TABS.map(p => (
          <button
            key={p.key}
            type="button"
            className={`push-plat-tab ${platform === p.key ? "push-plat-tab--active" : ""}`}
            onClick={() => setPlatform(p.key)}
          >
            {p.icon}
            <span>{p.label}</span>
          </button>
        ))}
      </div>

      {/* Steps */}
      <div className="push-guide-steps">
        <ol className="push-steps-list">
          {guide.steps.map((step, i) => (
            <li key={i} className="push-step-item">
              <span className="push-step-num">{i + 1}</span>
              <span dangerouslySetInnerHTML={{ __html: step }} />
            </li>
          ))}
        </ol>
      </div>
    </div>
  );
}

export default function PushSection({ token, subscribed: propSubscribed, permission: propPermission, onSubscribe, onUnsubscribe, pushError }) {
  const swSupported = "serviceWorker" in navigator;
  const pushSupported = "PushManager" in window;
  const notifSupported = "Notification" in window;

  const permission = propPermission ?? (notifSupported ? Notification.permission : "default");
  const subscribed = propSubscribed ?? false;

  const isGranted = permission === "granted";
  const isDenied = permission === "denied";

  return (
    <div className="push-section">
      {/* Hero */}
      <div className="push-hero pwa-card">
        <div className="push-hero-icon">
          <FaBell size={36} color="var(--pdl-gold)" />
          {subscribed && <span className="push-hero-online" />}
        </div>
        <div className="push-hero-text">
          <h2>Notificações Push</h2>
          <p>Receba alertas de eventos do servidor, sieges, resets de boss e mais, direto neste dispositivo.</p>
        </div>
      </div>

      {/* Status cards */}
      <div className="push-status-grid">
        <div className="push-status-card pwa-card">
          <h4>Compatibilidade</h4>
          <div className="push-features">
            <FeatureCheck label="Service Worker" ok={swSupported} />
            <FeatureCheck label="Push API" ok={pushSupported} />
            <FeatureCheck label="Notificações Web" ok={notifSupported} />
            <FeatureCheck label="Permissão concedida" ok={isGranted} />
          </div>
        </div>

        <div className="push-status-card pwa-card">
          <h4>Estado Atual</h4>
          <div className="push-state-body">
            <div className="push-state-item">
              <span className="push-state-label">Permissão</span>
              <StatusBadge
                ok={isGranted}
                label={permission === "granted" ? "Concedida" : permission === "denied" ? "Negada" : "Pendente"}
              />
            </div>
            <div className="push-state-item">
              <span className="push-state-label">Inscrito</span>
              <StatusBadge ok={subscribed} label={subscribed ? "Sim" : "Não"} />
            </div>
            <div className="push-state-item">
              <span className="push-state-label">Dispositivo</span>
              <StatusBadge ok label={IS_IOS ? "iOS" : IS_ANDROID ? "Android" : "Desktop"} />
            </div>
          </div>
        </div>
      </div>

      {/* Ações */}
      <div className="push-actions-card pwa-card">
        <h3>Ações</h3>

        {isDenied && (
          <div className="push-denied-warn">
            <FaInfoCircle size={16} />
            <span>
              Você <strong>bloqueou</strong> as notificações neste navegador.
              Para reativar, acesse as configurações do site no cadeado 🔒 na barra de endereço e redefina a permissão.
            </span>
          </div>
        )}

        <div className="push-btn-row">
          {!subscribed && !isDenied && (
            <button
              type="button"
              className="pwa-btn pwa-btn--primary"
              onClick={onSubscribe}
              disabled={!swSupported || !pushSupported}
            >
              <FaBell size={14} />
              {isGranted ? "Ativar Push" : "Permitir Notificações"}
            </button>
          )}
          {subscribed && (
            <>
              <div className="push-subscribed-indicator">
                <FaCheck size={14} color="#4caf50" />
                <span>Notificações ativadas neste dispositivo!</span>
              </div>
              <button type="button" className="pwa-btn pwa-btn--secondary" onClick={onUnsubscribe}>
                <FaTimes size={13} />
                Desativar
              </button>
            </>
          )}
        </div>

        {!swSupported && (
          <div className="push-compat-warn">
            ⚠️ Seu navegador não suporta Push Notifications.
            Use Chrome, Edge ou Firefox atualizado.
          </div>
        )}

        {pushError && <div className="error" style={{ marginTop: "0.75rem" }}>{pushError}</div>}
      </div>

      {/* Guia por plataforma */}
      <PlatformGuide />
    </div>
  );
}