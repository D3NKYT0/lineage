import React, { useState } from "react";
import { subscribeUserToPush, unsubscribeUserFromPush } from "./push";
import { FaBell, FaCheck, FaTimes, FaMobile, FaDownload } from "react-icons/fa";

function PermissionStatus({ permission }) {
  const getStatusInfo = () => {
    switch (permission) {
      case "granted":
        return { text: "Permitido", color: "#28a745", icon: <FaCheck /> };
      case "denied":
        return { text: "Negado", color: "#dc3545", icon: <FaTimes /> };
      default:
        return { text: "Não definido", color: "#ffc107", icon: <FaTimes /> };
    }
  };

  const status = getStatusInfo();
  
  return (
    <div className="push-permission-status">
      <div className="permission-icon" style={{ color: status.color }}>
        {status.icon}
      </div>
      <div className="permission-info">
        <div className="permission-label">Status da Permissão</div>
        <div className="permission-value" style={{ color: status.color }}>
          {status.text}
        </div>
      </div>
    </div>
  );
}

export default function PushSection({ token }) {
  const [permission, setPermission] = useState(Notification.permission);
  const [subscribed, setSubscribed] = useState(false);
  const [pushError, setPushError] = useState("");

  const handleSubscribe = async () => {
    console.log("Clicou em Ativar Push");
    setPushError("");
    const result = await subscribeUserToPush(token);
    console.log("Resultado subscribeUserToPush:", result);
    if (result && result.success) {
      setSubscribed(true);
      setPermission("granted");
    } else if (result && result.error) {
      setPushError(result.error);
    }
  };

  const handleUnsubscribe = async () => {
    if (!('serviceWorker' in navigator)) return;
    const registration = await navigator.serviceWorker.ready;
    const subscription = await registration.pushManager.getSubscription();
    if (subscription) {
      await subscription.unsubscribe();
      await unsubscribeUserFromPush(token, subscription);
      setSubscribed(false);
      setPermission(Notification.permission);
    }
  };

  return (
    <div className="push-section">
      <div className="push-header">
        <div className="push-icon">
          <FaBell size={32} color="#e6c77d" />
        </div>
        <div className="push-title">
          <h2>Notificações Push</h2>
          <p>Receba alertas importantes diretamente no seu celular.</p>
        </div>
      </div>

      <div className="push-status-card">
        <PermissionStatus permission={permission} />
        
        {subscribed && (
          <div className="push-subscribed-status">
            <div className="subscribed-icon">
              <FaCheck size={24} color="#28a745" />
            </div>
            <div className="subscribed-info">
              <div className="subscribed-title">Notificações Ativadas!</div>
              <div className="subscribed-desc">Você receberá alertas importantes deste app.</div>
            </div>
          </div>
        )}
      </div>

      <div className="push-actions">
        {permission !== "granted" && (
          <button className="btn-primary push-action-btn" onClick={handleSubscribe}>
            <FaBell />
            Permitir Notificações
          </button>
        )}
        {permission === "granted" && !subscribed && (
          <button className="btn-primary push-action-btn" onClick={handleSubscribe}>
            <FaBell />
            Ativar Push
          </button>
        )}
        {subscribed && (
          <button className="btn-secondary push-action-btn" onClick={handleUnsubscribe}>
            <FaTimes />
            Desativar Push
          </button>
        )}
      </div>

      {pushError && (
        <div className="push-error">
          <FaTimes />
          {pushError}
        </div>
      )}

      <div className="push-install-tip">
        <div className="install-icon">
          <FaDownload size={20} color="#e6c77d" />
        </div>
        <div className="install-text">
          <div className="install-title">Instalar App</div>
          <div className="install-desc">
            Use o menu do navegador e escolha <b>"Adicionar à tela inicial"</b>.
          </div>
        </div>
      </div>
    </div>
  );
} 