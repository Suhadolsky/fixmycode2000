import type { APIRoute } from 'astro';
import errorsDb from '../data/errors_db.json';

export const GET: APIRoute = async () => {
  const searchIndex = (errorsDb as any[]).map((item) => {
    const bSlug = item.brand_slug || item.brand.toLowerCase().replace(/[^a-z0-9]+/g, '-');
    return {
      b: item.brand,
      m: item.model_series,
      c: item.error_code,
      s: item.short_symptom,
      p: item.oem_part_number,
      u: `/${bSlug}/${item.slug}/`,
      e: item.equipment_type,
      n: item.primary_part_name,
    };
  });

  return new Response(JSON.stringify(searchIndex), {
    headers: {
      'Content-Type': 'application/json; charset=utf-8',
      'Cache-Control': 'public, max-age=86400, s-maxage=604800, immutable',
    },
  });
};
