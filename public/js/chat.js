const chatHistory = [];
let chatAberto = false;

function toggleChat() {
    chatAberto = !chatAberto;
    const win   = document.getElementById('chat-window');
    const badge = document.getElementById('chat-badge');
    const btn   = document.getElementById('chat-bubble');
    win.classList.toggle('aberto', chatAberto);
    btn.innerHTML = (chatAberto ? '×' : '💬') + '<span class="chat-badge" id="chat-badge"></span>';
    if (chatAberto) {
        document.getElementById('chat-badge').classList.remove('visible');
        document.getElementById('chat-input').focus();
        document.getElementById('chat-suggestions').style.display =
            chatHistory.length > 0 ? 'none' : 'flex';
    }
}

function addMsg(texto, tipo) {
    const msgs = document.getElementById('chat-messages');
    const div  = document.createElement('div');
    div.className = 'chat-msg ' + tipo;

    if (tipo === 'bot') {
        let html = texto
            .replace(
                /\[([^\]]+)\]\((https?:\/\/[^\)]+)\)/g,
                '<a href="$2" target="_blank" class="chat-link">$1 ↗</a>'
            )
            .replace(/\*\*([^*]+)\*\*/g, '<strong>$1</strong>')
            .replace(/\*([^*]+)\*/g, '<em>$1</em>')
            .replace(/\n/g, '<br>');
        div.innerHTML = html;
    } else {
        div.textContent = texto;
    }

    msgs.appendChild(div);
    msgs.scrollTop = msgs.scrollHeight;
    return div;
}

function enviarSugestao(btn) {
    document.getElementById('chat-input').value = btn.textContent;
    document.getElementById('chat-suggestions').style.display = 'none';
    enviarMensagem();
}

async function enviarMensagem() {
    const input = document.getElementById('chat-input');
    const send  = document.getElementById('chat-send');
    const texto = input.value.trim();
    if (!texto) return;

    input.value = '';
    send.disabled = true;
    document.getElementById('chat-suggestions').style.display = 'none';

    addMsg(texto, 'user');
    chatHistory.push({ role: 'user', content: texto });

    const typing = addMsg('Digitando...', 'digitando');

    try {
        const res = await fetch('/api/chat', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ messages: chatHistory })
        });
        const data = await res.json();
        typing.remove();

        const reply = data.reply || 'Desculpe, não consegui responder agora.';
        addMsg(reply, 'bot');
        chatHistory.push({ role: 'assistant', content: reply });

        if (!chatAberto) {
            document.getElementById('chat-badge').classList.add('visible');
        }
    } catch (err) {
        typing.remove();
        addMsg('Erro ao conectar. Tente novamente.', 'bot');
    }

    send.disabled = false;
    input.focus();
}
