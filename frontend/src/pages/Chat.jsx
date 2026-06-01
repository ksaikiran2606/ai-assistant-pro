import { useState, useEffect, useRef, useCallback } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import Sidebar from '../components/layout/Sidebar';
import Header from '../components/layout/Header';
import MessageList from '../components/chat/MessageList';
import ChatInput from '../components/chat/ChatInput';
import LoadingSpinner from '../components/common/LoadingSpinner';
import { useKeyboardShortcuts } from '../hooks/useKeyboardShortcuts';
import { exportToTxt, exportToPdf } from '../utils/exportChat';
import {
  getChats,
  createChat,
  deleteChat,
  renameChat,
  getMessages,
  sendMessageStream,
} from '../api/chats';

export default function Chat() {
  const { chatId } = useParams();
  const navigate = useNavigate();
  const inputRef = useRef(null);

  const [chats, setChats] = useState([]);
  const [messages, setMessages] = useState([]);
  const [activeChat, setActiveChat] = useState(null);
  const [search, setSearch] = useState('');
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const [loading, setLoading] = useState(true);
  const [isStreaming, setIsStreaming] = useState(false);
  const [streamingContent, setStreamingContent] = useState('');
  const [error, setError] = useState('');

  const loadChats = useCallback(async (searchTerm) => {
    try {
      const { data } = await getChats(searchTerm || undefined);
      setChats(data.chats);
    } catch {
      setError('Failed to load chats');
    }
  }, []);

  const loadMessages = useCallback(async (id) => {
    try {
      const { data } = await getMessages(id);
      setMessages(data.messages);
    } catch {
      setError('Failed to load messages');
    }
  }, []);

  useEffect(() => {
    const init = async () => {
      setLoading(true);
      await loadChats(search);
      if (chatId) {
        const chat = (await getChats()).data.chats.find((c) => c.id === Number(chatId));
        setActiveChat(chat || null);
        await loadMessages(chatId);
      } else {
        setActiveChat(null);
        setMessages([]);
      }
      setLoading(false);
    };
    init();
  }, [chatId, loadChats, loadMessages]);

  useEffect(() => {
    const timer = setTimeout(() => loadChats(search), 300);
    return () => clearTimeout(timer);
  }, [search, loadChats]);

  const handleNewChat = async () => {
    try {
      const { data } = await createChat('New Chat');
      await loadChats(search);
      navigate(`/chat/${data.id}`);
      setSidebarOpen(false);
    } catch {
      setError('Failed to create chat');
    }
  };

  const handleDeleteChat = async (id) => {
    if (!confirm('Delete this conversation?')) return;
    try {
      await deleteChat(id);
      await loadChats(search);
      if (Number(chatId) === id) navigate('/');
    } catch {
      setError('Failed to delete chat');
    }
  };

  const handleRenameChat = async (id, title) => {
    try {
      await renameChat(id, title);
      await loadChats(search);
      if (activeChat?.id === id) setActiveChat({ ...activeChat, title });
    } catch {
      setError('Failed to rename chat');
    }
  };

  const handleSend = async (content) => {
    setError('');
    let currentChatId = chatId;

    if (!currentChatId) {
      try {
        const { data } = await createChat('New Chat');
        currentChatId = data.id;
        setActiveChat(data);
        await loadChats(search);
        navigate(`/chat/${data.id}`, { replace: true });
      } catch {
        setError('Failed to create chat');
        return;
      }
    }

    const userMsg = {
      id: `temp-${Date.now()}`,
      role: 'user',
      content,
      created_at: new Date().toISOString(),
    };
    setMessages((prev) => [...prev, userMsg]);
    setIsStreaming(true);
    setStreamingContent('');

    sendMessageStream(
      Number(currentChatId),
      content,
      (chunk) => setStreamingContent((prev) => prev + chunk),
      async () => {
        setIsStreaming(false);
        setStreamingContent('');
        await loadMessages(currentChatId);
        await loadChats(search);
        const updated = (await getChats()).data.chats.find((c) => c.id === Number(currentChatId));
        if (updated) setActiveChat(updated);
      },
      (err) => {
        setIsStreaming(false);
        setStreamingContent('');
        setError(typeof err === 'string' ? err : 'AI response failed');
      }
    );
  };

  useKeyboardShortcuts({
    onNewChat: handleNewChat,
    onFocusInput: () => inputRef.current?.focus(),
    onEscape: () => setSidebarOpen(false),
  });

  const chatTitle = activeChat?.title || 'New Chat';

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <LoadingSpinner size="lg" />
      </div>
    );
  }

  return (
    <div className="flex h-screen overflow-hidden bg-white dark:bg-neutral-950">
      <Sidebar
        chats={chats}
        activeChatId={chatId ? Number(chatId) : null}
        onNewChat={handleNewChat}
        onDeleteChat={handleDeleteChat}
        onRenameChat={handleRenameChat}
        search={search}
        onSearchChange={setSearch}
        isOpen={sidebarOpen}
        onClose={() => setSidebarOpen(false)}
      />
      <main className="flex-1 flex flex-col min-w-0">
        <Header
          title={chatTitle}
          onMenuClick={() => setSidebarOpen(true)}
          onExportTxt={() => exportToTxt(chatTitle, messages)}
          onExportPdf={() => exportToPdf(chatTitle, messages)}
        />
        {error && (
          <div className="mx-4 mt-2 px-4 py-2 bg-red-100 dark:bg-red-900/30 text-red-700 dark:text-red-300 rounded-lg text-sm animate-fade-in">
            {error}
            <button onClick={() => setError('')} className="ml-2 underline">
              Dismiss
            </button>
          </div>
        )}
        <MessageList
          messages={messages}
          streamingContent={streamingContent}
          isStreaming={isStreaming}
        />
        <ChatInput onSend={handleSend} disabled={isStreaming} inputRef={inputRef} />
      </main>
    </div>
  );
}
