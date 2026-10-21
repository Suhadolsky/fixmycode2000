// Cloudflare Pages Middleware for Legacy URL Cleanup (410 Gone)
interface Env {}

export const onRequest: PagesFunction<Env> = async (context) => {
  const url = new URL(context.request.url);
  const pathname = url.pathname;

  // TASK 1: Return HTTP 410 Gone with minimal plain-text for legacy /tools/* and /about URLs
  if (
    pathname === '/tools' ||
    pathname === '/tools/' ||
    pathname.startsWith('/tools/') ||
    pathname === '/about' ||
    pathname === '/about/'
  ) {
    return new Response('410 Gone\n\nThis resource has been permanently removed.', {
      status: 410,
      statusText: 'Gone',
      headers: {
        'Content-Type': 'text/plain; charset=utf-8',
        'Cache-Control': 'public, max-age=604800, s-maxage=604800, immutable',
        'X-Robots-Tag': 'noindex, nofollow',
      },
    });
  }

  return context.next();
};
