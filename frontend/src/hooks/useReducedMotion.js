/**
 * useReducedMotion — reactively reads the OS-level prefers-reduced-motion media query.
 * All animation components must check this before applying any motion.
 */
import { useState, useEffect } from 'react'

export function useReducedMotion() {
  const [prefersReducedMotion, set] = useState(() =>
    typeof window !== 'undefined'
      ? window.matchMedia('(prefers-reduced-motion: reduce)').matches
      : false
  )

  useEffect(() => {
    const mq = window.matchMedia('(prefers-reduced-motion: reduce)')
    const handler = (e) => set(e.matches)
    mq.addEventListener('change', handler)
    return () => mq.removeEventListener('change', handler)
  }, [])

  return prefersReducedMotion
}
