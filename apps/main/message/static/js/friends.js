// Friends page JavaScript functions

// Real-time search functionality
let searchTimeout;
const searchInput = document.getElementById('search-input');
const searchResults = document.getElementById('search-results');

if (searchInput) {
    searchInput.addEventListener('input', function() {
        clearTimeout(searchTimeout);
        const query = this.value.trim();
        
        if (query.length < 2) {
            searchResults.style.display = 'none';
            return;
        }
        
        searchTimeout = setTimeout(() => {
            fetch(`/app/message/api/search-users/?q=${encodeURIComponent(query)}`)
                .then(response => response.json())
                .then(data => {
                    if (data.users.length > 0) {
                        displaySearchResults(data.users);
                    } else {
                        searchResults.style.display = 'none';
                    }
                })
                .catch(error => {
                    console.error('Erro na busca:', error);
                });
        }, 300);
    });
    
    // Hide results when clicking outside
    document.addEventListener('click', function(e) {
        if (!searchInput.contains(e.target) && !searchResults.contains(e.target)) {
            searchResults.style.display = 'none';
        }
    });
}

function displaySearchResults(users) {
    const resultsHtml = users.map(user => {
        let statusHtml = '';
        if (user.is_email_verified) {
            statusHtml += '<span class="verified-badge" title="E-mail verificado"><i class="fas fa-check-circle"></i> Verificado</span>';
        }
        statusHtml += `<span class="fichas-badge" title="Fichas do jogo"><i class="fas fa-coins"></i> ${user.fichas}</span>`;
        
        return `
            <div class="realtime-result-item" onclick="sendFriendRequest(${user.id})">
                <div class="result-avatar">
                    <div class="avatar-container" style="width: 60px; height: 60px; border-radius: 50%; overflow: hidden; border: 2px solid rgba(255, 255, 255, 0.3); box-shadow: 0 3px 10px rgba(0, 0, 0, 0.15); position: relative;">
                        <img src="${user.has_avatar ? '/decrypted-file/home/user/avatar/' + user.uuid + '/' : '/static/assets/img/team/generic_user.png'}" 
                             alt="${user.username}"
                             style="width: 100%; height: 100%; object-fit: cover; background-color: #cbd5e1;" />
                    </div>
                </div>
                <div class="result-info">
                    <div class="result-name">${user.username}</div>
                    ${user.first_name || user.last_name ? `<div class="result-fullname">${user.first_name} ${user.last_name}</div>` : ''}
                    ${user.bio ? `<div class="result-bio">${user.bio.substring(0, 50)}${user.bio.length > 50 ? '...' : ''}</div>` : ''}
                    <div class="result-status">${statusHtml}</div>
                </div>
                <div class="result-action">
                    <i class="fas fa-user-plus"></i>
                </div>
            </div>
        `;
    }).join('');
    
    searchResults.innerHTML = resultsHtml;
    searchResults.style.display = 'block';
}

// Action functions - Define them directly in global scope
window.sendFriendRequest = function(userId) {
    try {
        console.log('Enviando solicitação de amizade para usuário:', userId);
        const url = `/app/message/send-friend-request/${userId}/`;
        console.log('URL:', url);
        window.location.href = url;
    } catch (error) {
        console.error('Erro ao enviar solicitação de amizade:', error);
        alert('Erro ao enviar solicitação de amizade. Tente novamente.');
    }
};

window.removeFriend = function(friendshipId) {
    try {
        console.log('Removendo amigo com friendship ID:', friendshipId);
        if (confirm('Tem certeza que deseja remover este amigo?')) {
            const url = `/app/message/remove-friend/${friendshipId}/`;
            console.log('URL:', url);
            window.location.href = url;
        }
    } catch (error) {
        console.error('Erro ao remover amigo:', error);
        alert('Erro ao remover amigo. Tente novamente.');
    }
};

window.acceptRequest = function(requestId) {
    try {
        console.log('Aceitando solicitação com ID:', requestId);
        const url = `/app/message/accept-friend-request/${requestId}/`;
        console.log('URL:', url);
        window.location.href = url;
    } catch (error) {
        console.error('Erro ao aceitar solicitação:', error);
        alert('Erro ao aceitar solicitação. Tente novamente.');
    }
};

