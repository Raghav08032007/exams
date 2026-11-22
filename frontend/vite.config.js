import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import { VitePWA } from 'vite-plugin-pwa'
import fs from 'node:fs'
import path from 'node:path'

function framesPlugin() {
  return {
    name: 'frames-plugin',
    buildStart() {
      const srcDir = path.join(__dirname, 'ezgif-2e3765a2f2d84e19-jpg')
      const dstDir = path.join(__dirname, 'public', 'frames')
      if (fs.existsSync(srcDir)) {
        fs.mkdirSync(dstDir, { recursive: true })
        const files = fs.readdirSync(srcDir).filter(f => f.endsWith('.jpg'))
        for (const file of files) {
          fs.copyFileSync(path.join(srcDir, file), path.join(dstDir, file))
        }
      }
    },
    configureServer(server) {
      const srcDir = path.join(__dirname, 'ezgif-2e3765a2f2d84e19-jpg')
      const dstDir = path.join(__dirname, 'public', 'frames')
      if (fs.existsSync(srcDir)) {
        fs.mkdirSync(dstDir, { recursive: true })
        const files = fs.readdirSync(srcDir).filter(f => f.endsWith('.jpg'))
        for (const file of files) {
          const dest = path.join(dstDir, file)
          if (!fs.existsSync(dest)) {
            fs.copyFileSync(path.join(srcDir, file), dest)
          }
        }
      }
      server.middlewares.use('/frames', (req, res, next) => {
        const fileName = req.url.replace(/^\//, '')
        const filePath = path.join(__dirname, 'ezgif-2e3765a2f2d84e19-jpg', fileName)
        if (fs.existsSync(filePath) && fs.statSync(filePath).isFile()) {
          res.setHeader('Content-Type', 'image/jpeg')
          res.setHeader('Cache-Control', 'public, max-age=31536000')
          return fs.createReadStream(filePath).pipe(res)
        }
        next()
      })
    }
  }
}

export default defineConfig({
  plugins: [
    framesPlugin(),
    react(),
    VitePWA({
      registerType: 'autoUpdate',
      includeAssets: ['favicon.ico', 'icons/*.png'],
      manifest: {
        name: 'ExamVault — PYQ Papers',
        short_name: 'ExamVault',
        description: 'Previous Year Question Papers for TNPSC, UPSC, JEE & NEET',
        theme_color: '#10141F',
        background_color: '#10141F',
        display: 'standalone',
        icons: [
          { src: '/icons/icon-192.png', sizes: '192x192', type: 'image/png' },
          { src: '/icons/icon-512.png', sizes: '512x512', type: 'image/png' },
        ],
      },
      workbox: {
        globPatterns: ['**/*.{js,css,html,ico,png,svg}'],
        runtimeCaching: [
          {
            urlPattern: /^http:\/\/localhost:5000\/.*/i,
            handler: 'NetworkFirst',
            options: { cacheName: 'api-cache', networkTimeoutSeconds: 10 },
          },
          {
            urlPattern: /\.pdf$/i,
            handler: 'CacheFirst',
            options: {
              cacheName: 'pdf-cache',
              expiration: { maxEntries: 50, maxAgeSeconds: 7 * 24 * 60 * 60 },
            },
          },
        ],
      },
    }),
  ],
  server: {
    port: 5173,
    proxy: {
      '/api': {
        target: 'http://localhost:5000',
        changeOrigin: true,
        rewrite: (path) => path.replace(/^\/api/, ''),
      },
      '/uploads': {
        target: 'http://localhost:5000',
        changeOrigin: true,
      },
    },
  },
})
