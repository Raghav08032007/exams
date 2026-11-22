import { useState, useEffect, useCallback } from 'react'
import { downloadPaper } from '../api/client'
import { useToastStore } from '../store'

export function useOfflineStorage(paper) {
  const [isCached, setIsCached] = useState(false)
  const [isDownloading, setIsDownloading] = useState(false)
  const addToast = useToastStore((state) => state.addToast)

  // Check if paper's PDF is already in the Workbox pdf-cache
  const checkCache = useCallback(async () => {
    if (!paper?.pdf_url || !('caches' in window)) return
    try {
      const cache = await caches.open('pdf-cache')
      // Make URL absolute for Cache API checking
      const url = new URL(paper.pdf_url, window.location.origin).toString()
      const response = await cache.match(url)
      setIsCached(!!response)
    } catch (err) {
      console.error('Cache check failed:', err)
    }
  }, [paper?.pdf_url])

  useEffect(() => {
    checkCache()
  }, [checkCache])

  const saveForOffline = async () => {
    if (!paper) return
    setIsDownloading(true)
    try {
      // 1. Tell backend we are downloading this paper (increments count, gets URL)
      const data = await downloadPaper(paper.id)
      
      // 2. Fetch the actual PDF to trigger Workbox CacheFirst strategy
      const url = data.pdf_url
      if (!url) throw new Error('No PDF URL returned')

      // Ensure it's cached by explicitly fetching it
      await fetch(url, { mode: 'no-cors' })
      
      setIsCached(true)
      addToast('Paper saved for offline use!', 'success')
    } catch (err) {
      addToast('Failed to save paper for offline', 'error')
      console.error(err)
    } finally {
      setIsDownloading(false)
    }
  }

  const removeFromOffline = async () => {
    if (!paper?.pdf_url || !('caches' in window)) return
    try {
      const cache = await caches.open('pdf-cache')
      const url = new URL(paper.pdf_url, window.location.origin).toString()
      await cache.delete(url)
      setIsCached(false)
      addToast('Paper removed from offline storage', 'success')
    } catch (err) {
      console.error('Failed to remove from cache:', err)
    }
  }

  return {
    isCached,
    isDownloading,
    saveForOffline,
    removeFromOffline
  }
}
