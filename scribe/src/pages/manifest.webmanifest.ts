import type { APIRoute } from 'astro';
import { getTheme } from '../lib/themes';

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

const DEFAULT_APP_NAME = 'Athena Scribe';
const DEFAULT_THEME_COLOR = '#0b1120';

export const GET: APIRoute = async () => {
  let appName = DEFAULT_APP_NAME;
  let iconVersion = 'default';
  let themeId: string | undefined;

  try {
    const response = await fetch(`${GARDENER_URL}/api/branding`, {
      headers: authHeaders,
    });
    if (response.ok) {
      const settings = await response.json();
      appName = settings.app_name || appName;
      iconVersion = settings.icon_version || iconVersion;
      themeId = settings.theme || themeId;
    }
  } catch (error) {
    console.error('Manifest fetch error:', error);
  }

  const shortName = appName.length > 12 ? appName.slice(0, 12) : appName;
  const iconQuery = iconVersion ? `?v=${iconVersion}` : '';
  const theme = getTheme(themeId);
  const themeColor = theme?.themeColor || DEFAULT_THEME_COLOR;

  const manifest = {
    name: appName,
    short_name: shortName,
    description: 'Capture and browse notes in Project Athena.',
    start_url: '/',
    scope: '/',
    display: 'standalone',
    background_color: themeColor,
    theme_color: themeColor,
    icons: [
      {
        src: `/icons/pwa-192.png${iconQuery}`,
        sizes: '192x192',
        type: 'image/png',
      },
      {
        src: `/icons/pwa-512.png${iconQuery}`,
        sizes: '512x512',
        type: 'image/png',
      },
    ],
  };

  return new Response(JSON.stringify(manifest), {
    status: 200,
    headers: {
      'Content-Type': 'application/manifest+json',
      'Cache-Control': 'no-cache',
    },
  });
};
