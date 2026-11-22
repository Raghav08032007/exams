import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import './index.css'
import App from './App.jsx'
import { registerSW } from 'virtual:pwa-register'

// Unregister any stale / foreign service workers (e.g. CarePulse)
// before registering ExamVault's own SW.
if ('serviceWorker' in navigator) {
  navigator.serviceWorker.getRegistrations().then((registrations) => {
    for (const registration of registrations) {
      const swUrl = registration.active?.scriptURL || registration.installing?.scriptURL || ''
      // Keep only our own sw.js; kill everything else
      if (!swUrl.includes('sw.js') || swUrl.includes('carepulse')) {
        registration.unregister()
      }
    }
  })
  // Also clear all caches that don't belong to ExamVault
  caches.keys().then((cacheNames) => {
    cacheNames.forEach((cacheName) => {
      if (!cacheName.startsWith('examvault') && !cacheName.startsWith('workbox')) {
        caches.delete(cacheName)
      }
    })
  })
}

registerSW({ immediate: true })

createRoot(document.getElementById('root')).render(
  <StrictMode>
    <App />
  </StrictMode>,
)

