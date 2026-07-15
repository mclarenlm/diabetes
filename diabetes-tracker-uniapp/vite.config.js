import { defineConfig } from 'vite'
import uni from '@dcloudio/vite-plugin-uni'

export default defineConfig({
  plugins: [uni()],
  server: {
    proxy: {
      '/api': 'http://localhost:5000',
      '/manifest.json': 'http://localhost:5000',
      '/sw.js': 'http://localhost:5000'
    }
  }
})
