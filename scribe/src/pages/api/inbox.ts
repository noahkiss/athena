import type { APIRoute } from 'astro';

const GARDNER_URL = import.meta.env.GARDNER_URL || 'http://localhost:8000';

export const POST: APIRoute = async ({ request }) => {
  try {
    const formData = await request.formData();
    const content = formData.get('content')?.toString() || '';

    if (!content.trim()) {
      return new Response(
        '<p class="text-yellow-500">Please enter some content.</p>',
        { status: 400, headers: { 'Content-Type': 'text/html' } }
      );
    }

    const response = await fetch(`${GARDNER_URL}/api/inbox`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ content }),
    });

    if (!response.ok) {
      throw new Error(`Gardner responded with ${response.status}`);
    }

    const data = await response.json();

    return new Response(
      `<p class="text-green-500">Saved to inbox: ${data.filename}</p>`,
      { status: 200, headers: { 'Content-Type': 'text/html' } }
    );
  } catch (error) {
    console.error('Inbox submission error:', error);
    return new Response(
      '<p class="text-red-500">Failed to save note. Is Gardner running?</p>',
      { status: 500, headers: { 'Content-Type': 'text/html' } }
    );
  }
};
