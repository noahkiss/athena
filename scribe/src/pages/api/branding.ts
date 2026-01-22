import type { APIRoute } from 'astro';

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
    const appName = formData.get('app_name');
    const theme = formData.get('theme');
    const payload: Record<string, string> = {};

    if (appName !== null) payload.app_name = appName.toString();
    if (theme !== null) payload.theme = theme.toString();

    const response = await fetch(`${GARDENER_URL}/api/branding`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json', ...authHeaders },
      body: JSON.stringify(payload),
    });

    if (!response.ok) {
      const detail = await response.text();
      throw new Error(detail || `Gardener responded with ${response.status}`);
    }

    const settings = await response.json();
    const safeName = escapeHtml(settings.app_name || 'Scribe');
    return new Response(`<p class="text-success">Saved branding for ${safeName}.</p>`, {
      status: 200,
      headers: { 'Content-Type': 'text/html' },
    });
  } catch (error) {
    console.error('Branding update error:', error);
    return new Response(
      '<p class="text-danger">Failed to update branding. Is Gardener running?</p>',
      { status: 500, headers: { 'Content-Type': 'text/html' } }
    );
  }
};
