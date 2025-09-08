/**
 * Configuração do Sistema de Notificações Flutuantes
 * 
 * Este arquivo permite personalizar facilmente o comportamento
 * e aparência das notificações sem modificar o código principal.
 */

// Configurações padrão do sistema
const FLOATING_NOTIFICATIONS_CONFIG = {
  // Comportamento geral
  autoClose: true,              // Fecha automaticamente
  autoCloseDelay: 5000,         // Tempo em milissegundos (5 segundos)
  maxNotifications: 5,          // Máximo de notificações simultâneas
  animationDuration: 300,       // Duração das animações
  
  // Posicionamento
  position: {
    top: '20px',
    right: '20px',
    left: 'auto',               // Para posicionamento à esquerda
    bottom: 'auto'              // Para posicionamento inferior
  },
  
  // Tamanhos
  maxWidth: '400px',
  mobileMaxWidth: 'none',       // Largura em dispositivos móveis
  
  // Cores personalizadas (opcional)
  colors: {
    success: {
      border: '#28a745',
      background: 'linear-gradient(135deg, #d4edda 0%, #c3e6cb 100%)',
      icon: '#155724',
      title: '#155724'
    },
    error: {
      border: '#dc3545',
      background: 'linear-gradient(135deg, #f8d7da 0%, #f5c6cb 100%)',
      icon: '#721c24',
      title: '#721c24'
    },
    warning: {
      border: '#ffc107',
      background: 'linear-gradient(135deg, #fff3cd 0%, #ffeaa7 100%)',
      icon: '#856404',
      title: '#856404'
    },
    info: {
      border: '#17a2b8',
      background: 'linear-gradient(135deg, #d1ecf1 0%, #bee5eb 100%)',
      icon: '#0c5460',
      title: '#0c5460'
    },
    debug: {
      border: '#6c757d',
      background: 'linear-gradient(135deg, #e2e3e5 0%, #d6d8db 100%)',
      icon: '#495057',
      title: '#495057'
    }
  },
  
  // Ícones personalizados (Bootstrap Icons)
  icons: {
    success: 'bi-check-circle-fill',
    error: 'bi-exclamation-triangle-fill',
    warning: 'bi-exclamation-circle-fill',
    info: 'bi-info-circle-fill',
    debug: 'bi-bug-fill'
  },
  
  // Títulos personalizados
  titles: {
    success: 'Sucesso',
    error: 'Erro',
    warning: 'Aviso',
    info: 'Informação',
    debug: 'Debug'
  },
  
  // Comportamentos avançados
  features: {
    pauseOnHover: true,         // Pausa auto-close no hover
    pauseDelay: 2000,           // Tempo de pausa após hover
    progressBar: true,          // Mostra barra de progresso
    sound: false,               // Som de notificação (futuro)
    vibration: false,           // Vibração em mobile (futuro)
    swipeToClose: true          // Fechar com swipe em mobile (futuro)
  },
  
  // Configurações de acessibilidade
  accessibility: {
    announceToScreenReader: true,  // Anuncia para leitores de tela
    focusManagement: true,         // Gerencia foco do teclado
    keyboardShortcuts: true        // Atalhos de teclado (futuro)
  },
  
  // Configurações de internacionalização
  i18n: {
    closeButton: 'Fechar',
    closeAllButton: 'Fechar Todas',
    successTitle: 'Sucesso',
    errorTitle: 'Erro',
    warningTitle: 'Aviso',
    infoTitle: 'Informação',
    debugTitle: 'Debug'
  }
};

// Função para aplicar configurações personalizadas
function applyCustomConfig() {
  // Aplica cores personalizadas se definidas
  if (FLOATING_NOTIFICATIONS_CONFIG.colors) {
    const style = document.createElement('style');
    let css = '';
    
    Object.entries(FLOATING_NOTIFICATIONS_CONFIG.colors).forEach(([type, colors]) => {
      css += `
        .floating-notification-${type} {
          border-left-color: ${colors.border} !important;
          background: ${colors.background} !important;
        }
        .floating-notification-${type} .notification-icon {
          color: ${colors.icon} !important;
        }
        .floating-notification-${type} .notification-title {
          color: ${colors.title} !important;
        }
        .floating-notification-${type} .notification-progress::before {
          background: ${colors.border} !important;
        }
      `;
    });
    
    style.textContent = css;
    document.head.appendChild(style);
  }
  
  // Aplica posicionamento personalizado
  if (FLOATING_NOTIFICATIONS_CONFIG.position) {
    const container = document.getElementById('floating-notifications-container');
    if (container) {
      Object.entries(FLOATING_NOTIFICATIONS_CONFIG.position).forEach(([property, value]) => {
        if (value !== 'auto') {
          container.style[property] = value;
        }
      });
    }
  }
}

