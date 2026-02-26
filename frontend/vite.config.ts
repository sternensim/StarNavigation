import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [react()],
  server: {
    port: 5173,
    host: true,    // bind to 0.0.0.0 so the container is reachable from outside
    // HMR websocket host: when accessing from another machine the browser must
    // connect to the Docker host's real IP, not the container-internal 0.0.0.0.
    // Set VITE_HMR_HOST to the host machine's IP or hostname in that case.
    // Unset = Vite uses the page's own hostname (works for localhost access).
    ...(process.env.VITE_HMR_HOST
      ? { hmr: { host: process.env.VITE_HMR_HOST, port: 5173, clientPort: 5173 } }
      : {}),
    proxy: {
      '/api': {
        // VITE_API_TARGET lets docker-compose.dev.yml point at the backend
        // service name; falls back to localhost for native dev (npm run dev).
        target: process.env.VITE_API_TARGET ?? 'http://localhost:8000',
        changeOrigin: true,
      },
    },
  },
})
