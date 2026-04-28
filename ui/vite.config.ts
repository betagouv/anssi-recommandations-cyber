import { defineConfig } from 'vite';
import { svelte } from '@sveltejs/vite-plugin-svelte';
import { resolve } from 'path';

const pages = {
  cgu: 'cgu.html',
  faq: 'faq.html',
  'politique-confidentialite': 'politique-confidentialite.html',
};

const input = Object.fromEntries(
  Object.entries(pages).map(([name, path]) => [
    name,
    resolve(`${__dirname}/pages`, path),
  ])
);

console.log(input);

export default defineConfig({
  plugins: [svelte()],
  build: {
    rollupOptions: {
      input: {
        ...input,
        main: resolve(`${__dirname}`, 'index.html'),
      },
    },
  },
});
