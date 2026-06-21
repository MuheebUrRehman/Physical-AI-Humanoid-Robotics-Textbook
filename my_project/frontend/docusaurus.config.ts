import {themes as prismThemes} from 'prism-react-renderer';
import type {Config} from '@docusaurus/types';
import type * as Preset from '@docusaurus/preset-classic';

// This runs in Node.js - Don't use client-side code here (browser APIs, JSX...)

const config: Config = {
  title: 'Physical AI & Humanoid Robotics',
  tagline: 'A Comprehensive Guide to Embodied Intelligence',
  favicon: 'img/favicon.ico',

  future: {
    v4: true,
  },

  url: 'https://physical-ai-humanoid-robotics-textb-three-alpha.vercel.app',
  baseUrl: '/',

  organizationName: 'panaversity',
  projectName: 'physical-ai-humanoid-robotics-textbook',

  onBrokenLinks: 'throw',

  i18n: {
    defaultLocale: 'en',
    locales: ['en'],
  },
  stylesheets: [
    {
      href: 'https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap',
      type: 'text/css',
    },
  ],
  customFields: {
    apiBaseUrl: process.env.API_BASE_URL || 'http://localhost:8000',
    chatkitDomainKey: process.env.CHATKIT_DOMAIN_KEY || 'physical-ai-textbook-local',
  },

  presets: [
    [
      'classic',
      {
        docs: {
          sidebarPath: './sidebars.ts',
          editUrl:
            'https://github.com/panaversity/physical-ai-humanoid-robotics-textbook/tree/main/my_project/frontend',
        },
        theme: {
          customCss: './src/css/custom.css',
        },
      } satisfies Preset.Options,
    ],
  ],

  plugins: [
    function (context, options) {
      return {
        name: 'raw-loader-plugin',
        configureWebpack(config, isServer) {
          return {
            module: {
              rules: [
                {
                  test: /\.py$/,
                  use: require.resolve('raw-loader'),
                },
                {
                  test: /\.cs$/,
                  use: require.resolve('raw-loader'),
                },
                {
                  test: /\.world$/,
                  use: require.resolve('raw-loader'),
                },
              ],
            },
          };
        },
      };
    },
    // Plugin to add dev server proxy for API calls (Docusaurus native proxy format)
    function () {
      return {
        name: 'dev-server-proxy',
        proxy: {
          '/api/chatkit': {
            target: process.env.API_BASE_URL || 'http://localhost:8000',
            changeOrigin: true,
          },
          '/chatkit': {
            target: process.env.API_BASE_URL || 'http://localhost:8000',
            changeOrigin: true,
          },
        },
      };
    },
  ],

  scripts: [
    {
      src: 'https://cdn.platform.openai.com/deployments/chatkit/chatkit.js',
      async: true,
    },
  ],

  themeConfig: {
    // Replace with your project's social card
    image: 'img/docusaurus-social-card.jpg',
    colorMode: {
      defaultMode: 'dark',
      respectPrefersColorScheme: true,
    },
    navbar: {
      title: 'Physical AI Robotics',
      logo: {
        alt: 'Physical AI Robotics Logo',
        src: 'img/logo.svg',
      },
      items: [
        {
          type: 'docSidebar',
          sidebarId: 'tutorialSidebar',
          position: 'left',
          label: 'Tutorial',
        },
        {
          href: 'https://github.com/panaversity/physical-ai-humanoid-robotics-textbook',
          label: 'GitHub',
          position: 'right',
        },
      ],
    },
    footer: {
      style: 'dark',
      links: [
        {
          title: 'Docs',
          items: [
            { label: 'Getting Started', to: '/docs/module1/chapter1' },
          ],
        },
        {
          title: 'Community',
          items: [
            { label: 'GitHub', href: 'https://github.com/panaversity/physical-ai-humanoid-robotics-textbook' },
          ],
        },
      ],
      copyright: `Copyright © ${new Date().getFullYear()} Physical AI & Humanoid Robotics`,
    },
  prism: {
      theme: prismThemes.github,
      darkTheme: prismThemes.dracula,
    },
  } satisfies Preset.ThemeConfig,
};

export default config;
