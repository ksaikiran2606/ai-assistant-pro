import api from './axios';

export const getChats = (search) =>
  api.get('/chats', { params: search ? { search } : {} });
export const createChat = (title) => api.post('/chats', { title });
export const renameChat = (id, title) => api.patch(`/chats/${id}`, { title });
export const deleteChat = (id) => api.delete(`/chats/${id}`);
export const getMessages = (chatId) => api.get(`/messages/${chatId}`);
export const getProfile = () => api.get('/profile');

export const sendMessageStream = async (chatId, content, onChunk, onDone, onError) => {
  const token = localStorage.getItem('token');
  const API_URL = import.meta.env.VITE_API_URL || '';

  const response = await fetch(`${API_URL}/api/messages`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      Authorization: `Bearer ${token}`,
    },
    body: JSON.stringify({ chat_id: chatId, content }),
  });

  if (!response.ok) {
    const err = await response.json().catch(() => ({ detail: 'Request failed' }));
    onError(err.detail || 'Failed to send message');
    return;
  }

  const reader = response.body.getReader();
  const decoder = new TextDecoder();
  let buffer = '';

  while (true) {
    const { done, value } = await reader.read();
    if (done) break;

    buffer += decoder.decode(value, { stream: true });
    const lines = buffer.split('\n');
    buffer = lines.pop() || '';

    for (const line of lines) {
      if (line.startsWith('data: ')) {
        try {
          const data = JSON.parse(line.slice(6));
          if (data.error) {
            onError(data.error);
            return;
          }
          if (data.content) onChunk(data.content);
          if (data.done) onDone();
        } catch {
          /* skip malformed */
        }
      }
    }
  }
  onDone();
};
