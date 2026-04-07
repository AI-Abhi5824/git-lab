document.addEventListener('DOMContentLoaded', () => {
  const chatForm = document.getElementById('chatForm');
  const chatInput = document.getElementById('chatInput');
  const chatWindow = document.getElementById('chatWindow');

  if (!chatForm || !chatInput || !chatWindow) return;

  const conversation = [];

  const appendMessage = (role, text) => {
    const wrapper = document.createElement('div');
    wrapper.className = `mb-2 d-flex ${role === 'user' ? 'justify-content-end' : 'justify-content-start'}`;

    const bubble = document.createElement('div');
    bubble.className = role === 'user' ? 'chat-bubble user-bubble' : 'chat-bubble bot-bubble';
    bubble.textContent = text;

    wrapper.appendChild(bubble);
    chatWindow.appendChild(wrapper);
    chatWindow.scrollTop = chatWindow.scrollHeight;
  };

  appendMessage('bot', 'Hello! I am your chatbot. Ask me any question.');

  chatForm.addEventListener('submit', async (event) => {
    event.preventDefault();
    const message = chatInput.value.trim();
    if (!message) return;

    appendMessage('user', message);
    conversation.push({ role: 'user', content: message });
    chatInput.value = '';

    try {
      const response = await fetch('/api/chatbot', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message, history: conversation }),
      });

      const data = await response.json();
      const reply = data.reply || 'Sorry, I could not generate a response.';

      appendMessage('bot', reply);
      conversation.push({ role: 'assistant', content: reply });
    } catch (error) {
      appendMessage('bot', 'Unable to reach chatbot service right now.');
    }
  });
});
