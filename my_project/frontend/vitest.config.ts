import { defineConfig } from 'vitest/config';
import path from 'path';

export default defineConfig({
  esbuild: {
    jsx: 'automatic',
    jsxImportSource: 'react',
  },
  test: {
    environment: 'jsdom',
    setupFiles: ['./src/test-setup.ts'],
    globals: true,
    include: ['src/**/*.test.{ts,tsx}'],
    css: { modules: { classNameStrategy: 'non-scoped' } },
  },
  resolve: {
    alias: {
      '@site': path.resolve(__dirname),
      '@theme/Layout': path.resolve(__dirname, 'src/__mocks__/docusaurus/Layout.tsx'),
      '@docusaurus/Link': path.resolve(__dirname, 'src/__mocks__/docusaurus/Link.tsx'),
      '@docusaurus/useDocusaurusContext': path.resolve(__dirname, 'src/__mocks__/docusaurus/useDocusaurusContext.ts'),
    },
  },
});
