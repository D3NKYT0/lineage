class WebSocketChat {
    constructor() {
        this.socket = null;
        this.activeFriendId = null;
        this.reconnectAttempts = 0;
        this.maxReconnectAttempts = 5;
        this.reconnectDelay = 1000;
        
        this.initializeElements();
        this.initializeWebSocket();
        this.initializeEventListeners();
        this.initializeEmojiPicker();
        this.startActivityTracking();
    }

    initializeElements() {
        this.messageInput = document.getElementById('message-input');
        this.sendBtn = document.getElementById('send-btn');
        this.emojiBtn = document.getElementById('emoji-btn');
        this.chatMessages = document.getElementById('chat-messages');
        this.chatInputContainer = document.getElementById('chat-input-container');
        this.friendItems = document.querySelectorAll('.friend-item');
        this.friendSearch = document.getElementById('friend-search');
    }

    initializeWebSocket() {
        const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
        const wsUrl = `${protocol}//${window.location.host}/ws/messages/`;
        
        this.socket = new WebSocket(wsUrl);
        
        this.socket.onopen = () => {
            console.log('WebSocket connected');
            this.reconnectAttempts = 0;
            this.updateConnectionStatus(true);
        };
        
        this.socket.onmessage = (event) => {
            this.handleWebSocketMessage(event);
        };
        
        this.socket.onclose = (event) => {
            console.log('WebSocket disconnected:', event.code, event.reason);
            this.updateConnectionStatus(false);
            this.handleReconnect();
        };
        
        this.socket.onerror = (error) => {
            console.error('WebSocket error:', error);
            this.updateConnectionStatus(false);
        };
    }

    handleReconnect() {
        if (this.reconnectAttempts < this.maxReconnectAttempts) {
            this.reconnectAttempts++;
            console.log(`Attempting to reconnect... (${this.reconnectAttempts}/${this.maxReconnectAttempts})`);
            
            setTimeout(() => {
                this.initializeWebSocket();
            }, this.reconnectDelay * this.reconnectAttempts);
        } else {
            console.error('Max reconnection attempts reached');
            this.showConnectionError();
        }
    }

    updateConnectionStatus(connected) {
        // Adicionar indicador visual de status da conexão se necessário
        const statusIndicator = document.getElementById('connection-status');
        if (!statusIndicator) {
            const indicator = document.createElement('div');
            indicator.id = 'connection-status';
            indicator.className = 'connection-status';
            document.body.appendChild(indicator);
        }
        
        const indicator = document.getElementById('connection-status');
        if (connected) {
            indicator.textContent = '🟢 Conectado';
            indicator.className = 'connection-status connected';
            setTimeout(() => {
                indicator.style.opacity = '0';
                setTimeout(() => indicator.remove(), 300);
            }, 2000);
        } else {
            indicator.textContent = '🔴 Desconectado';
            indicator.className = 'connection-status disconnected';
        }
    }

    showConnectionError() {
        const errorDiv = document.createElement('div');
        errorDiv.innerHTML = `
            <div style="
                position: fixed;
                top: 50%;
                left: 50%;
                transform: translate(-50%, -50%);
                background: white;
                padding: 2rem;
                border-radius: 12px;
                box-shadow: 0 10px 30px rgba(0,0,0,0.3);
                text-align: center;
                z-index: 10000;
            ">
                <h4 style="color: #dc3545; margin-bottom: 1rem;">Erro de Conexão</h4>
                <p style="margin-bottom: 1.5rem;">Não foi possível conectar ao servidor. Verifique sua conexão e tente novamente.</p>
                <button onclick="location.reload()" class="send-btn">Recarregar Página</button>
            </div>
        `;
        document.body.appendChild(errorDiv);
    }

    handleWebSocketMessage(event) {
        try {
            const data = JSON.parse(event.data);
            
            switch (data.type) {
                case 'new_message':
                    this.handleNewMessage(data);
                    break;
                case 'message_sent':
                    this.handleMessageSent(data);
                    break;
                case 'messages_loaded':
                    this.handleMessagesLoaded(data);
                    break;
                case 'messages_marked_read':
                    this.handleMessagesMarkedRead(data);
                    break;
                case 'unread_counts':
                    this.handleUnreadCounts(data);
                    break;
                case 'friends_stats':
                    this.handleFriendsStats(data);
                    break;
                case 'friends_status':
                    this.handleFriendsStatus(data);
                    break;
                case 'error':
                    this.showError(data.error);
                    break;
                default:
                    console.log('Unknown message type:', data.type);
            }
        } catch (error) {
            console.error('Error parsing WebSocket message:', error);
        }
    }

    handleNewMessage(data) {
        // Adicionar nova mensagem ao chat se estiver ativo
        if (this.activeFriendId && data.sender_id == this.activeFriendId) {
            this.addMessageToChat(data, false);
            this.scrollToBottom();
            
            // Marcar como lida
            this.sendWebSocketMessage({
                type: 'mark_as_read',
                friend_id: this.activeFriendId
            });
        }
        
        // Atualizar contador de não lidas
        this.updateUnreadBadge(data.sender_id, true);
    }

    handleMessageSent(data) {
        // Confirmar envio da mensagem
        this.addMessageToChat(data, true);
        this.scrollToBottom();
    }

    handleMessagesLoaded(data) {
        this.displayMessages(data.messages);
        this.scrollToBottom();
    }

    handleMessagesMarkedRead(data) {
        // Atualizar contador de não lidas
        this.updateUnreadBadge(data.friend_id, false);
    }

    handleUnreadCounts(data) {
        Object.entries(data.unread_counts).forEach(([friendId, count]) => {
            this.updateUnreadBadge(friendId, count > 0);
        });
    }

    handleFriendsStats(data) {
        // Atualizar estatísticas na interface
        const stats = data.stats;
        
        // Atualizar contadores na interface (se existirem)
        const friendsCountEl = document.getElementById('friends-count');
        const pendingRequestsEl = document.getElementById('pending-requests-count');
        const sentRequestsEl = document.getElementById('sent-requests-count');
        
        if (friendsCountEl) {
            friendsCountEl.textContent = stats.total_friends;
        }
        
        if (pendingRequestsEl) {
            pendingRequestsEl.textContent = stats.total_pending_requests;
        }
        
        if (sentRequestsEl) {
            sentRequestsEl.textContent = stats.total_sent_requests;
        }
        
        // Disparar evento customizado para outros componentes
        const event = new CustomEvent('friendsStatsUpdated', { detail: stats });
        document.dispatchEvent(event);
    }

    handleFriendsStatus(data) {
        // Atualizar status online/offline dos amigos
        const friendsStatus = data.friends_status;
        
        Object.entries(friendsStatus).forEach(([friendId, status]) => {
            const statusElement = document.getElementById(`status-${friendId}`);
            if (statusElement) {
                if (status.is_online) {
                    statusElement.innerHTML = '<span class="text-success"><i class="fas fa-circle"></i> Online</span>';
                    statusElement.className = 'friend-status text-success';
                } else {
                    statusElement.innerHTML = '<span class="text-muted"><i class="fas fa-circle"></i> Offline</span>';
                    statusElement.className = 'friend-status text-muted';
                }
            }
        });
        
        // Disparar evento customizado para outros componentes
        const event = new CustomEvent('friendsStatusUpdated', { detail: friendsStatus });
        document.dispatchEvent(event);
    }

    addMessageToChat(data, isOwn) {
        const messageDiv = document.createElement('div');
        messageDiv.className = `message ${isOwn ? 'own' : ''}`;
        
        const timestamp = new Date(data.timestamp).toLocaleString();
        const formattedMessage = data.message.replace(/\n/g, '<br>');
        
        messageDiv.innerHTML = `
            <div class="message-avatar">
                <img src="${isOwn ? avatarUrl : data.sender_avatar_url}" alt="${isOwn ? currentUser : data.sender_username}">
            </div>
            <div class="message-content">
                <div class="message-header">
                    <span class="message-sender">${isOwn ? currentUser : data.sender_username}</span>
                    <span class="message-time">${timestamp}</span>
                </div>
                <p class="message-text">${formattedMessage}</p>
            </div>
        `;
        
        this.chatMessages.appendChild(messageDiv);
    }

    displayMessages(messages) {
        this.chatMessages.innerHTML = '';
        
        if (messages.length === 0) {
            this.chatMessages.innerHTML = `
                <div class="chat-placeholder">
                    <div class="chat-placeholder-icon">
                        <i class="fas fa-comment-dots"></i>
                    </div>
                    <h4>Nenhuma mensagem ainda</h4>
                    <p>Seja o primeiro a enviar uma mensagem!</p>
                </div>
            `;
            return;
        }
        
        messages.forEach(message => {
            this.addMessageToChat({
                message: message.text,
                sender_username: message.sender.username,
                sender_avatar_url: message.sender.avatar_url,
                timestamp: message.timestamp
            }, message.is_own);
        });
    }

    updateUnreadBadge(friendId, hasUnread) {
        const badge = document.getElementById(`unread-${friendId}`);
        if (badge) {
            if (hasUnread) {
                badge.style.display = 'flex';
                // Se hasUnread for um número, mostrar o número, senão mostrar apenas o badge
                if (typeof hasUnread === 'number') {
                    badge.textContent = hasUnread;
                }
            } else {
                badge.style.display = 'none';
            }
        }
    }

    scrollToBottom() {
        setTimeout(() => {
            this.chatMessages.scrollTop = this.chatMessages.scrollHeight;
        }, 100);
    }

    initializeEventListeners() {
        // Enviar mensagem
        this.sendBtn.addEventListener('click', () => this.sendMessage());
        
        // Enter para enviar, Shift+Enter para nova linha
        this.messageInput.addEventListener('keydown', (e) => {
            if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                this.sendMessage();
            }
        });
        
        // Auto-resize do textarea
        this.messageInput.addEventListener('input', () => {
            this.messageInput.style.height = 'auto';
            this.messageInput.style.height = Math.min(this.messageInput.scrollHeight, 120) + 'px';
            this.updateSendButton();
        });
        
        // Selecionar amigo
        this.friendItems.forEach(item => {
            item.addEventListener('click', () => {
                const friendId = item.getAttribute('data-friend-id');
                this.selectFriend(friendId, item);
            });
        });
        
        // Busca de amigos
        if (this.friendSearch) {
            this.friendSearch.addEventListener('input', () => this.filterFriends());
        }
    }

    initializeEmojiPicker() {
        if (typeof EmojiButton !== 'undefined') {
            const picker = new EmojiButton();
            
            this.emojiBtn.addEventListener('click', () => {
                picker.togglePicker(this.emojiBtn);
            });
            
            picker.on('emoji', emoji => {
                const pos = this.messageInput.selectionStart;
                const text = this.messageInput.value;
                this.messageInput.value = text.slice(0, pos) + emoji + text.slice(pos);
                this.messageInput.focus();
                this.messageInput.setSelectionRange(pos + emoji.length, pos + emoji.length);
                this.updateSendButton();
            });
        }
    }

    sendMessage() {
        const message = this.messageInput.value.trim();
        
        if (!message || !this.activeFriendId) {
            return;
        }
        
        this.sendWebSocketMessage({
            type: 'send_message',
            message: message,
            friend_id: this.activeFriendId
        });
        
        this.messageInput.value = '';
        this.messageInput.style.height = 'auto';
        this.updateSendButton();
    }

    selectFriend(friendId, item) {
        this.activeFriendId = friendId;
        
        // Atualizar UI
        this.friendItems.forEach(friend => friend.classList.remove('active'));
        item.classList.add('active');
        
        // Mostrar área de input
        this.chatInputContainer.style.display = 'block';
        
        // Carregar mensagens
        this.sendWebSocketMessage({
            type: 'load_messages',
            friend_id: friendId
        });
        
        // Marcar como lidas
        this.sendWebSocketMessage({
            type: 'mark_as_read',
            friend_id: friendId
        });
    }

    filterFriends() {
        const searchTerm = this.friendSearch.value.toLowerCase();
        
        this.friendItems.forEach(item => {
            const name = item.querySelector('.friend-name').textContent.toLowerCase();
            const shouldShow = name.includes(searchTerm);
            item.style.display = shouldShow ? 'flex' : 'none';
        });
    }

    updateSendButton() {
        const hasText = this.messageInput.value.trim().length > 0;
        const hasActiveFriend = this.activeFriendId !== null;
        
        this.sendBtn.disabled = !hasText || !hasActiveFriend;
    }

    sendWebSocketMessage(data) {
        if (this.socket && this.socket.readyState === WebSocket.OPEN) {
            this.socket.send(JSON.stringify(data));
        } else {
            console.error('WebSocket is not connected');
        }
    }

    startActivityTracking() {
        // Enviar atividade a cada 5 minutos
        setInterval(() => {
            this.sendWebSocketMessage({
                type: 'user_activity'
            });
        }, 300000);
        
        // Enviar atividade inicial
        this.sendWebSocketMessage({
            type: 'user_activity'
        });
        
        // Atualizar contadores de não lidas a cada 10 segundos
        setInterval(() => {
            this.sendWebSocketMessage({
                type: 'get_unread_count'
            });
        }, 10000);
        
        // Enviar contadores iniciais
        this.sendWebSocketMessage({
            type: 'get_unread_count'
        });
        
        // Obter estatísticas de amigos a cada 30 segundos
        setInterval(() => {
            this.sendWebSocketMessage({
                type: 'get_friends_stats'
            });
        }, 30000);
        
        // Obter estatísticas iniciais
        this.sendWebSocketMessage({
            type: 'get_friends_stats'
        });
        
        // Obter status dos amigos a cada 15 segundos
        setInterval(() => {
            this.sendWebSocketMessage({
                type: 'get_friends_status'
            });
        }, 15000);
        
        // Obter status inicial dos amigos
        this.sendWebSocketMessage({
            type: 'get_friends_status'
        });
    }

    showError(message) {
        // Criar notificação de erro
        const errorDiv = document.createElement('div');
        errorDiv.className = 'notification error';
        errorDiv.textContent = message;
        
        document.body.appendChild(errorDiv);
        
        setTimeout(() => {
            errorDiv.style.opacity = '0';
            setTimeout(() => errorDiv.remove(), 300);
        }, 3000);
    }

    getFriendsStats() {
        this.sendWebSocketMessage({
            type: 'get_friends_stats'
        });
    }

    getFriendsStatus() {
        this.sendWebSocketMessage({
            type: 'get_friends_status'
        });
    }
}

// Inicializar quando o DOM estiver pronto
document.addEventListener('DOMContentLoaded', () => {
    window.websocketChat = new WebSocketChat();
}); 