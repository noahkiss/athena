import type { APIRoute } from 'astro';

const GARDNER_URL =
  process.env.GARDNER_URL ||
  import.meta.env.GARDNER_URL ||
  'http://localhost:8000';

export const GET: APIRoute = async ({ params }) => {
  const path = params.path || '';

  try {
    const response = await fetch(`${GARDNER_URL}/api/browse/${path}`);

    if (!response.ok) {
      throw new Error(`Gardner responded with ${response.status}`);
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
