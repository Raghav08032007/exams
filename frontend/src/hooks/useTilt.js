/**
 * useTilt — cursor-position based 3D tilt effect for cards.
 *
 * Usage:
 *   const { ref, tiltStyle } = useTilt({ max: 10, disabled: false })
 *   <div ref={ref} style={{ ...cardStyle, ...tiltStyle }}>…</div>
 *
 * The tilt is applied via CSS transform: perspective + rotateX/rotateY.
 * Automatically disabled when prefers-reduced-motion is active (via `disabled` prop).
 * Resets to flat on mouse leave (smooth lerp via CSS transition).
 */
import { useRef, useCallback } from 'react'

export function useTilt({ max = 12, perspective = 700, disabled = false } = {}) {
  const ref = useRef(null)
  const tiltRef = useRef({ x: 0, y: 0 })
  const rafRef  = useRef(null)

  const onMouseMove = useCallback((e) => {
    if (disabled || !ref.current) return
    const rect = ref.current.getBoundingClientRect()
    const cx   = rect.left + rect.width  / 2
    const cy   = rect.top  + rect.height / 2
    const dx   = (e.clientX - cx) / (rect.width  / 2)
    const dy   = (e.clientY - cy) / (rect.height / 2)
    tiltRef.current = { x: dy * max, y: -dx * max }

    if (rafRef.current) cancelAnimationFrame(rafRef.current)
    rafRef.current = requestAnimationFrame(() => {
      if (ref.current) {
        ref.current.style.transform =
          `perspective(${perspective}px) rotateX(${tiltRef.current.x}deg) rotateY(${tiltRef.current.y}deg) translateZ(4px)`
      }
    })
  }, [disabled, max, perspective])

  const onMouseLeave = useCallback(() => {
    if (disabled || !ref.current) return
    if (rafRef.current) cancelAnimationFrame(rafRef.current)
    ref.current.style.transform = 'perspective(700px) rotateX(0deg) rotateY(0deg) translateZ(0px)'
  }, [disabled])

  // Attach events to the element via the ref callback
  const setRef = useCallback((el) => {
    if (ref.current) {
      ref.current.removeEventListener('mousemove', onMouseMove)
      ref.current.removeEventListener('mouseleave', onMouseLeave)
    }
    ref.current = el
    if (el && !disabled) {
      el.addEventListener('mousemove', onMouseMove, { passive: true })
      el.addEventListener('mouseleave', onMouseLeave, { passive: true })
    }
  }, [disabled, onMouseMove, onMouseLeave])

  // Provide a base transition style so the reset is smooth
  const tiltStyle = disabled ? {} : {
    transition: 'transform 0.15s ease-out',
    willChange: 'transform',
  }

  return { ref: setRef, tiltStyle }
}