window.rejectRequest = function(requestId) {
    try {
        console.log('Recusando solicitação com ID:', requestId);
        if (confirm('Tem certeza que deseja recusar esta solicitação?')) {
            const url = `/app/message/reject-friend-request/${requestId}/`;
            console.log('URL:', url);
            window.location.href = url;
        }
    } catch (error) {
        console.error('Erro ao recusar solicitação:', error);
        alert('Erro ao recusar solicitação. Tente novamente.');
    }
};

window.cancelRequest = function(requestId) {
    try {
        console.log('Cancelando solicitação com ID:', requestId);
        if (confirm('Tem certeza que deseja cancelar esta solicitação?')) {
            const url = `/app/message/cancel-friend-request/${requestId}/`;
            console.log('URL:', url);
            window.location.href = url;
        }
    } catch (error) {
        console.error('Erro ao cancelar solicitação:', error);
        alert('Erro ao cancelar solicitação. Tente novamente.');
    }
};

window.sendMessage = function(friendId) {
    try {
        console.log('Enviando mensagem para o usuário:', friendId);
        const url = `/app/message/index/`;
        console.log('URL:', url);
        window.location.href = url;
    } catch (error) {
        console.error('Erro ao abrir mensagens:', error);
        alert('Erro ao abrir mensagens. Tente novamente.');
    }
};

// Update statistics using WebSocket
window.updateStats = function() {
    // Se o WebSocket estiver disponível, usar ele
    if (window.websocketChat && window.websocketChat.getFriendsStats) {
        window.websocketChat.getFriendsStats();
    } else {
        // Fallback para AJAX se WebSocket não estiver disponível
        fetch('/app/message/api/friends-stats/')
            .then(response => response.json())
            .then(data => {
                updateStatsDisplay(data);
            })
            .catch(error => {
                console.error('Erro ao atualizar estatísticas:', error);
            });
    }
};

// Função para atualizar a exibição das estatísticas
function updateStatsDisplay(data) {
    document.getElementById('total-friends').textContent = data.total_friends;
    document.getElementById('pending-requests').textContent = data.total_pending_requests;
    document.getElementById('sent-requests').textContent = data.total_sent_requests;
    
    // Update section counts
    const friendsCount = document.querySelector('.friends-section .section-count');
    const pendingCount = document.querySelector('.pending-section .section-count');
    if (friendsCount) friendsCount.textContent = data.total_friends;
    if (pendingCount) pendingCount.textContent = data.total_pending_requests;
}

// Listen for WebSocket friends stats updates
document.addEventListener('friendsStatsUpdated', function(event) {
    updateStatsDisplay(event.detail);
});

// Listen for WebSocket friends status updates
document.addEventListener('friendsStatusUpdated', function(event) {
    updateFriendsStatus(event.detail);
});

// Função para atualizar o status dos amigos
function updateFriendsStatus(friendsStatus) {
    Object.entries(friendsStatus).forEach(([friendId, status]) => {
        const statusElement = document.querySelector(`[data-friend-id="${friendId}"] .friend-status`);
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
}

// Update statistics every 30 seconds
setInterval(updateStats, 30000);

// Add loading animation to refresh button
const refreshButton = document.querySelector('.btn-refresh');
if (refreshButton) {
    refreshButton.addEventListener('click', function() {
        this.classList.add('spinning');
        setTimeout(() => {
            this.classList.remove('spinning');
        }, 1000);
    });
}

// Initialize when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    console.log('Friends page JavaScript loaded successfully');
    
    // Double-check that functions are available
    if (typeof window.sendFriendRequest === 'undefined') {
        console.error('sendFriendRequest function not available');
    }
    if (typeof window.removeFriend === 'undefined') {
        console.error('removeFriend function not available');
    }
    if (typeof window.sendMessage === 'undefined') {
        console.error('sendMessage function not available');
    }
}); 