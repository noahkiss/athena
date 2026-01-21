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

export const GET: APIRoute = async ({ params }) => {
  const path = params.path || '';

  try {
    const response = await fetch(`${GARDENER_URL}/api/browse/${path}`, {
      headers: authHeaders,
    });

    if (!response.ok) {
      throw new Error(`Gardener responded with ${response.status}`);
    }

    const data = await response.json();
    return new Response(JSON.stringify(data), {
      status: 200,
      headers: { 'Content-Type': 'application/json' },
    });
  } catch (error) {
    console.error('Browse error:', error);
    return new Response(
      JSON.stringify({ error: 'Could not fetch directory listing' }),
      { status: 500, headers: { 'Content-Type': 'application/json' } }
    );
  }
};
