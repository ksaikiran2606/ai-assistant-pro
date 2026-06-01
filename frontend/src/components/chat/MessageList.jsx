import MessageItem from './MessageItem';
import TypingIndicator from './TypingIndicator';
import MarkdownRenderer from '../common/MarkdownRenderer';
import { useAutoScroll } from '../../hooks/useAutoScroll';

export default function MessageList({ messages, streamingContent, isStreaming }) {
  const bottomRef = useAutoScroll([messages, streamingContent, isStreaming]);

  if (messages.length === 0 && !isStreaming) {
    return (
      <div className="flex-1 flex flex-col items-center justify-center px-4 text-center animate-fade-in">
        <div className="w-16 h-16 rounded-2xl bg-gradient-to-br from-primary-500 to-emerald-500 flex items-center justify-center mb-4">
          <span className="text-2xl font-bold text-white">AI</span>
        </div>
        <h2 className="text-2xl font-bold mb-2">AI Assistant Pro</h2>
        <p className="text-gray-500 dark:text-gray-400 max-w-md">
          Your intelligent assistant for coding, writing, analysis, and more.
          Start a conversation below.
        </p>
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 mt-8 max-w-lg w-full">
          {[
            'Explain quantum computing simply',
            'Write a Python REST API',
            'Help me debug my code',
            'Summarize this concept',
          ].map((suggestion) => (
            <div
              key={suggestion}
              className="card p-3 text-sm text-left text-gray-600 dark:text-gray-400 hover:border-primary-500 cursor-default transition-colors"
            >
              {suggestion}
            </div>
          ))}
        </div>
      </div>
    );
  }

  return (
    <div className="flex-1 overflow-y-auto">
      <div className="max-w-3xl mx-auto">
        {messages.map((msg) => (
          <MessageItem key={msg.id || `${msg.role}-${msg.created_at}`} message={msg} />
        ))}
        {isStreaming && (
          <div className="flex gap-3 px-4 py-4 bg-gray-50 dark:bg-neutral-900/50 animate-fade-in">
            <div className="flex-shrink-0 w-8 h-8 rounded-full bg-gradient-to-br from-emerald-500 to-teal-600 flex items-center justify-center text-sm font-semibold text-white">
              AI
            </div>
            <div className="flex-1 min-w-0">
              {streamingContent ? (
                <MarkdownRenderer content={streamingContent} />
              ) : (
                <TypingIndicator />
              )}
            </div>
          </div>
        )}
        <div ref={bottomRef} />
      </div>
    </div>
  );
}
