/**
 * ScrollReveal — GSAP ScrollTrigger wrapper that stagger-fades children into view.
 * Automatically skips animation if prefers-reduced-motion is set.
 *
 * Usage:
 *   <ScrollReveal className="papers-list">
 *     {items.map(item => <Card key={item.id} ... />)}
 *   </ScrollReveal>
 */
import { useEffect, useRef } from 'react'
import gsap from 'gsap'
import { ScrollTrigger } from 'gsap/ScrollTrigger'
import { useReducedMotion } from '../../hooks/useReducedMotion'

gsap.registerPlugin(ScrollTrigger)

export default function ScrollReveal({
  children,
  className,
  stagger = 0.065,
  y = 28,
  duration = 0.55,
  start = 'top 86%',
  ...rest
}) {
  const containerRef = useRef(null)
  const reduced = useReducedMotion()

  useEffect(() => {
    if (reduced || !containerRef.current) return

    const items = Array.from(containerRef.current.children)
    if (!items.length) return

    // Set initial invisible state
    gsap.set(items, { opacity: 0, y, willChange: 'opacity, transform' })

    const ctx = gsap.context(() => {
      gsap.to(items, {
        opacity: 1,
        y: 0,
        stagger,
        duration,
        ease: 'power3.out',
        clearProps: 'willChange',
        scrollTrigger: {
          trigger: containerRef.current,
          start,
          once: true,
        },
      })
    }, containerRef)

    return () => ctx.revert()
  }, [reduced, stagger, y, duration, start])

  return (
    <div ref={containerRef} className={className} {...rest}>
      {children}
    </div>
  )
}
