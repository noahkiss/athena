import type { APIRoute } from 'astro';

/** Escape HTML special characters to prevent XSS. */
function escapeHtml(text: string): string {
  return text
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
    .replace(/'/g, '&#039;');
}

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

    const response = await fetch(`${GARDENER_URL}/api/inbox`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json', ...authHeaders },
      body: JSON.stringify({ content }),
    });

    if (!response.ok) {
      throw new Error(`Gardener responded with ${response.status}`);
    }

    const data = await response.json();

    return new Response(
      `<p class="text-green-500">Saved to inbox: ${escapeHtml(data.filename)}</p>`,
      { status: 200, headers: { 'Content-Type': 'text/html' } }
    );
  } catch (error) {
    console.error('Inbox submission error:', error);
    return new Response(
      '<p class="text-red-500">Failed to save note. Is Gardener running?</p>',
      { status: 500, headers: { 'Content-Type': 'text/html' } }
    );
  }
};
