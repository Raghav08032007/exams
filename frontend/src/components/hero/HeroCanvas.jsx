/**
 * HeroCanvas — 3D Frame-Sequence Card-Cycle Transition Hero
 *
 * Folder path: frontend/ezgif-2e3765a2f2d84e19-jpg
 * Uses all 50 frame images (ezgif-frame-001.jpg through ezgif-frame-050.jpg)
 * for the 3D card-cycling transition effect!
 *
 * Cycle Order: UPSC → TNPSC → JEE → NEET → UPSC
 */
import { useState, useEffect, useRef, useMemo } from 'react'
import { useNavigate } from 'react-router-dom'
import { useAuthStore, useToastStore } from '../../store'
import { useReducedMotion } from '../../hooks/useReducedMotion'

// Dynamically import all 50 frame images from frontend/ezgif-2e3765a2f2d84e19-jpg
const frameModules = import.meta.glob('../../ezgif-2e3765a2f2d84e19-jpg/*.jpg', { eager: true, import: 'default' })

// Sort frame URLs by file name (ezgif-frame-001.jpg -> ezgif-frame-050.jpg)
const FRAME_URLS = Object.keys(frameModules)
  .sort((a, b) => {
    const numA = parseInt(a.match(/frame-(\d+)/)?.[1] || '0', 10)
    const numB = parseInt(b.match(/frame-(\d+)/)?.[1] || '0', 10)
    return numA - numB
  })
  .map(k => frameModules[k])

const EXAMS_DATA = [
  { slug: 'upsc',  label: 'UPSC',  sub: 'Civil Services Exam',   color: '#8FB9A8', emoji: '🏛️', count: '120+ Papers' },
  { slug: 'tnpsc', label: 'TNPSC', sub: 'State Civil Services',  color: '#E8998D', emoji: '📋', count: '180+ Papers' },
  { slug: 'jee',   label: 'JEE',   sub: 'Engineering Entrance',  color: '#8FB8E0', emoji: '⚗️', count: '210+ Papers' },
  { slug: 'neet',  label: 'NEET',  sub: 'Medical Entrance',      color: '#C3A8D9', emoji: '🩺', count: '140+ Papers' },
]

