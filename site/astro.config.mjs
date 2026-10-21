// @ts-check
import { defineConfig } from 'astro/config';
import tailwind from '@astrojs/tailwind';

// Cloudflare Pages build trigger
export default defineConfig({
  site: 'https://gettinytool.com',
  integrations: [
    tailwind(),
  ],
});

