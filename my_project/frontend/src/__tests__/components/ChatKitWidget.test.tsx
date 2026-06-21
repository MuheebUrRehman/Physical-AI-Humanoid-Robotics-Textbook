import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, fireEvent, act } from '@testing-library/react';

vi.mock('@openai/chatkit-react', () => ({
  useChatKit: () => ({
    control: {},
    setComposerValue: vi.fn(),
  }),
  ChatKit: ({ control }: any) => <div data-testid="chatkit-chat">Chat</div>,
}));

vi.mock('@docusaurus/useDocusaurusContext', () => ({
  default: () => ({
    siteConfig: {
      customFields: {
        apiBaseUrl: 'http://localhost:8000',
        chatkitDomainKey: 'physical-ai-textbook-local',
      },
    },
  }),
}));

vi.mock('../../utils/chatkit-fetch', () => ({
  createChatKitFetch: (id: string) => vi.fn(),
}));

describe('ChatKitWidget', () => {
  beforeEach(() => {
    localStorage.clear();
    document.body.innerHTML = '';
  });

  it('renders the toggle button', async () => {
    const { default: ChatKitWidget } = await import('../../components/ChatKitWidget');
    const { container } = render(<ChatKitWidget />);
    const toggle = container.querySelector('button[aria-label="Open Chat Assistant"]');
    expect(toggle).toBeInTheDocument();
  });

  it('opens chat window when toggle is clicked', async () => {
    const { default: ChatKitWidget } = await import('../../components/ChatKitWidget');
    const { container } = render(<ChatKitWidget />);
    const toggle = container.querySelector('button[aria-label="Open Chat Assistant"]')!;
    fireEvent.click(toggle);
    const chatWindow = container.querySelector('[data-visible="true"]');
    expect(chatWindow).toBeInTheDocument();
  });

  it('closes chat window on second toggle click', async () => {
    const { default: ChatKitWidget } = await import('../../components/ChatKitWidget');
    const { container } = render(<ChatKitWidget />);
    const toggle = container.querySelector('button[aria-label="Open Chat Assistant"]')!;
    fireEvent.click(toggle);
    fireEvent.click(toggle);
    const chatWindow = container.querySelector('[data-visible="false"]');
    expect(chatWindow).toBeInTheDocument();
  });

  it('generates a persistent student ID from localStorage', async () => {
    localStorage.setItem('chatkit_student_id', 'persisted-id-123');
    const { default: ChatKitWidget } = await import('../../components/ChatKitWidget');
    render(<ChatKitWidget />);
    expect(localStorage.getItem('chatkit_student_id')).toBe('persisted-id-123');
  });

  it('renders ChatKit component inside chat body', async () => {
    const { default: ChatKitWidget } = await import('../../components/ChatKitWidget');
    const { container } = render(<ChatKitWidget />);
    const toggle = container.querySelector('button[aria-label="Open Chat Assistant"]')!;
    fireEvent.click(toggle);
    expect(screen.getByTestId('chatkit-chat')).toBeInTheDocument();
  });
});