// Função para obter configuração
function getNotificationConfig() {
  return FLOATING_NOTIFICATIONS_CONFIG;
}

// Função para atualizar configuração dinamicamente
function updateNotificationConfig(newConfig) {
  Object.assign(FLOATING_NOTIFICATIONS_CONFIG, newConfig);
  
  // Reaplica configurações se o sistema já foi inicializado
  if (window.floatingNotifications) {
    window.floatingNotifications.setOptions({
      autoClose: FLOATING_NOTIFICATIONS_CONFIG.autoClose,
      autoCloseDelay: FLOATING_NOTIFICATIONS_CONFIG.autoCloseDelay,
      maxNotifications: FLOATING_NOTIFICATIONS_CONFIG.maxNotifications,
      animationDuration: FLOATING_NOTIFICATIONS_CONFIG.animationDuration
    });
  }
  
  // Reaplica estilos personalizados
  applyCustomConfig();
}

// Exemplo de configuração personalizada
function setupCustomNotifications() {
  // Configuração para tema escuro
  const darkThemeConfig = {
    colors: {
      success: {
        border: '#00d4aa',
        background: 'linear-gradient(135deg, #1a1a1a 0%, #2d2d2d 100%)',
        icon: '#00d4aa',
        title: '#00d4aa'
      },
      error: {
        border: '#ff6b6b',
        background: 'linear-gradient(135deg, #1a1a1a 0%, #2d2d2d 100%)',
        icon: '#ff6b6b',
        title: '#ff6b6b'
      },
      warning: {
        border: '#ffd93d',
        background: 'linear-gradient(135deg, #1a1a1a 0%, #2d2d2d 100%)',
        icon: '#ffd93d',
        title: '#ffd93d'
      },
      info: {
        border: '#4ecdc4',
        background: 'linear-gradient(135deg, #1a1a1a 0%, #2d2d2d 100%)',
        icon: '#4ecdc4',
        title: '#4ecdc4'
      }
    },
    autoCloseDelay: 7000, // 7 segundos para tema escuro
    maxNotifications: 3   // Menos notificações para tema escuro
  };
  
  // Aplica configuração personalizada
  updateNotificationConfig(darkThemeConfig);
}

// Exemplo de configuração para diferentes tipos de usuário
function setupUserSpecificNotifications(userType) {
  const configs = {
    admin: {
      autoCloseDelay: 10000,    // 10 segundos para admins
      maxNotifications: 10,     // Mais notificações para admins
      features: {
        ...FLOATING_NOTIFICATIONS_CONFIG.features,
        sound: true             // Som para admins
      }
    },
    user: {
      autoCloseDelay: 5000,     // 5 segundos para usuários normais
      maxNotifications: 5,      // Notificações padrão
      features: {
        ...FLOATING_NOTIFICATIONS_CONFIG.features,
        sound: false
      }
    },
    mobile: {
      autoCloseDelay: 3000,     // 3 segundos para mobile
      maxNotifications: 3,      // Menos notificações para mobile
      position: {
        top: '10px',
        right: '10px',
        left: '10px',
        bottom: 'auto'
      }
    }
  };
  
  const config = configs[userType] || configs.user;
  updateNotificationConfig(config);
}

// Detecta automaticamente se é dispositivo móvel
function setupResponsiveNotifications() {
  const isMobile = window.innerWidth <= 768;
  const userType = isMobile ? 'mobile' : 'user';
  setupUserSpecificNotifications(userType);
}

// Inicializa configurações quando o DOM estiver pronto
document.addEventListener('DOMContentLoaded', function() {
  // Aplica configurações padrão
  applyCustomConfig();
  
  // Configura responsividade
  setupResponsiveNotifications();
  
  // Listener para mudanças de tamanho de tela
  window.addEventListener('resize', setupResponsiveNotifications);
});

// Exporta funções para uso global
window.FloatingNotificationsConfig = {
  getConfig: getNotificationConfig,
  updateConfig: updateNotificationConfig,
  setupCustom: setupCustomNotifications,
  setupUserSpecific: setupUserSpecificNotifications,
  setupResponsive: setupResponsiveNotifications
};

// Exemplo de uso:
// 
// // Configurar para tema escuro
// window.FloatingNotificationsConfig.setupCustom();
// 
// // Configurar para admin
// window.FloatingNotificationsConfig.setupUserSpecific('admin');
// 
// // Atualizar configuração manualmente
// window.FloatingNotificationsConfig.updateConfig({
//   autoCloseDelay: 8000,
//   maxNotifications: 8
// });
