import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [react()],
  server: {
    port: 5173,
    host: true,    // required when running inside Docker
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
