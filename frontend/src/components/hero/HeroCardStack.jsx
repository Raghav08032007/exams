/**
 * HeroCardStack.jsx
 * Magazine / Page-Style Card Stack displaying matching 3D exam title images.
 * Perfect Alignment:
 * - TNPSC -> 3D TNPSC Image
 * - UPSC  -> 3D UPSC Image
 * - JEE   -> 3D JEE Image
 * - NEET  -> 3D NEET Image
 * Smooth 850ms 3D transition on click.
 */
import { useMemo } from 'react'
import { motion } from 'framer-motion'
import { useNavigate } from 'react-router-dom'
import { useAuthStore, useToastStore } from '../../store'
import { useReducedMotion } from '../../hooks/useReducedMotion'

// Import all 50 transition frame JPEGs from ezgif-2e3765a2f2d84e19-jpg
const frameModules = import.meta.glob('../../../ezgif-2e3765a2f2d84e19-jpg/*.jpg', { eager: true, import: 'default' })

const FRAME_URLS = Object.keys(frameModules)
  .sort((a, b) => {
    const numA = parseInt(a.match(/frame-(\d+)/)?.[1] || '0', 10)
    const numB = parseInt(b.match(/frame-(\d+)/)?.[1] || '0', 10)
    return numA - numB
  })
  .map(k => frameModules[k])

