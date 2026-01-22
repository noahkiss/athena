import { defineConfig } from 'astro/config';
import tailwind from '@astrojs/tailwind';
import node from '@astrojs/node';
import icon from 'astro-icon';

export default defineConfig({
  output: 'server',
  adapter: node({
    mode: 'standalone'
  }),
  integrations: [
    tailwind(),
    icon({
      include: {
        solar: ['*'], // Solar icons (primary)
        'material-symbols': ['*'], // Material Symbols (fallback)
      },
    }),
  ],
  server: {
    port: 3000,
    host: true
  }
});
