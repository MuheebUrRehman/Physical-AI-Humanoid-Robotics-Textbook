import { describe, it, expect, beforeEach, vi } from 'vitest';

describe('chatkit-fetch', () => {
  beforeEach(() => {
    document.title = 'Test Page | Physical AI & Humanoid Robotics';
    document.body.innerHTML = '<h1>Test</h1>';
    Object.defineProperty(window, 'location', {
      value: { href: 'https://example.com/test' },
      writable: true,
    });
  });

  it('injects pageContext into threads.create requests', async () => {
    const { createChatKitFetch } = await import('../../utils/chatkit-fetch');
    const fetcher = createChatKitFetch('student-1');

    const mockFetch = vi.fn().mockResolvedValue(new Response('ok'));
    globalThis.fetch = mockFetch;

    const body = JSON.stringify({
      type: 'threads.create',
      params: { input: { content: [{ text: 'hello' }] } },
    });

    await fetcher('http://localhost/chatkit', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' } as any,
      body,
    });

    const calledBody = JSON.parse(mockFetch.mock.calls[0][1].body);
    expect(calledBody.params.input.metadata.pageContext).toBeDefined();
    expect(calledBody.params.input.metadata.pageContext.url).toBe('https://example.com/test');
  });

  it('injects pageContext into threads.addUserMessage requests', async () => {
    const { createChatKitFetch } = await import('../../utils/chatkit-fetch');
    const fetcher = createChatKitFetch('student-2');

    const mockFetch = vi.fn().mockResolvedValue(new Response('ok'));
    globalThis.fetch = mockFetch;

    const body = JSON.stringify({
      type: 'threads.addUserMessage',
      params: { input: { content: [{ text: 'tell me more' }] } },
    });

    await fetcher('http://localhost/chatkit', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' } as any,
      body,
    });

    const calledBody = JSON.parse(mockFetch.mock.calls[0][1].body);
    expect(calledBody.params.input.metadata.pageContext).toBeDefined();
  });

  it('injects pageContext into threads.run requests', async () => {
    const { createChatKitFetch } = await import('../../utils/chatkit-fetch');
    const fetcher = createChatKitFetch('student-3');

    const mockFetch = vi.fn().mockResolvedValue(new Response('ok'));
    globalThis.fetch = mockFetch;

    const body = JSON.stringify({
      type: 'threads.run',
      params: { input: { content: [{ text: 'run it' }] } },
    });

    await fetcher('http://localhost/chatkit', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' } as any,
      body,
    });

    const calledBody = JSON.parse(mockFetch.mock.calls[0][1].body);
    expect(calledBody.params.input.metadata.pageContext).toBeDefined();
  });

  it('sets X-User-ID header from studentId', async () => {
    const { createChatKitFetch } = await import('../../utils/chatkit-fetch');
    const fetcher = createChatKitFetch('student-007');

    const mockFetch = vi.fn().mockResolvedValue(new Response('ok'));
    globalThis.fetch = mockFetch;

    await fetcher('http://localhost/chatkit', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' } as any,
      body: JSON.stringify({ type: 'threads.create', params: {} }),
    });

    const headers = mockFetch.mock.calls[0][1].headers as Headers;
    expect(headers.get('X-User-ID')).toBe('student-007');
  });

  it('does not modify non-message request types', async () => {
    const { createChatKitFetch } = await import('../../utils/chatkit-fetch');
    const fetcher = createChatKitFetch('student-1');

    const mockFetch = vi.fn().mockResolvedValue(new Response('ok'));
    globalThis.fetch = mockFetch;

    const body = JSON.stringify({ type: 'threads.list', params: {} });

    await fetcher('http://localhost/chatkit', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' } as any,
      body,
    });

    const calledBody = JSON.parse(mockFetch.mock.calls[0][1].body);
    expect(calledBody.params?.input?.metadata?.pageContext).toBeUndefined();
  });
});
