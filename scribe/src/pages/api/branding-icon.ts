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
    const iconFile = formData.get('icon');

    if (!(iconFile instanceof File)) {
      return new Response('<p class="text-warning">Please choose an icon file.</p>', {
        status: 400,
        headers: { 'Content-Type': 'text/html' },
      });
    }

    const uploadData = new FormData();
    uploadData.set('file', iconFile);

    const response = await fetch(`${GARDENER_URL}/api/branding/icon`, {
      method: 'POST',
      headers: authHeaders,
      body: uploadData,
    });

    if (!response.ok) {
      const detail = await response.text();
      throw new Error(detail || `Gardener responded with ${response.status}`);
    }

    return new Response('<p class="text-success">Icon updated. Refresh to apply.</p>', {
      status: 200,
      headers: { 'Content-Type': 'text/html' },
    });
  } catch (error) {
    console.error('Icon upload error:', error);
    return new Response(
      '<p class="text-danger">Failed to upload icon. Is Gardener running?</p>',
      { status: 500, headers: { 'Content-Type': 'text/html' } }
    );
  }
};
