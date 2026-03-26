import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import tailwindcss from '@tailwindcss/vite'

export default defineConfig({
  plugins: [react(), tailwindcss()],
  server: {
    proxy: {
      '/api': process.env.VERCEL === '1' 
        ? 'https://your-backend-url.vercel.app'
        : 'http://localhost:8005'
    }
  }
})