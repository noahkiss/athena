import type { APIRoute } from 'astro';

const GARDENER_URL =
  process.env.GARDENER_URL ||
  import.meta.env.GARDENER_URL ||
  'http://localhost:8000';

export const POST: APIRoute = async ({ request }) => {
  try {
    const formData = await request.formData();
    const content = formData.get('content')?.toString() || '';

    if (!content.trim()) {
      return new Response(
        '<p class="text-gray-500">Enter some content to get suggestions.</p>',
        { status: 200, headers: { 'Content-Type': 'text/html' } }
      );
    }

    const response = await fetch(`${GARDENER_URL}/api/refine`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ content }),
    });

    if (!response.ok) {
      throw new Error(`Gardener responded with ${response.status}`);
    }

    const html = await response.text();
    return new Response(html, {
      status: 200,
      headers: { 'Content-Type': 'text/html' },
    });
  } catch (error) {
    console.error('Refine error:', error);
    return new Response(
      '<p class="text-yellow-500">Could not get suggestions. Is Gardener running?</p>',
      { status: 200, headers: { 'Content-Type': 'text/html' } }
    );
  }
};
