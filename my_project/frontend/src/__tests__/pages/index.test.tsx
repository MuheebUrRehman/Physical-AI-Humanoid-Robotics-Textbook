import { describe, it, expect } from 'vitest';
import { render, screen } from '@testing-library/react';
import React from 'react';

vi.mock('@docusaurus/Link', () => ({
  default: ({ to, children }: any) => <a href={to}>{children}</a>,
}));

vi.mock('@docusaurus/useDocusaurusContext', () => ({
  default: () => ({
    siteConfig: {
      title: 'Physical AI & Humanoid Robotics',
      tagline: 'A Comprehensive Guide to Embodied Intelligence',
      customFields: {},
    },
  }),
}));

vi.mock('@theme/Layout', () => ({
  default: ({ children, title, description }: any) => (
    <div data-testid="layout" data-title={title} data-description={description}>
      {children}
    </div>
  ),
}));

vi.mock('@site/src/components/HomepageFeatures', () => ({
  default: () => <div data-testid="homepage-features">Features</div>,
}));

describe('Home page', () => {
  it('renders the hero title', async () => {
    const { default: Home } = await import('../../pages/index');
    render(<Home />);
    expect(screen.getByText('Physical AI & Humanoid Robotics')).toBeInTheDocument();
  });

  it('renders the hero subtitle', async () => {
    const { default: Home } = await import('../../pages/index');
    render(<Home />);
    expect(screen.getByText('A Comprehensive Guide to Embodied Intelligence')).toBeInTheDocument();
  });

  it('renders Get Started link pointing to glossary', async () => {
    const { default: Home } = await import('../../pages/index');
    render(<Home />);
    const link = screen.getByText('Get Started');
    expect(link).toBeInTheDocument();
    expect(link.getAttribute('href')).toBe('/docs/glossary');
  });

  it('renders HomepageFeatures component', async () => {
    const { default: Home } = await import('../../pages/index');
    render(<Home />);
    expect(screen.getByTestId('homepage-features')).toBeInTheDocument();
  });

  it('passes siteConfig.title as Layout title', async () => {
    const { default: Home } = await import('../../pages/index');
    render(<Home />);
    const layout = screen.getByTestId('layout');
    expect(layout.getAttribute('data-title')).toBe('Physical AI & Humanoid Robotics');
  });
});
