const chatBody = document.getElementById('chatBody');
const chatInput = document.getElementById('chatInput');
const sendButton = document.getElementById('sendButton');

function currentTime() {
    return new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
}

document.getElementById('initial-time').textContent = currentTime();

// Id único por navegador, para que cada persona tenga su propio historial
let fallbackChatId = null;
function getChatId() {
    try {
        let id = localStorage.getItem('chat_id');
        if (!id) {
            id = crypto.randomUUID();
            localStorage.setItem('chat_id', id);
        }
        return id;
    } catch (e) {
        // Storage bloqueado: id válido solo mientras la página siga abierta
        if (!fallbackChatId) fallbackChatId = crypto.randomUUID();
        return fallbackChatId;
    }
}

function sendMessage() {
    const message = chatInput.value.trim();

    if (!message) return;

    chatBody.innerHTML += `<div class="message user"><div class="time">Tú - ${currentTime()}</div><div>${message}</div></div>`;
    chatInput.value = '';
    chatInput.disabled = true;
    sendButton.disabled = true;

    const typingIndicator = document.createElement('div');
    typingIndicator.className = 'typing-indicator';
    typingIndicator.innerHTML = '<div class="dot"></div><div class="dot"></div><div class="dot"></div>';
    chatBody.appendChild(typingIndicator);
    chatBody.scrollTop = chatBody.scrollHeight;

    fetch('/api/v1/bot/', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ chat_id: getChatId(), message: message })
    })
    .then(response => {
        if (response.status === 422) {
            throw new Error('Tu mensaje es demasiado largo. Intenta con uno más corto.');
        }
        if (!response.ok) {
            return response.json().then(err => {
                throw new Error(err.detail || `Error ${response.status}`);
            });
        }
        return response.json();
    })
    .then(data => {
        chatBody.removeChild(typingIndicator);
        chatBody.innerHTML += `<div class="message bot"><div class="time">Chatbot - ${currentTime()}</div><div>${data.response}</div></div>`;
        chatBody.scrollTop = chatBody.scrollHeight;
    })
    .catch(error => {
        console.error('Error:', error);
        chatBody.removeChild(typingIndicator);
        chatBody.innerHTML += `<div class="message bot"><div class="time">Chatbot - ${currentTime()}</div><div>Error: ${error.message}</div></div>`;
        chatBody.scrollTop = chatBody.scrollHeight;
    })
    .finally(() => {
        chatInput.disabled = false;
        sendButton.disabled = false;
        chatInput.focus();
    });
}

sendButton.addEventListener('click', sendMessage);
chatInput.addEventListener('keydown', (event) => {
    if (event.key === 'Enter') sendMessage();
});
