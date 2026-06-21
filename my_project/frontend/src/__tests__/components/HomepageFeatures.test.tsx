import { describe, it, expect } from 'vitest';
import { render, screen } from '@testing-library/react';
import React from 'react';

vi.mock('@docusaurus/Link', () => ({
  default: ({ to, children, ...props }: any) => <a href={to} {...props}>{children}</a>,
}));

describe('HomepageFeatures', () => {
  it('renders the section heading', async () => {
    const { default: HomepageFeatures } = await import('../../components/HomepageFeatures');
    render(<HomepageFeatures />);
    expect(screen.getByText('Course Modules')).toBeInTheDocument();
  });

  it('renders the section subheading', async () => {
    const { default: HomepageFeatures } = await import('../../components/HomepageFeatures');
    render(<HomepageFeatures />);
    expect(screen.getByText(/Explore the complete curriculum/i)).toBeInTheDocument();
  });

  it('renders all 4 module cards', async () => {
    const { default: HomepageFeatures } = await import('../../components/HomepageFeatures');
    const { container } = render(<HomepageFeatures />);
    const cards = container.querySelectorAll('a');
    expect(cards.length).toBe(4);
  });

  it('renders Foundations of Physical AI card', async () => {
    const { default: HomepageFeatures } = await import('../../components/HomepageFeatures');
    render(<HomepageFeatures />);
    expect(screen.getByText('Foundations of Physical AI')).toBeInTheDocument();
  });

  it('renders Explore Module links on each card', async () => {
    const { default: HomepageFeatures } = await import('../../components/HomepageFeatures');
    render(<HomepageFeatures />);
    const links = screen.getAllByText(/Explore Module/);
    expect(links.length).toBe(4);
  });

  it('module badges display module numbers', async () => {
    const { default: HomepageFeatures } = await import('../../components/HomepageFeatures');
    const { container } = render(<HomepageFeatures />);
    const badges = container.querySelectorAll('span');
    const badgeTexts = Array.from(badges).map(b => b.textContent).filter(Boolean);
    expect(badgeTexts).toContain('01');
    expect(badgeTexts).toContain('04');
  });

  it('module cards link to correct doc paths', async () => {
    const { default: HomepageFeatures } = await import('../../components/HomepageFeatures');
    const { container } = render(<HomepageFeatures />);
    const cards = container.querySelectorAll('a');
    const hrefs = Array.from(cards).map(c => c.getAttribute('href'));
    expect(hrefs).toContain('/docs/module1/chapter1');
    expect(hrefs).toContain('/docs/module2/chapter3');
    expect(hrefs).toContain('/docs/module3/chapter5');
    expect(hrefs).toContain('/docs/module4/chapter6');
  });
});
