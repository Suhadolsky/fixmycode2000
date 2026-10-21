import type { APIRoute } from 'astro';

export const GET: APIRoute = async () => {
  return new Response('fixmycode2026abc1', {
    headers: {
      'Content-Type': 'text/plain; charset=utf-8',
    },
  });
};
