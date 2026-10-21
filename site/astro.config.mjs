// @ts-check
import { defineConfig } from 'astro/config';
import tailwind from '@astrojs/tailwind';
import sitemap from '@astrojs/sitemap';

// Cloudflare Pages build trigger
export default defineConfig({
  site: 'https://gettinytool.com',
  integrations: [
    tailwind(),
    sitemap(),
  ],
});
