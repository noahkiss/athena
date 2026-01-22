import type { APIRoute } from 'astro';

const GARDENER_URL =
  process.env.GARDENER_URL ||
  import.meta.env.GARDENER_URL ||
  'http://localhost:8000';
const AUTH_TOKEN =
  process.env.ATHENA_AUTH_TOKEN ||
  import.meta.env.ATHENA_AUTH_TOKEN ||
  '';
const authHeaders = AUTH_TOKEN
  ? { Authorization: `Bearer ${AUTH_TOKEN}`, 'X-Auth-Token': AUTH_TOKEN }
  : {};

const allowed = new Set([
  'favicon-16',
  'favicon-32',
  'favicon-48',
  'apple-touch-icon-120',
  'apple-touch-icon-152',
  'apple-touch-icon-167',
  'apple-touch-icon-180',
  'pwa-192',
  'pwa-512',
]);

export const GET: APIRoute = async ({ params }) => {
  const name = params.name || '';
  if (!allowed.has(name)) {
    return new Response('Not found', { status: 404 });
  }

  const response = await fetch(`${GARDENER_URL}/api/branding/icon/${name}.png`, {
    headers: authHeaders,
  });

  if (!response.ok || !response.body) {
    return new Response('Not found', { status: response.status });
  }

  return new Response(response.body, {
    status: 200,
    headers: {
      'Content-Type': response.headers.get('content-type') || 'image/png',
      'Cache-Control': 'public, max-age=3600',
    },
  });
};
