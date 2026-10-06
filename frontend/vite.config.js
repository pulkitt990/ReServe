import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// https://vitejs.dev/config/
const backendTarget = process.env.BACKEND_PROXY_URL || 'http://backend:8000';

export default defineConfig({
  plugins: [react()],
  server: {
    host: true,
    port: 5173,
    proxy: {
      '/health': {
        target: backendTarget,
        changeOrigin: true,
      },
      '/api': {
        target: backendTarget,
        changeOrigin: true,
      }
    }
  }
})