export default function HeroCanvas() {
  const navigate = useNavigate()
  const reduced = useReducedMotion()

  const [activeIndex, setActiveIndex]   = useState(0)
  const [frameIndex, setFrameIndex]     = useState(0)
  const [isTransitioning, setIsTrans]   = useState(false)
  const [tiltStyle, setTiltStyle]       = useState({})

  const animRef = useRef(null)
  const touchStartRef = useRef(null)

  // Preload all 50 frame images into browser memory
  useEffect(() => {
    FRAME_URLS.forEach((url) => {
      const img = new Image()
      img.src = url
    })
  }, [])

  // Current active exam info
  const currentExam = EXAMS_DATA[activeIndex]
  const nextExam    = EXAMS_DATA[(activeIndex + 1) % EXAMS_DATA.length]
  const peekExam2   = EXAMS_DATA[(activeIndex + 2) % EXAMS_DATA.length]

  // Triggers the 50-frame transition sequence on click / tap / swipe
  const handleCycle = () => {
    if (isTransitioning) return
    setIsTrans(true)

    const totalFrames = FRAME_URLS.length
    const duration = 750 // 750ms total transition
    const startTime = performance.now()

    const step = (now) => {
      const elapsed = now - startTime
      const progress = Math.min(elapsed / duration, 1)
      const f = Math.floor(progress * (totalFrames - 1))
      setFrameIndex(f)

      if (progress < 1) {
        animRef.current = requestAnimationFrame(step)
      } else {
        // Complete transition: advance to next exam in cycle order
        setActiveIndex((prev) => (prev + 1) % EXAMS_DATA.length)
        setFrameIndex(0)
        setIsTrans(false)
      }
    }

    animRef.current = requestAnimationFrame(step)
  }

  const handleNavigate = (slug) => {
    const user = useAuthStore.getState().user
    if (!user) {
      useToastStore.getState().addToast('Please sign in or register to browse exam papers.', 'info')
      navigate('/login')
      return
    }
    navigate(`/exam/${slug}`)
  }

  // 3D Parallax Tilt Effect on Mouse Movement
  const handleMouseMove = (e) => {
    if (reduced || isTransitioning) return
    const rect = e.currentTarget.getBoundingClientRect()
    const x = e.clientX - rect.left - rect.width / 2
    const y = e.clientY - rect.top - rect.height / 2
    const rotX = (y / rect.height) * -14
    const rotY = (x / rect.width) * 14
    setTiltStyle({
      transform: `perspective(1000px) rotateX(${rotX}deg) rotateY(${rotY}deg) scale3d(1.02, 1.02, 1.02)`,
      transition: 'transform 0.1s ease-out',
    })
  }

  const handleMouseLeave = () => {
    setTiltStyle({
      transform: 'perspective(1000px) rotateX(0deg) rotateY(0deg) scale3d(1, 1, 1)',
      transition: 'transform 0.5s ease',
    })
  }

  // Mobile Swipe Handlers
  const handleTouchStart = (e) => {
    touchStartRef.current = e.touches[0].clientX
  }

  const handleTouchEnd = (e) => {
    if (!touchStartRef.current) return
    const touchEnd = e.changedTouches[0].clientX
    if (Math.abs(touchStartRef.current - touchEnd) > 35) {
      handleCycle()
    }
    touchStartRef.current = null
  }

  return (
    <div
      style={{
        width: '100%',
        display: 'flex',
        flexDirection: 'column',
        alignItems: 'center',
        justifyContent: 'center',
        padding: '20px 0',
        userSelect: 'none',
      }}
      onTouchStart={handleTouchStart}
      onTouchEnd={handleTouchEnd}
    >
      {/* Interactive Hero Stack Box */}
      <div
        onMouseMove={handleMouseMove}
        onMouseLeave={handleMouseLeave}
        onClick={(e) => {
          if (e.target.tagName !== 'BUTTON') {
            handleCycle()
          }
        }}
        style={{
          position: 'relative',
          width: '380px',
          maxWidth: '90vw',
          height: '270px',
          cursor: 'pointer',
          ...tiltStyle,
        }}
      >
        {/* Background Stack Peek 2 (Furthest) */}
        <div
          style={{
            position: 'absolute',
            top: '-20px',
            right: '-20px',
            width: '100%',
            height: '100%',
            backgroundColor: peekExam2.color,
            borderRadius: '20px',
            opacity: 0.5,
            transform: 'scale(0.86) rotate(6deg)',
            boxShadow: 'var(--shadow-sm)',
            border: '1px solid rgba(255,255,255,0.4)',
          }}
        />

        {/* Background Stack Peek 1 (Middle) */}
        <div
          style={{
            position: 'absolute',
            top: '-10px',
            right: '-10px',
            width: '100%',
            height: '100%',
            backgroundColor: nextExam.color,
            borderRadius: '20px',
            opacity: 0.75,
            transform: 'scale(0.93) rotate(3deg)',
            boxShadow: 'var(--shadow-md)',
            border: '1px solid rgba(255,255,255,0.5)',
          }}
        />

        {/* Main Front Card Container with Frame Transition */}
        <div
          style={{
            position: 'relative',
            width: '100%',
            height: '100%',
            backgroundColor: currentExam.color,
            borderRadius: '20px',
            boxShadow: 'var(--shadow-xl)',
            overflow: 'hidden',
            border: '1.5px solid rgba(255,255,255,0.6)',
            display: 'flex',
            flexDirection: 'column',
            justifyContent: 'space-between',
            padding: '24px',
          }}
        >
          {/* Active Frame Image from ezgif-2e3765a2f2d84e19-jpg */}
          {FRAME_URLS.length > 0 && (
            <img
              src={FRAME_URLS[frameIndex] || FRAME_URLS[0]}
              alt={`3D Card Transition Frame ${frameIndex + 1}`}
              style={{
                position: 'absolute',
                top: 0,
                left: 0,
                width: '100%',
                height: '100%',
                objectFit: 'cover',
                opacity: isTransitioning ? 0.92 : 0.28,
                mixBlendMode: isTransitioning ? 'normal' : 'multiply',
                transition: 'opacity 0.2s ease',
                pointerEvents: 'none',
              }}
            />
          )}

          {/* Top Folder Accent Bar */}
          <div
            style={{
              position: 'relative',
              zIndex: 2,
              display: 'flex',
              justifyContent: 'space-between',
              alignItems: 'center',
            }}
          >
            <div
              style={{
                display: 'inline-flex',
                alignItems: 'center',
                gap: '8px',
                padding: '6px 14px',
                borderRadius: '9999px',
                backgroundColor: 'rgba(255,255,255,0.85)',
                backdropFilter: 'blur(8px)',
                boxShadow: '0 2px 8px rgba(0,0,0,0.08)',
              }}
            >
              <span style={{ fontSize: '18px' }}>{currentExam.emoji}</span>
              <span
                style={{
                  fontFamily: "'IBM Plex Mono', monospace",
                  fontSize: '13px',
                  fontWeight: 700,
                  letterSpacing: '0.12em',
                  color: '#2B2A28',
                  textTransform: 'uppercase',
                }}
              >
                {currentExam.label}
              </span>
            </div>

            <span
              style={{
                fontFamily: "'IBM Plex Mono', monospace",
                fontSize: '10px',
                fontWeight: 600,
                letterSpacing: '0.1em',
                color: 'rgba(43,42,40,0.65)',
                backgroundColor: 'rgba(255,255,255,0.6)',
                padding: '4px 10px',
                borderRadius: '9999px',
                textTransform: 'uppercase',
              }}
            >
              {currentExam.count}
            </span>
          </div>

          {/* Middle Exam Subtitle & Status */}
          <div style={{ position: 'relative', zIndex: 2, textAlign: 'center', margin: 'auto 0' }}>
            <h2
              style={{
                fontFamily: "'Fraunces', Georgia, serif",
                fontSize: '24px',
                fontWeight: 700,
                color: '#2B2A28',
                margin: '0 0 4px',
                letterSpacing: '-0.01em',
              }}
            >
              {currentExam.sub}
            </h2>
            <p
              style={{
                fontFamily: "'Inter', sans-serif",
                fontSize: '12px',
                color: 'rgba(43,42,40,0.7)',
                margin: 0,
              }}
            >
              {isTransitioning ? `Transitioning to ${nextExam.label}…` : 'Click card to cycle next exam'}
            </p>
          </div>

          {/* Bottom Actions Bar */}
          <div
            style={{
              position: 'relative',
              zIndex: 2,
              display: 'flex',
              justifyContent: 'space-between',
              alignItems: 'center',
            }}
          >
            <span
              style={{
                fontSize: '11px',
                fontFamily: "'IBM Plex Mono', monospace",
                color: 'rgba(43,42,40,0.6)',
                letterSpacing: '0.05em',
              }}
            >
              Cycle: {currentExam.label} → {nextExam.label}
            </span>

            <button
              type="button"
              onClick={(e) => {
                e.stopPropagation()
                handleNavigate(currentExam.slug)
              }}
              style={{
                padding: '8px 18px',
                fontSize: '12px',
                fontWeight: 600,
                fontFamily: "'Inter', sans-serif",
                color: '#FAF7F2',
                backgroundColor: '#2B2A28',
                border: 'none',
                borderRadius: '9999px',
                cursor: 'pointer',
                boxShadow: '0 4px 14px rgba(0,0,0,0.2)',
                transition: 'transform 0.15s ease, background-color 0.15s ease',
              }}
              onMouseEnter={(e) => (e.target.style.transform = 'scale(1.06)')}
              onMouseLeave={(e) => (e.target.style.transform = 'scale(1.0)')}
            >
              View Papers →
            </button>
          </div>
        </div>
      </div>

      {/* Frame Sequence Indicator Bar */}
      <div
        style={{
          marginTop: '16px',
          display: 'flex',
          alignItems: 'center',
          gap: '8px',
          fontSize: '11px',
          fontFamily: "'IBM Plex Mono', monospace",
          color: 'var(--text-muted)',
          textTransform: 'uppercase',
          letterSpacing: '0.08em',
        }}
      >
        <span>Card Cycle ({activeIndex + 1}/4)</span>
        <div style={{ width: '40px', height: '3px', backgroundColor: 'var(--color-border)', borderRadius: '2px', overflow: 'hidden' }}>
          <div
            style={{
              width: `${((frameIndex + 1) / FRAME_URLS.length) * 100}%`,
              height: '100%',
              backgroundColor: currentExam.color,
              transition: 'width 0.05s linear',
            }}
          />
        </div>
        <span>{currentExam.label}</span>
      </div>
    </div>
  )
}
