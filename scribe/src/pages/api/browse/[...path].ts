import type { APIRoute } from 'astro';

const GARDENER_URL =
  process.env.GARDENER_URL ||
  import.meta.env.GARDENER_URL ||
  'http://localhost:8000';

export const GET: APIRoute = async ({ params }) => {
  const path = params.path || '';

  try {
    const response = await fetch(`${GARDENER_URL}/api/browse/${path}`);

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
