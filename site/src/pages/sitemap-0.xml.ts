import type { APIRoute } from 'astro';
import { generateSitemapXml } from '../utils/sitemap';

export const GET: APIRoute = async () => {
  return new Response(generateSitemapXml(), {
    headers: {
      'Content-Type': 'application/xml; charset=utf-8',
    },
  });
};
