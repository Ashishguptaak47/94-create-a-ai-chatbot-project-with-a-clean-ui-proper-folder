document.addEventListener('DOMContentLoaded', () => {
  let currentPersona = 'assistant';
  let sessionId = 'session_' + Math.random().toString(36).substring(2, 10);

  const personaCards = document.querySelectorAll('.persona-card');
  const chatContainer = document.getElementById('chat-container');
  const chatForm = document.getElementById('chat-form');
  const userInput = document.getElementById('user-input');
  const activePersonaName = document.getElementById('active-persona-name');
  const activePersonaRole = document.getElementById('active-persona-role');
  const btnClear = document.getElementById('btn-clear');
  const btnExport = document.getElementById('btn-export');
  const chips = document.querySelectorAll('.chip');

  // Persona switching
  personaCards.forEach(card => {
    card.addEventListener('click', () => {
      personaCards.forEach(c => c.classList.remove('active'));
      card.classList.add('active');
      currentPersona = card.dataset.persona;
      activePersonaName.textContent = card.querySelector('.p-name').textContent;
      activePersonaRole.textContent = card.querySelector('.p-desc').textContent;
      appendNotice(`Switched persona to ${activePersonaName.textContent}.`);
    });
  });

  // Quick prompt chips
  chips.forEach(chip => {
    chip.addEventListener('click', () => {
      userInput.value = chip.dataset.prompt;
      userInput.focus();
    });
  });

  // Auto resize textarea
  userInput.addEventListener('input', () => {
    userInput.style.height = 'auto';
    userInput.style.height = Math.min(userInput.scrollHeight, 120) + 'px';
  });

  userInput.addEventListener('keydown', (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      chatForm.dispatchEvent(new Event('submit'));
    }
  });

  // Send Message via SSE Streaming
  chatForm.addEventListener('submit', async (e) => {
    e.preventDefault();
    const message = userInput.value.trim();
    if (!message) return;

    appendMessage('user', message);
    userInput.value = '';
    userInput.style.height = 'auto';

    const botMsgBody = appendMessage('bot', '');
    const textContainer = botMsgBody.querySelector('.bubble-text');

    try {
      const params = new URLSearchParams({
        session_id: sessionId,
        message: message,
        persona: currentPersona
      });

      const response = await fetch(`/api/chat/stream?${params.toString()}`);
      if (!response.ok) throw new Error('Stream request failed');

      const reader = response.body.getReader();
      const decoder = new TextDecoder();
      let accumulated = '';

      while (true) {
        const { value, done } = await reader.read();
        if (done) break;

        const chunk = decoder.decode(value);
        const lines = chunk.split('\n');

        for (const line of lines) {
          if (line.startsWith('data: ')) {
            const dataStr = line.slice(6).trim();
            if (dataStr === '[DONE]') break;
            try {
              const parsed = JSON.parse(dataStr);
              accumulated += parsed.token;
              textContainer.textContent = accumulated;
              chatContainer.scrollTop = chatContainer.scrollHeight;
            } catch (err) {}
          }
        }
      }
    } catch (err) {
      textContainer.textContent = 'Sorry, an error occurred while streaming the response.';
    }
  });

  // Append chat message helper
  function appendMessage(role, content) {
    const bubble = document.createElement('div');
    bubble.className = `message-bubble ${role}`;

    const avatar = document.createElement('div');
    avatar.className = 'bubble-avatar';
    avatar.textContent = role === 'user' ? 'U' : '✦';

    const body = document.createElement('div');
    body.className = 'bubble-body';

    const meta = document.createElement('div');
    meta.className = 'bubble-meta';
    meta.textContent = role === 'user' ? 'You • Just now' : `${activePersonaName.textContent} • Just now`;

    const text = document.createElement('div');
    text.className = 'bubble-text';
    text.textContent = content;

    body.appendChild(meta);
    body.appendChild(text);
    bubble.appendChild(avatar);
    bubble.appendChild(body);
    chatContainer.appendChild(bubble);

    chatContainer.scrollTop = chatContainer.scrollHeight;
    return body;
  }

  function appendNotice(note) {
    const noteEl = document.createElement('div');
    noteEl.style.cssText = 'text-align:center; font-size: 0.75rem; color: #64748b; margin: 0.5rem 0;';
    noteEl.textContent = `— ${note} —`;
    chatContainer.appendChild(noteEl);
    chatContainer.scrollTop = chatContainer.scrollHeight;
  }

  // Clear History
  btnClear.addEventListener('click', async () => {
    await fetch(`/api/history/${sessionId}`, { method: 'DELETE' });
    chatContainer.innerHTML = '';
    appendNotice('Conversation memory has been cleared.');
  });

  // Export Chat
  btnExport.addEventListener('click', async () => {
    const res = await fetch(`/api/history/${sessionId}`);
    const data = await res.json();
    const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `chat-export-${Date.now()}.json`;
    a.click();
    URL.revokeObjectURL(url);
  });
});
