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
    const question = formData.get('content')?.toString() || '';

    if (!question.trim()) {
      return new Response(
        '<p class="text-gray-500">Enter a question to explore your notes.</p>',
        { status: 200, headers: { 'Content-Type': 'text/html' } }
      );
    }

    const response = await fetch(`${GARDENER_URL}/api/ask`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json', ...authHeaders },
      body: JSON.stringify({ question }),
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
    console.error('Ask error:', error);
    return new Response(
      '<p class="text-yellow-500">Could not explore your notes. Is Gardener running?</p>',
      { status: 200, headers: { 'Content-Type': 'text/html' } }
    );
  }
};
