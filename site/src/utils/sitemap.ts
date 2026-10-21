import errorsDb from '../data/errors_db.json';

export const SITE_URL = 'https://gettinytool.com';

export function generateSitemapXml(): string {
  const today = new Date().toISOString().split('T')[0];

  const brandSlugs = new Set<string>();
  errorsDb.forEach((item: any) => {
    const bSlug = item.brand_slug || item.brand.toLowerCase().replace(/[^a-z0-9]+/g, '-');
    brandSlugs.add(bSlug);
  });

  let xml = `<?xml version="1.0" encoding="UTF-8"?>\n`;
  xml += `<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n`;

  // 1. Homepage
  xml += `  <url>\n`;
  xml += `    <loc>${SITE_URL}/</loc>\n`;
  xml += `    <lastmod>${today}</lastmod>\n`;
  xml += `    <changefreq>daily</changefreq>\n`;
  xml += `    <priority>1.0</priority>\n`;
  xml += `  </url>\n`;

  // 2. Brand hubs
  for (const b of Array.from(brandSlugs).sort()) {
    xml += `  <url>\n`;
    xml += `    <loc>${SITE_URL}/${b}/</loc>\n`;
    xml += `    <lastmod>${today}</lastmod>\n`;
    xml += `    <changefreq>weekly</changefreq>\n`;
    xml += `    <priority>0.8</priority>\n`;
    xml += `  </url>\n`;
  }

  // 3. Error code pages
  for (const item of errorsDb as any[]) {
    const bSlug = item.brand_slug || item.brand.toLowerCase().replace(/[^a-z0-9]+/g, '-');
    xml += `  <url>\n`;
    xml += `    <loc>${SITE_URL}/${bSlug}/${item.slug}/</loc>\n`;
    xml += `    <lastmod>${today}</lastmod>\n`;
    xml += `    <changefreq>monthly</changefreq>\n`;
    xml += `    <priority>0.7</priority>\n`;
    xml += `  </url>\n`;
  }

  xml += `</urlset>\n`;
  return xml;
}
