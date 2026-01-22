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

export const GET: APIRoute = async () => {
  const response = await fetch(`${GARDENER_URL}/api/branding/icon/favicon.ico`, {
    headers: authHeaders,
  });

  if (!response.ok || !response.body) {
    return new Response('Not found', { status: response.status });
  }

  return new Response(response.body, {
    status: 200,
    headers: {
      'Content-Type': response.headers.get('content-type') || 'image/x-icon',
      'Cache-Control': 'public, max-age=3600',
    },
  });
};
