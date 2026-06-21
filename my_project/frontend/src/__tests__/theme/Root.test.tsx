import { describe, it, expect } from 'vitest';
import { render, screen } from '@testing-library/react';
import React from 'react';

vi.mock('../../components/ChatKitWidget', () => ({
  default: () => <div data-testid="chatkit-widget">Widget</div>,
}));

describe('Root wrapper', () => {
  it('renders children', async () => {
    const { default: Root } = await import('../../theme/Root');
    render(
      <Root>
        <div data-testid="child">Hello</div>
      </Root>
    );
    expect(screen.getByTestId('child')).toBeInTheDocument();
    expect(screen.getByText('Hello')).toBeInTheDocument();
  });

  it('renders ChatKitWidget alongside children', async () => {
    const { default: Root } = await import('../../theme/Root');
    render(
      <Root>
        <div>Content</div>
      </Root>
    );
    expect(screen.getByTestId('chatkit-widget')).toBeInTheDocument();
  });
});
