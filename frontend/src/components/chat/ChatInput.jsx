import { useRef, useEffect } from 'react';

export default function ChatInput({ onSend, disabled, inputRef }) {
  const localRef = useRef(null);
  const ref = inputRef || localRef;

  useEffect(() => {
    ref.current?.focus();
  }, []);

  const handleSubmit = (e) => {
    e.preventDefault();
    const text = ref.current?.value.trim();
    if (!text || disabled) return;
    onSend(text);
    ref.current.value = '';
    ref.current.style.height = 'auto';
  };

  const handleKeyDown = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSubmit(e);
    }
  };

  const handleInput = () => {
    const el = ref.current;
    el.style.height = 'auto';
    el.style.height = Math.min(el.scrollHeight, 200) + 'px';
  };

  return (
    <form onSubmit={handleSubmit} className="border-t border-gray-200 dark:border-neutral-800 p-4">
      <div className="max-w-3xl mx-auto flex gap-3 items-end">
        <textarea
          ref={ref}
          rows={1}
          placeholder="Message AI Assistant Pro... (Enter to send, Shift+Enter for new line)"
          disabled={disabled}
          onKeyDown={handleKeyDown}
          onInput={handleInput}
          className="input-field resize-none min-h-[44px] max-h-[200px] py-3"
        />
        <button
          type="submit"
          disabled={disabled}
          className="btn-primary flex-shrink-0 h-[44px] px-5"
        >
          <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 19l9 2-9-18-9 18 9-2zm0 0v-8" />
          </svg>
        </button>
      </div>
      <p className="text-center text-xs text-gray-400 mt-2">
        Ctrl+K new chat · Ctrl+/ focus input
      </p>
    </form>
  );
}
