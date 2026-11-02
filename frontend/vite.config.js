import { defineConfig } from 'vite';

// En desarrollo, /api se redirige a Flask para no tener que configurar CORS.
export default defineConfig({
  server: {
    port: 5173,
    proxy: {
      '/api': `http://127.0.0.1:${process.env.GOTUTOR_API_PORT || 8000}`
    }
  }
});
