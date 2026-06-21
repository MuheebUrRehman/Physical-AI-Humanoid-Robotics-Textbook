import React, { useState, useEffect, useCallback, useMemo } from 'react';
import { ChatKit, useChatKit } from '@openai/chatkit-react';
import useDocusaurusContext from '@docusaurus/useDocusaurusContext';
import styles from './ChatKitWidget.module.css';
import { createChatKitFetch } from '../utils/chatkit-fetch';

const ChatKitWidget: React.FC = () => {
  const {siteConfig} = useDocusaurusContext();
  const {customFields} = siteConfig as typeof siteConfig & {customFields: {apiBaseUrl?: string; chatkitDomainKey?: string}};
  const apiBaseUrl = customFields?.apiBaseUrl || 'http://localhost:8000';
  const chatkitDomainKey = customFields?.chatkitDomainKey || 'physical-ai-textbook-local';

  const [isOpen, setIsOpen] = useState(false);
  const [selection, setSelection] = useState<{ text: string; x: number; y: number } | null>(null);
  const [error, setError] = useState<string | null>(null);

  // Initialize a persistent student ID for development
  const [studentId] = useState(() => {
    if (typeof window !== 'undefined') {
      try {
        const saved = localStorage.getItem('chatkit_student_id');
        if (saved) return saved;
      } catch {
        // localStorage unavailable (private browsing, storage full)
      }
      const newId = 'student-' + Math.random().toString(36).substring(2, 11);
      try {
        localStorage.setItem('chatkit_student_id', newId);
      } catch {
        // fall through — use in-memory only
      }
      return newId;
    }
    return 'anonymous';
  });

  // Stable fetch instance — prevents ChatKit re-initialization on every render
  const chatkitFetch = useMemo(() => createChatKitFetch(studentId), [studentId]);

  // Initialize ChatKit with the backend protocol endpoint and custom fetch
  const { control, setComposerValue } = useChatKit({
    api: {
      url: `${apiBaseUrl}/chatkit`,
      domainKey: chatkitDomainKey,
      fetch: chatkitFetch,
    },
    onError: (event) => {
      setError(event?.error?.message || 'An error occurred. Please try again.');
    },
  });

  // Auto-dismiss error after 10 seconds
  useEffect(() => {
    if (!error) return;
    const timer = setTimeout(() => setError(null), 10000);
    return () => clearTimeout(timer);
  }, [error]);

  // Listen for text selection to show the "Ask AI" button
  useEffect(() => {
    const handleMouseUp = () => {
      const sel = window.getSelection();
      const text = sel?.toString().trim();
      
      if (text && text.length > 10) {
        const range = sel?.getRangeAt(0);
        const rect = range?.getBoundingClientRect();
        if (rect) {
          setSelection({
            text,
            x: rect.left,
            y: rect.top - 40,
          });
        }
      } else {
        setSelection(null);
      }
    };

    document.addEventListener('mouseup', handleMouseUp);
    return () => document.removeEventListener('mouseup', handleMouseUp);
  }, []);

  const askAboutSelection = useCallback(() => {
    if (!selection) return;
    
    setIsOpen(true);
    setComposerValue({ text: `Tell me more about this: "${selection.text}"` });
    setSelection(null);
  }, [selection, setComposerValue]);

  return (
    <>
      {selection && (
        <button
          className={styles.selectionButton}
          style={{ top: Math.min(selection.y, window.innerHeight - 60), left: Math.min(selection.x, window.innerWidth - 120) }}
          onClick={askAboutSelection}
          aria-label="Ask AI about selected text"
        >
          ✨ Ask AI
        </button>
      )}
      
      <div className={styles.widgetContainer}>
        <button 
          className={styles.toggleButton}
          onClick={() => setIsOpen(!isOpen)}
          aria-label={isOpen ? 'Close Chat Assistant' : 'Open Chat Assistant'}
        >
          {isOpen ? '×' : '💬'}
        </button>
        
        {/* Always keep ChatKit mounted to preserve conversation state.
            Use CSS visibility to show/hide instead of conditional rendering. */}
        <div className={styles.chatWindow} data-visible={isOpen} role="dialog" aria-modal="true" aria-label="Chat with Physical AI Assistant">
          <div className={styles.chatHeader}>
            <span>Physical AI Assistant</span>
          </div>
          <div className={styles.chatBody}>
            {error && (
              <div className={styles.errorBanner}>
                <span>{error}</span>
                <button className={styles.errorDismiss} onClick={() => setError(null)} aria-label="Dismiss error">&times;</button>
              </div>
            )}
            <ChatKit control={control} />
          </div>
        </div>
      </div>
    </>
  );
};

export default ChatKitWidget;