export default function HeroCardStack({ examOrder, currentIndex, onAdvance, isTransitioning, frameIndex }) {
  const navigate = useNavigate()
  const reduced  = useReducedMotion()

  const handleNavigate = (slug, e) => {
    e.stopPropagation()
    const user = useAuthStore.getState().user
    if (!user) {
      useToastStore.getState().addToast('Please sign in or register to browse exam papers.', 'info')
      navigate('/login')
      return
    }
    navigate(`/exam/${slug}`)
  }

  // Compute 3D stack positions for all 4 cards based on currentIndex
  const cardsWithPositions = useMemo(() => {
    return examOrder.map((exam, idx) => {
      const distance = (idx - currentIndex + 4) % 4
      return { exam, idx, distance }
    })
  }, [examOrder, currentIndex])

  return (
    <div
      className="hero-card-stack-wrapper"
      style={{
        perspective: '1400px',
        width: 'min(540px, 92vw)',
        height: 'clamp(250px, 45vw, 320px)',
        position: 'relative',
        margin: '0 auto',
        userSelect: 'none',
      }}
    >
      {cardsWithPositions.map(({ exam, idx, distance }) => {
        const isFront = distance === 0

        // Smooth, fluid page-stack transform
        let animateProps = {
          scale: 1 - distance * 0.10,
          y: distance * 18,
          z: -distance * 70,
          opacity: isFront ? 1 : Math.max(0, 0.70 - distance * 0.25),
          rotateY: isFront ? 0 : -distance * 4,
          zIndex: 40 - distance * 10,
        }

        if (reduced) {
          animateProps = {
            scale: isFront ? 1 : 0.88,
            y: isFront ? 0 : 16,
            z: 0,
            opacity: isFront ? 1 : 0,
            rotateY: 0,
            zIndex: isFront ? 40 : 10,
          }
        }

        // Dedicated 3D Image Frame selection
        const displayImageSrc = isFront
          ? (FRAME_URLS[frameIndex] || FRAME_URLS[exam.activeFrame])
          : FRAME_URLS[exam.activeFrame]

        return (
          <motion.div
            key={exam.slug}
            aria-label={isFront ? `Currently showing ${exam.name}. Click to turn page.` : undefined}
            tabIndex={isFront ? 0 : -1}
            role={isFront ? 'button' : undefined}
            onClick={() => {
              if (isFront && !isTransitioning) {
                onAdvance()
              }
            }}
            onKeyDown={(e) => {
              if (isFront && (e.key === 'Enter' || e.key === ' ')) {
                e.preventDefault()
                onAdvance()
              }
            }}
            animate={animateProps}
            transition={{ duration: 0.75, ease: [0.25, 1, 0.5, 1] }}
            style={{
              position: 'absolute',
              top: 0,
              left: 0,
              width: '100%',
              height: '100%',
              backgroundColor: '#FFFFFF',
              borderRadius: '16px',
              borderLeft: `5px solid ${exam.accent}`,
              borderTop: '1px solid var(--color-border)',
              borderRight: '1px solid var(--color-border)',
              borderBottom: '1px solid var(--color-border)',
              boxShadow: isFront
                ? `0 20px 50px rgba(43,42,40,0.12), 0 6px 18px rgba(0,0,0,0.06)`
                : '0 4px 14px rgba(0,0,0,0.05)',
              padding: '20px 24px',
              display: 'flex',
              flexDirection: 'column',
              justifyContent: 'space-between',
              cursor: isFront ? 'pointer' : 'default',
              overflow: 'hidden',
              transformStyle: 'preserve-3d',
            }}
          >
            {/* Matching 3D Image Display from ezgif-2e3765a2f2d84e19-jpg */}
            {FRAME_URLS.length > 0 && (
              <img
                src={displayImageSrc}
                alt={`${exam.name} 3D Visual`}
                style={{
                  position: 'absolute',
                  inset: 0,
                  width: '100%',
                  height: '100%',
                  objectFit: 'cover',
                  opacity: isFront ? 1 : 0.45,
                  transition: 'opacity 0.25s ease',
                  pointerEvents: 'none',
                  borderRadius: '14px',
                }}
              />
            )}

            {/* Top Page Header Pill Badge */}
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', zIndex: 10 }}>
              <div
                style={{
                  display: 'inline-flex',
                  alignItems: 'center',
                  gap: '8px',
                  padding: '6px 14px',
                  borderRadius: '9999px',
                  backgroundColor: 'rgba(255, 255, 255, 0.95)',
                  backdropFilter: 'blur(8px)',
                  boxShadow: '0 2px 10px rgba(0,0,0,0.14)',
                  border: `1px solid ${exam.accent}`,
                }}
              >
                <span style={{ fontSize: '18px' }}>{exam.emoji}</span>
                <span
                  style={{
                    fontFamily: "'IBM Plex Mono', monospace",
                    fontSize: '13px',
                    fontWeight: 700,
                    letterSpacing: '0.14em',
                    color: 'var(--text-primary)',
                    textTransform: 'uppercase',
                  }}
                >
                  {exam.name}
                </span>
              </div>

              <span
                style={{
                  fontFamily: "'IBM Plex Mono', monospace",
                  fontSize: '11px',
                  fontWeight: 600,
                  color: 'var(--text-primary)',
                  backgroundColor: 'rgba(255, 255, 255, 0.92)',
                  padding: '5px 14px',
                  borderRadius: '9999px',
                  letterSpacing: '0.08em',
                  textTransform: 'uppercase',
                  boxShadow: '0 2px 8px rgba(0,0,0,0.1)',
                }}
              >
                {exam.stat}
              </span>
            </div>

            {/* Bottom Page Footer & Action */}
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', zIndex: 10 }}>
              <span
                style={{
                  fontSize: '11px',
                  fontFamily: "'IBM Plex Mono', monospace",
                  color: 'rgba(255, 255, 255, 0.95)',
                  textShadow: '0 1px 4px rgba(0,0,0,0.85)',
                  letterSpacing: '0.06em',
                }}
              >
                {isFront ? (isTransitioning ? 'Turning page…' : 'Click page to cycle next →') : ''}
              </span>

              {isFront && (
                <button
                  type="button"
                  onClick={(e) => handleNavigate(exam.slug, e)}
                  aria-label={`View ${exam.name} question papers`}
                  style={{
                    padding: '9px 20px',
                    fontSize: '12px',
                    fontWeight: 600,
                    fontFamily: "'Inter', sans-serif",
                    color: 'var(--text-inverse)',
                    backgroundColor: 'var(--text-primary)',
                    border: 'none',
                    borderRadius: '9999px',
                    cursor: 'pointer',
                    boxShadow: '0 4px 16px rgba(0,0,0,0.3)',
                    transition: 'transform 0.15s ease, background-color 0.15s ease',
                  }}
                  onMouseEnter={(e) => (e.currentTarget.style.transform = 'scale(1.05)')}
                  onMouseLeave={(e) => (e.currentTarget.style.transform = 'scale(1.0)')}
                >
                  View Papers →
                </button>
              )}
            </div>
          </motion.div>
        )
      })}
    </div>
  )
}
