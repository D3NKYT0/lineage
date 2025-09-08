document.addEventListener('DOMContentLoaded', () => {
    const chatInput = document.querySelector('#message-input');
    const emojiButton = document.querySelector('#emoji-button');
    const toggleButton = document.getElementById('toggle-friend-list');
    const friendListContent = document.getElementById('friend-list-content');
    const chatSection = toggleButton.closest('.row').querySelector('.col-lg-9');
    const sendMessageButton = document.getElementById('send-message');
    const messageInput = document.getElementById('message-input');
    const messageContainer = document.getElementById('message-container');
    const messageInputGroup = document.getElementById('message-input-group');
    const friendItems = document.querySelectorAll('.friend-item');

    let activeFriendId = null;
    let messageReloadInterval = null;

    // EMOJI PICKER
    const picker = new EmojiButton();
    emojiButton.addEventListener('click', () => picker.togglePicker(emojiButton));
    picker.on('emoji', emoji => {
        chatInput.value += emoji;
        chatInput.focus();
    });

    // TOGGLE AMIGOS
    toggleButton.addEventListener('click', () => {
        friendListContent.classList.toggle('hidden');
        chatSection.classList.toggle('col-lg-9');
        chatSection.classList.toggle('col-lg-12');
        toggleButton.classList.toggle('fa-plus');
        toggleButton.classList.toggle('fa-times');
    });

    // ENVIAR MENSAGEM
    sendMessageButton.addEventListener('click', sendMessage);

    function sendMessage() {
        const message = messageInput.value.trim();
        if (!message || !activeFriendId) return;
    
        fetch('/app/message/api/send-message/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': csrfToken
            },
            body: JSON.stringify({ message, friend_id: activeFriendId })
        })
        .then(res => res.json())
        .then(data => {
            if (data.success) {
                const formatted = message.replace(/\n/g, '<br>');
                messageContainer.innerHTML += `
                    <div class="media mb-3 d-flex justify-content-end text-end" style="gap: 5px;">
                        <div class="media-body" style="max-width: 80%;">
                            <div class="current-user">
                                <div class="title-current">
                                    <h6 class="m-0 fw-bold">${currentUser}</h6>
                                    <small class="text-dark">${new Date().toLocaleString()}</small>
                                </div>
                                <p class="m-0" style="font-size: 12pt; word-break: break-word; white-space: pre-wrap;">${formatted}</p>
                            </div>
                        </div>
                        <img src="${avatarUrl}" class="rounded-circle ms-3" alt="Avatar" width="40" height="40">
                    </div>
                `;
                messageInput.value = '';
                messageContainer.scrollTop = messageContainer.scrollHeight;
            }
        })
        .catch(console.error);
    }    

    // TECLA ENTER / SHIFT
    messageInput.addEventListener('keydown', e => {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            sendMessage();
        } else if (e.key === 'Enter' && e.shiftKey) {
            e.preventDefault();
            const pos = messageInput.selectionStart;
            messageInput.value = messageInput.value.slice(0, pos) + '\n' + messageInput.value.slice(pos);
            messageInput.selectionEnd = pos + 1;
        }
    });

    // CARREGAR MENSAGENS
    friendItems.forEach(item => {
        const friendId = item.getAttribute('data-friend-id');

        item.addEventListener('click', () => {
            activeFriendId = friendId;
            loadMessages(friendId);

            friendItems.forEach(f => {
                f.classList.remove('active');
                f.querySelector('.friend-status')?.classList.remove('shadow-text');
            });

            item.classList.add('active');
            item.querySelector('.friend-status')?.classList.add('shadow-text');
            messageInputGroup.style.display = 'flex';

            if (messageReloadInterval) clearInterval(messageReloadInterval);
            messageReloadInterval = setInterval(() => loadMessages(friendId), 3000);
        });

        // CHECK ONLINE STATUS
        fetch(`/app/message/api/check-user-activity/${friendId}/`)
            .then(res => res.json())
            .then(data => {
                const status = item.querySelector('.friend-status');
                if (status) {
                    status.classList.toggle('text-success', data.is_online);
                    status.classList.toggle('text-danger', !data.is_online);
                    status.innerText = data.is_online ? 'Online' : 'Offline';
                }
            })
            .catch(console.error);
    });

    function loadMessages(friendId) {
        fetch(`/app/message/api/load-messages/${friendId}/`)
            .then(res => res.json())
            .then(data => {
                messageContainer.innerHTML = '';

                data.messages.forEach(msg => {
                    const isUser = msg.sender.username === currentUser;
                    const formatted = msg.text.replace(/\n/g, '<br>');
                
                    messageContainer.innerHTML += `
                        <div class="media mb-3 d-flex ${isUser ? 'justify-content-end text-end' : 'justify-content-start text-start'}" style="gap: 5px;">
                            ${!isUser ? `<img src="${msg.sender.avatar_url}" class="rounded-circle me-3" alt="${msg.sender.username}" width="40" height="40">` : ''}
                            <div class="media-body" style="max-width: 80%;">
                                <div class="${isUser ? 'current-user' : 'current-friend'}">
                                    <div class="${isUser ? 'title-current' : 'title-friend'}">
                                        <h6 class="m-0 fw-bold">${msg.sender.username}</h6>
                                        <small class="text-dark">${new Date(msg.timestamp).toLocaleString()}</small>
                                    </div>
                                    <p class="m-0" style="font-size: 12pt; word-break: break-word; white-space: pre-wrap;">${formatted}</p>
                                </div>
                            </div>
                            ${isUser ? `<img src="${msg.sender.avatar_url}" class="rounded-circle ms-3" alt="${msg.sender.username}" width="40" height="40">` : ''}
                        </div>`;
                });                

                if (data.has_unread_messages) {
                    messageContainer.scrollTop = messageContainer.scrollHeight;
                }
            })
            .catch(console.error);
    }

    // CONTADORES DE MENSAGENS NÃO LIDAS
    function updateUnreadCounts() {
        fetch('/app/message/api/get_unread_count/')
            .then(res => res.json())
            .then(response => {
                for (const [friendId, count] of Object.entries(response.unread_counts)) {
                    const el = document.getElementById(`unread-count-${friendId}`);
                    if (!el) continue;

                    el.textContent = count > 0 ? count : "";
                    el.classList.toggle('bg-success', count > 0);
                    el.classList.toggle('text-white', count > 0);
                }
            })
            .catch(err => console.error('Erro ao carregar contadores:', err));
    }

    setInterval(updateUnreadCounts, 5000);
    updateUnreadCounts();

    // STATUS DE ATIVIDADE
    function setUserActive() {
        fetch('/app/message/api/set-user-active/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': csrfToken
            }
        })
        .then(res => res.json())
        .then(data => console.log('Atividade registrada:', data))
        .catch(console.error);
    }

    setInterval(setUserActive, 300000);
    setUserActive();
});

// FILTRO DE AMIGOS
function filterFriends() {
    const input = document.getElementById('msg-friends').value.toLowerCase();
    const items = document.querySelectorAll('.friend-item');

    document.getElementById("smileys").style.display = "block";

    items.forEach(item => {
        const name = item.querySelector('.friend-name').textContent.toLowerCase();
        item.classList.toggle('desativar', !name.includes(input));
    });
}

// TABS
function openTab(evt, tabName) {
    document.querySelectorAll(".tab-content").forEach(el => el.style.display = "none");
    document.querySelectorAll(".tab-button").forEach(btn => btn.classList.remove("active"));

    document.getElementById(tabName).style.display = "block";
    evt.currentTarget.classList.add("active");
}
