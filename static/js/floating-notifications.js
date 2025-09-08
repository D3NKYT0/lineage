/**
 * Sistema de Notificações Flutuantes para Django
 * Gerencia notificações com auto-close, fechamento manual e animações suaves
 */
class FloatingNotifications {
  constructor(options = {}) {
    this.container = document.getElementById('floating-notifications-container');
    this.options = {
      autoClose: true,
      autoCloseDelay: 5000, // 5 segundos
      maxNotifications: 5,
      animationDuration: 300,
      ...options
    };
    
    this.notifications = [];
    this.init();
  }

  init() {
    if (!this.container) {
      console.warn('Container de notificações não encontrado');
      return;
    }

    // Inicializa notificações existentes
    this.initializeExistingNotifications();
    
    // Adiciona listeners para botões de fechar
    this.addCloseListeners();
    
    // Configura auto-close
    if (this.options.autoClose) {
      this.setupAutoClose();
    }
  }

  initializeExistingNotifications() {
    const existingNotifications = this.container.querySelectorAll('.floating-notification');
    
    existingNotifications.forEach((notification, index) => {
      // Adiciona delay escalonado para entrada
      setTimeout(() => {
        notification.classList.add('show');
      }, index * 100);
      
      this.notifications.push(notification);
    });
  }

  addCloseListeners() {
    // Listener para botões de fechar existentes
    this.container.addEventListener('click', (e) => {
      if (e.target.closest('.notification-close')) {
        const notification = e.target.closest('.floating-notification');
        this.closeNotification(notification);
      }
    });

    // Listener para fechar ao clicar na notificação (opcional)
    this.container.addEventListener('click', (e) => {
      const notification = e.target.closest('.floating-notification');
      if (notification && !e.target.closest('.notification-close')) {
        // Pausa o auto-close temporariamente
        this.pauseAutoClose(notification);
      }
    });
  }

  setupAutoClose() {
    const notifications = this.container.querySelectorAll('.floating-notification[data-auto-close="true"]');
    
    notifications.forEach((notification) => {
      const timeoutId = setTimeout(() => {
        this.closeNotification(notification);
      }, this.options.autoCloseDelay);
      
      // Armazena o timeout ID para poder cancelar se necessário
      notification.dataset.timeoutId = timeoutId;
    });
  }

  pauseAutoClose(notification) {
    const timeoutId = notification.dataset.timeoutId;
    if (timeoutId) {
      clearTimeout(parseInt(timeoutId));
      notification.dataset.timeoutId = null;
      
      // Reinicia o auto-close após 2 segundos de inatividade
      setTimeout(() => {
        if (notification.dataset.autoClose === 'true') {
          const newTimeoutId = setTimeout(() => {
            this.closeNotification(notification);
          }, this.options.autoCloseDelay);
          notification.dataset.timeoutId = newTimeoutId;
        }
      }, 2000);
    }
  }

  closeNotification(notification) {
    if (!notification || notification.classList.contains('hiding')) {
      return;
    }

    // Remove o timeout se existir
    const timeoutId = notification.dataset.timeoutId;
    if (timeoutId) {
      clearTimeout(parseInt(timeoutId));
    }

    // Adiciona classe para animação de saída
    notification.classList.add('hiding', 'fade-out');
    notification.classList.remove('show');

    // Remove a notificação após a animação
    setTimeout(() => {
      if (notification.parentNode) {
        notification.remove();
        this.notifications = this.notifications.filter(n => n !== notification);
      }
    }, this.options.animationDuration);
  }

  // Método para adicionar notificação programaticamente
  addNotification(message, type = 'info', options = {}) {
    const notificationOptions = {
      autoClose: this.options.autoClose,
      autoCloseDelay: this.options.autoCloseDelay,
      ...options
    };

    const notification = this.createNotificationElement(message, type, notificationOptions);
    
    // Limita o número máximo de notificações
    if (this.notifications.length >= this.options.maxNotifications) {
      const oldestNotification = this.notifications.shift();
      this.closeNotification(oldestNotification);
    }

    this.container.appendChild(notification);
    this.notifications.push(notification);

    // Anima a entrada
    setTimeout(() => {
      notification.classList.add('show');
    }, 100);

    // Configura auto-close se habilitado
    if (notificationOptions.autoClose) {
      const timeoutId = setTimeout(() => {
        this.closeNotification(notification);
      }, notificationOptions.autoCloseDelay);
      notification.dataset.timeoutId = timeoutId;
    }

    return notification;
  }

  createNotificationElement(message, type, options) {
    const notification = document.createElement('div');
    notification.className = `floating-notification floating-notification-${type}`;
    notification.dataset.autoClose = options.autoClose.toString();
    
    const iconMap = {
      success: 'bi-check-circle-fill',
      error: 'bi-exclamation-triangle-fill',
      warning: 'bi-exclamation-circle-fill',
      info: 'bi-info-circle-fill',
      debug: 'bi-bug-fill'
    };

    const titleMap = {
      success: 'Sucesso',
      error: 'Erro',
      warning: 'Aviso',
      info: 'Informação',
      debug: 'Debug'
    };

    notification.innerHTML = `
      <div class="notification-content">
        <div class="notification-icon">
          <i class="bi ${iconMap[type] || 'bi-bell-fill'}"></i>
        </div>
        <div class="notification-text">
          <div class="notification-title">${titleMap[type] || 'Notificação'}</div>
          <div class="notification-message">${message}</div>
        </div>
        <button type="button" class="notification-close" aria-label="Fechar">
          <i class="bi bi-x"></i>
        </button>
      </div>
      <div class="notification-progress"></div>
    `;

    return notification;
  }

  // Métodos utilitários
  closeAll() {
    this.notifications.forEach(notification => {
      this.closeNotification(notification);
    });
  }

  // Configurações dinâmicas
  setOptions(newOptions) {
    this.options = { ...this.options, ...newOptions };
  }

  // Método para mostrar notificação de sucesso
  success(message, options = {}) {
    return this.addNotification(message, 'success', options);
  }

  // Método para mostrar notificação de erro
  error(message, options = {}) {
    return this.addNotification(message, 'error', options);
  }

  // Método para mostrar notificação de aviso
  warning(message, options = {}) {
    return this.addNotification(message, 'warning', options);
  }

  // Método para mostrar notificação de informação
  info(message, options = {}) {
    return this.addNotification(message, 'info', options);
  }

  // Método para mostrar notificação de debug
  debug(message, options = {}) {
    return this.addNotification(message, 'debug', options);
  }
}

// Inicializa o sistema quando o DOM estiver pronto
document.addEventListener('DOMContentLoaded', function() {
  // Cria instância global para uso em outros scripts
  window.floatingNotifications = new FloatingNotifications({
    autoClose: true,
    autoCloseDelay: 5000,
    maxNotifications: 5
  });
});

// Exemplo de uso programático:
// window.floatingNotifications.success('Operação realizada com sucesso!');
// window.floatingNotifications.error('Ocorreu um erro na operação');
// window.floatingNotifications.warning('Atenção: dados incompletos');
// window.floatingNotifications.info('Nova atualização disponível');
