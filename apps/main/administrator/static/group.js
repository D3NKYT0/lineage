const isLocalhost = window.location.hostname === '127.0.0.1';
const protocol = isLocalhost ? 'ws://' : 'wss://';
const chatSocket = new WebSocket(
    protocol + window.location.host + '/ws/chat/' + groupName + '/'
);    

chatSocket.onerror = function(e) {
    console.error('WebSocket error:', e);
};

chatSocket.onmessage = function(e) {
    const data = JSON.parse(e.data);
    if (data.error) {
        console.error('Chat error:', data.error);
        return;
    }
    appendMessage(data.message, data.sender, data.avatar_url, data.sender === currentUser, data.timestamp);
};

chatSocket.onclose = function(e) {
    console.error('Chat socket closed unexpectedly');
    showConnectionStatus('Desconectado', 'danger');
};

chatSocket.onopen = function(e) {
    console.log('Chat socket connected');
    showConnectionStatus('Conectado', 'success');
};

document.querySelector('#chat-message-input').focus();

document.querySelector('#chat-message-input').onkeyup = function(e) {
    if (e.keyCode === 13) {  
        document.querySelector('#chat-message-submit').click();
    }
};

document.querySelector('#chat-message-submit').onclick = function(e) {
    const messageInputDom = document.querySelector('#chat-message-input');
    const message = messageInputDom.value;
    if (message.trim()) {
        chatSocket.send(JSON.stringify({
            'message': message,
            'sender': currentUser
        }));
        appendMessage(message, currentUser, currentUserAvatar, true, null);
        messageInputDom.value = '';
    }
};

function appendMessage(message, sender, avatarUrl, isSent, timestamp = null) {
    const messagesContainer = document.getElementById('messages-container');
    const chatLog = document.getElementById('chat-log');

    // Usa o timestamp fornecido ou gera um novo
    const messageTimestamp = timestamp || new Date().toLocaleString([], { 
        year: 'numeric', 
        month: '2-digit', 
        day: '2-digit', 
        hour: '2-digit', 
        minute: '2-digit', 
        second: '2-digit',
        hour12: false
    });
    
    const senderName = sender;

    const messageDiv = document.createElement('div');
    messageDiv.classList.add('chat-message', isSent ? 'sent' : 'received');
    messageDiv.style.animation = 'fadeInUp 0.3s ease-out';

    messageDiv.innerHTML = `
        <div class="avatar-container">
            <img src="${avatarUrl}" alt="${senderName}" />
        </div>
        <div class="message-content">
            <div class="message-header">
                <strong class="sender-name">${senderName}</strong>
                <span class="message-time">${messageTimestamp}</span>
            </div>
            <div class="message-text">${escapeHtml(message)}</div>
        </div>
    `;

    messagesContainer.appendChild(messageDiv);
    chatLog.scrollTop = chatLog.scrollHeight;
}

// Função para escapar HTML e prevenir XSS
function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

// Função para mostrar status da conexão
function showConnectionStatus(message, type) {
    const statusDiv = document.getElementById('connection-status');
    if (statusDiv) {
        statusDiv.className = `alert alert-${type} alert-dismissible fade show`;
        statusDiv.innerHTML = `
            <i class="fas fa-${type === 'success' ? 'check-circle' : 'exclamation-triangle'}"></i>
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        `;
        statusDiv.style.display = 'block';
        
        // Auto-hide after 3 seconds for success messages
        if (type === 'success') {
            setTimeout(() => {
                statusDiv.style.display = 'none';
            }, 3000);
        }
    }
}

document.addEventListener('DOMContentLoaded', () => {
    const chatInput = document.querySelector('#chat-message-input');
    const emojiButton = document.querySelector('#emoji-button');
    
    // Inicialize o Emoji Button
    const picker = new EmojiButton();

    // Mostra o seletor de emojis ao clicar no botão
    emojiButton.addEventListener('click', () => {
        picker.togglePicker(emojiButton);
    });

    // Insere o emoji no campo de texto quando selecionado
    picker.on('emoji', emoji => {
        chatInput.value += emoji;
        chatInput.focus(); // Foca no campo de texto após inserir o emoji
    });

    const chatLog = document.getElementById('chat-log');
    chatLog.scrollTop = chatLog.scrollHeight;
});
