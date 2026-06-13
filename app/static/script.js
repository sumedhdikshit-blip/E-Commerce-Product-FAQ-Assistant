const chatForm = document.getElementById('chatForm');
const messageInput = document.getElementById('messageInput');
const chatMessages = document.getElementById('chatMessages');
const loadingIndicator = document.getElementById('loadingIndicator');
const quickReplies = document.querySelectorAll('.quick-reply');

function timeNow() {
  return new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
}

function appendMessage(text, sender) {
  const article = document.createElement('article');
  article.className = `message ${sender}`;

  const avatar = document.createElement('div');
  avatar.className = 'avatar';
  avatar.setAttribute('aria-hidden', 'true');
  avatar.textContent = sender === 'user' ? '🙂' : '🤖';

  const bubble = document.createElement('div');
  bubble.className = 'bubble';
  bubble.textContent = text;

  const time = document.createElement('span');
  time.className = 'timestamp';
  time.textContent = timeNow();
  bubble.appendChild(time);

  article.appendChild(avatar);
  article.appendChild(bubble);
  chatMessages.appendChild(article);
  chatMessages.scrollTop = chatMessages.scrollHeight;
}

async function fetchBotResponse(message) {
  const response = await fetch('/chat', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ message }),
  });

  if (!response.ok) {
    throw new Error(`Server error: ${response.status} ${response.statusText}`);
  }

  const data = await response.json();
  return data.response;
}

async function handleSend(text) {
  const trimmed = text.trim();
  if (!trimmed) return;

  appendMessage(trimmed, 'user');
  messageInput.value = '';

  loadingIndicator.hidden = false;
  chatMessages.scrollTop = chatMessages.scrollHeight;

  try {
    const botReply = await fetchBotResponse(trimmed);
    appendMessage(botReply, 'bot');
  } catch (error) {
    const isNetworkError = error instanceof TypeError && error.message === 'Failed to fetch';
    const userFacingMessage = isNetworkError
      ? "Couldn't reach the server. Please check your connection and try again."
      : "Something went wrong on our end. Please try again in a moment.";
    appendMessage(userFacingMessage, 'bot');
    console.error('[Chat] Failed to fetch bot response:', error);
  } finally {
    loadingIndicator.hidden = true;
  }
}

chatForm.addEventListener('submit', (e) => {
  e.preventDefault();
  handleSend(messageInput.value);
});

quickReplies.forEach((btn) => {
  btn.addEventListener('click', () => {
    handleSend(btn.dataset.text);
  });
});