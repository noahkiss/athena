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

export const POST: APIRoute = async ({ request }) => {
  try {
    const formData = await request.formData();
    const content = formData.get('content')?.toString() || '';

    if (!content.trim()) {
      return new Response(
        '<p class="text-subtle">Enter some content to get suggestions.</p>',
        { status: 200, headers: { 'Content-Type': 'text/html' } }
      );
    }

    const response = await fetch(`${GARDENER_URL}/api/refine`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json', ...authHeaders },
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
      '<p class="text-warning">Could not get suggestions. Is Gardener running?</p>',
      { status: 200, headers: { 'Content-Type': 'text/html' } }
    );
  }
};
