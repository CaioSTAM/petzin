import { defineConfig } from 'vite';

const proxy = { '/api': process.env.PETZIN_API_URL || 'http://127.0.0.1:8000' };

export default defineConfig({
  server: { proxy },
  preview: { proxy },
});
