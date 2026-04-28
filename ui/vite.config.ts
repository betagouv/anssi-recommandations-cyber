import { defineConfig } from 'vite';
import { svelte } from '@sveltejs/vite-plugin-svelte';
import { resolve } from 'path';

export default defineConfig({
  plugins: [svelte()],
  build: {
    rollupOptions: {
      input: {
        main: resolve(__dirname, 'index.html'),
        cgu: resolve(__dirname, 'cgu.html'),
        faq: resolve(__dirname, 'faq.html'),
        'politique-confidentialite': resolve(
          __dirname,
          'politique-confidentialite.html'
        ),
      },
    },
  },
});
