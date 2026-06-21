import { describe, it, expect, beforeEach, vi } from 'vitest';

describe('context-extractor', () => {
  beforeEach(() => {
    document.title = 'Chapter 1 | Physical AI & Humanoid Robotics';
    document.head.innerHTML = '<title>Chapter 1 | Physical AI & Humanoid Robotics</title>';
    Object.defineProperty(window, 'location', {
      value: { href: 'https://example.com/docs/module1/chapter1' },
      writable: true,
    });
  });

  it('extracts url from window.location', async () => {
    const { getPageContext } = await import('../../utils/context-extractor');
    const ctx = getPageContext();
    expect(ctx.url).toBe('https://example.com/docs/module1/chapter1');
  });

  it('strips site title suffix from document.title dynamically', async () => {
    const { getPageContext } = await import('../../utils/context-extractor');
    const ctx = getPageContext();
    expect(ctx.title).toBe('Chapter 1');
  });

  it('returns full title when no separator present', async () => {
    document.title = 'Standalone Page';
    const { getPageContext } = await import('../../utils/context-extractor');
    const ctx = getPageContext();
    expect(ctx.title).toBe('Standalone Page');
  });

  it('handles title with multiple separators correctly', async () => {
    document.title = 'Chapter | Sub | Site Name';
    const { getPageContext } = await import('../../utils/context-extractor');
    const ctx = getPageContext();
    expect(ctx.title).toBe('Chapter | Sub');
  });

  it('returns up to 5 headings from h1 and h2 elements', async () => {
    document.body.innerHTML = `
      <h1>Main Title</h1>
      <h2>Section One</h2>
      <h2>Section Two</h2>
      <h3>Subsection (ignored)</h3>
      <h2>Section Three</h2>
    `;
    const { getPageContext } = await import('../../utils/context-extractor');
    const ctx = getPageContext();
    expect(ctx.headings).toEqual(['Main Title', 'Section One', 'Section Two', 'Section Three']);
    expect(ctx.headings.length).toBeLessThanOrEqual(5);
  });

  it('returns empty headings when no h1/h2 present', async () => {
    document.body.innerHTML = '<p>No headings here</p>';
    const { getPageContext } = await import('../../utils/context-extractor');
    const ctx = getPageContext();
    expect(ctx.headings).toEqual([]);
  });

  it('handles server-side rendering (no window)', async () => {
    const win = globalThis.window;
    (globalThis as any).window = undefined;
    const { getPageContext } = await import('../../utils/context-extractor');
    const ctx = getPageContext();
    expect(ctx.url).toBe('');
    expect(ctx.title).toBe('');
    expect(ctx.headings).toEqual([]);
    (globalThis as any).window = win;
  });
});
