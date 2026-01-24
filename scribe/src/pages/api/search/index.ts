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
  try {
    const response = await fetch(`${GARDENER_URL}/api/search/index`, {
      headers: authHeaders,
    });

    if (!response.ok) {
      throw new Error(`Gardener responded with ${response.status}`);
    }

    const data = await response.json();
    return new Response(JSON.stringify(data), {
      status: 200,
      headers: {
        'Content-Type': 'application/json',
        // Cache for 5 minutes to reduce load
        'Cache-Control': 'public, max-age=300',
      },
    });
  } catch (error) {
    console.error('Search index error:', error);
    return new Response(
      JSON.stringify({ error: 'Could not fetch search index', notes: [], total: 0 }),
      { status: 500, headers: { 'Content-Type': 'application/json' } }
    );
  }
};
