import React, { useState, useRef, useEffect } from 'react';
import clsx from 'clsx';
import useDocusaurusContext from '@docusaurus/useDocusaurusContext';
import styles from './FloatingChat.module.css';

interface Message {
  id: string;
  content: string;
  sender: 'user' | 'ai';
  timestamp: Date;
}

const FloatingChat: React.FC = () => {
  const {siteConfig} = useDocusaurusContext();
  const configuredApiBaseUrl = String(siteConfig.customFields?.apiBaseUrl ?? 'http://localhost:8000');
  const apiBaseUrl = configuredApiBaseUrl.replace(/\/+$/, '');
  const [isOpen, setIsOpen] = useState(false);
  const [messages, setMessages] = useState<Message[]>([]);
  const [inputValue, setInputValue] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  // Add initial welcome message
  useEffect(() => {
    if (isOpen && messages.length === 0) {
      setTimeout(() => {
        setMessages([
          {
            id: 'welcome',
            content: 'Welcome! Ask me anything about Physical AI & Humanoid Robotics. I\'m here to help you explore the fascinating world of AI and robotics!',
            sender: 'ai',
            timestamp: new Date(),
          }
        ]);
      }, 300);
    }
  }, [isOpen, messages.length]);

  // Scroll to bottom of messages
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  // Auto-resize textarea
  useEffect(() => {
    if (textareaRef.current) {
      textareaRef.current.style.height = 'auto';
      textareaRef.current.style.height = Math.min(textareaRef.current.scrollHeight, 120) + 'px';
    }
  }, [inputValue]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!inputValue.trim() || isLoading) return;

    const userQuery = inputValue;
    try {
      // Add user message
      const userMessage: Message = {
        id: Date.now().toString(),
        content: userQuery,
        sender: 'user',
        timestamp: new Date(),
      };

      setMessages(prev => [...prev, userMessage]);
      setInputValue('');
      setIsLoading(true);
      setError(null);

      // Create a placeholder AI message for streaming
      const aiMessageId = (Date.now() + 1).toString();
      const aiPlaceholder: Message = {
        id: aiMessageId,
        content: '',
        sender: 'ai',
        timestamp: new Date(),
      };
      setMessages(prev => [...prev, aiPlaceholder]);

      // Call backend API
      const response = await fetch(`${apiBaseUrl}/chat`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          query: userQuery,
          user_id: 'user-default', // In a real app, this would be from auth
          session_id: 'session-default',
        }),
      });

      if (!response.ok) {
        throw new Error(`API error: ${response.status} ${response.statusText}`);
      }

      const reader = response.body?.getReader();
      const decoder = new TextDecoder();
      let accumulatedBuffer = '';

      if (!reader) {
        throw new Error('Response body is null');
      }

      while (true) {
        const { done, value } = await reader.read();
        if (done) break;

        accumulatedBuffer += decoder.decode(value, { stream: true });
        
        // Split by the standard SSE double-newline delimiter
        const parts = accumulatedBuffer.split('\n\n');
        
        // Keep the last part in the buffer if it's incomplete
        accumulatedBuffer = parts.pop() || '';

        for (const line of parts) {
          const trimmedLine = line.trim();
          if (trimmedLine.startsWith('data: ')) {
            try {
              const data = JSON.parse(trimmedLine.slice(6));
              
              if (data.type === 'token') {
                accumulatedContent += data.content;
                setMessages(prev => 
                  prev.map(msg => 
                    msg.id === aiMessageId ? { ...msg, content: accumulatedContent } : msg
                  )
                );
              } else if (data.type === 'final') {
                // Final structured data reached
                const finalResponse = data.content;
                setMessages(prev => 
                  prev.map(msg => 
                    msg.id === aiMessageId ? { ...msg, content: finalResponse.answer } : msg
                  )
                );
              } else if (data.type === 'error') {
                setError(data.content);
              }
            } catch (parseErr) {
              console.error('SSE parse error on line:', trimmedLine, parseErr);
            }
          }
        }
      }
    } catch (err) {
      console.error('Error sending message:', err);
      setError(err instanceof Error ? err.message : 'Failed to send message');

      // Add error message to chat if not already showing one
      const errorMessage: Message = {
        id: Date.now().toString(),
        content: 'Sorry, I encountered an error processing your request. Please try again.',
        sender: 'ai',
        timestamp: new Date(),
      };
      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleQuickPrompt = (prompt: string) => {
    setInputValue(prompt);
    // Focus the input field after setting the prompt
    setTimeout(() => {
      if (textareaRef.current) {
        textareaRef.current.focus();
      }
    }, 100);
  };

  const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSubmit(e as any);
    }
  };

  return (
    <div className={styles.floatingChat}>
      {isOpen ? (
        <div className={styles.chatContainer}>
          <div className={styles.chatHeader}>
            <h3>RAG Assistant</h3>
            <button
              className={styles.closeButton}
              onClick={() => setIsOpen(false)}
              aria-label="Close chat"
            >
              ×
            </button>
          </div>

          <div className={styles.messagesContainer}>
            {messages.map((message) => (
              <div
                key={message.id}
                className={clsx(
                  styles.message,
                  message.sender === 'user' ? styles['message-user'] : styles['message-ai']
                )}
              >
                {message.content}
              </div>
            ))}
            {isLoading && (
              <div className={styles.typingIndicator}>
                <div className={styles.typingDot}></div>
                <div className={styles.typingDot}></div>
                <div className={styles.typingDot}></div>
                <span>AI is thinking...</span>
              </div>
            )}
            <div ref={messagesEndRef} />
          </div>

          {/* Quick prompts for first message */}
          {messages.length <= 1 && !isLoading && (
            <div className={styles.quickPrompts}>
              <div className={styles.quickPromptsTitle}>Try asking:</div>
              <div className={styles.quickPromptsContainer}>
                <button
                  onClick={() => handleQuickPrompt('Explain neural networks in robotics')}
                  className={styles.quickPromptBtn}
                >
                  Neural networks in robotics
                </button>
                <button
                  onClick={() => handleQuickPrompt('How do humanoid robots maintain balance?')}
                  className={styles.quickPromptBtn}
                >
                  Balance in humanoid robots
                </button>
                <button
                  onClick={() => handleQuickPrompt('What is physical AI?')}
                  className={styles.quickPromptBtn}
                >
                  Physical AI concepts
                </button>
                <button
                  onClick={() => handleQuickPrompt('Explain reinforcement learning for robots')}
                  className={styles.quickPromptBtn}
                >
                  RL for robots
                </button>
              </div>
            </div>
          )}

          {/* Input area */}
          <div className={styles.inputContainer}>
            {error && (
              <div className={styles.errorContainer}>
                {error}
              </div>
            )}
            <form onSubmit={handleSubmit} className={styles.inputForm}>
              <textarea
                ref={textareaRef}
                value={inputValue}
                onChange={(e) => setInputValue(e.target.value)}
                onKeyDown={handleKeyDown}
                placeholder="Ask about Physical AI, robotics, or humanoid technology..."
                className={styles.inputField}
                disabled={isLoading}
                rows={1}
              />
              <button
                type="submit"
                disabled={!inputValue.trim() || isLoading}
                className={styles.sendButton}
              >
                {isLoading ? 'Sending...' : 'Send'}
              </button>
            </form>
          </div>
        </div>
      ) : (
        <button
          className={styles.floatingButton}
          onClick={() => setIsOpen(true)}
          aria-label="Open chat"
        >
          🤖
        </button>
      )}
    </div>
  );
};

export default FloatingChat;