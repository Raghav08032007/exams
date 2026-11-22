/**
 * HeroHUD.jsx
 * Text overlay HUD component synced with currentIndex.
 * Animates text entrances/exits via Framer Motion AnimatePresence mode="wait".
 */
import { motion, AnimatePresence } from 'framer-motion'

export default function HeroHUD({ exam, index, total, onJumpToIndex, hasInteracted }) {
  return (
    <div
      className="hero-hud-wrapper"
      style={{
        display: 'flex',
        flexDirection: 'column',
        alignItems: 'center',
        textAlign: 'center',
        maxWidth: 'min(640px, 92vw)',
        margin: '12px auto 32px',
        pointerEvents: 'none', // Allow card clicks through empty areas
      }}
    >
      <AnimatePresence mode="wait">
        <motion.div
          key={exam.slug}
          initial={{ y: 24, opacity: 0, filter: 'blur(6px)' }}
          animate={{ y: 0, opacity: 1, filter: 'blur(0px)' }}
          exit={{ y: -16, opacity: 0, filter: 'blur(3px)' }}
          transition={{ duration: 0.55, ease: [0.22, 1, 0.36, 1] }}
          style={{ pointerEvents: 'auto' }}
        >
          {/* Serial Number & Upper Slug */}
          <div
            style={{
              fontFamily: "'IBM Plex Mono', monospace",
              fontSize: '0.75rem',
              fontWeight: 700,
              letterSpacing: '0.22em',
              textTransform: 'uppercase',
              color: exam.accent,
              marginBottom: 'var(--space-2)',
            }}
          >
            0{index + 1} / {exam.name}
          </div>

          {/* Main Full Name Heading */}
          <h2
            style={{
              fontFamily: "'Fraunces', Georgia, serif",
              fontSize: 'clamp(1.75rem, 4vw, 2.75rem)',
              fontWeight: 700,
              color: 'var(--text-primary)',
              lineHeight: 1.15,
              marginBottom: 'var(--space-2)',
              letterSpacing: '-0.02em',
            }}
          >
            {exam.fullName}
          </h2>

          {/* Subtitle / Tagline */}
          <p
            style={{
              fontFamily: "'Inter', sans-serif",
              fontSize: '1rem',
              fontWeight: 600,
              color: exam.accent,
              marginBottom: 'var(--space-3)',
            }}
          >
            {exam.tagline}
          </p>

          {/* Description */}
          <p
            style={{
              fontFamily: "'Inter', sans-serif",
              fontSize: '0.9375rem',
              color: 'var(--text-secondary)',
              maxWidth: '520px',
              margin: '0 auto var(--space-4)',
              lineHeight: 1.6,
            }}
          >
            {exam.description}
          </p>

          {/* Stat Badge */}
          <div
            style={{
              display: 'inline-block',
              fontFamily: "'IBM Plex Mono', monospace",
              fontSize: '0.75rem',
              fontWeight: 600,
              color: 'var(--text-primary)',
              backgroundColor: 'var(--color-bg-raised)',
              border: `1px solid ${exam.accent}`,
              padding: '4px 14px',
              borderRadius: '9999px',
              letterSpacing: '0.06em',
              textTransform: 'uppercase',
            }}
          >
            {exam.stat}
          </div>
        </motion.div>
      </AnimatePresence>

      {/* Cycle Position Dots (Interactive Jump) */}
      <div
        style={{
          display: 'flex',
          alignItems: 'center',
          gap: '10px',
          marginTop: 'var(--space-5)',
          pointerEvents: 'auto',
        }}
      >
        {Array.from({ length: total }, (_, i) => {
          const isActive = i === index
          return (
            <button
              key={i}
              type="button"
              onClick={() => onJumpToIndex(i)}
              aria-label={`Jump to ${exam.name}`}
              style={{
                width: isActive ? '24px' : '10px',
                height: '10px',
                borderRadius: '9999px',
                backgroundColor: isActive ? exam.accent : 'transparent',
                border: `1.5px solid ${isActive ? exam.accent : 'var(--text-muted)'}`,
                cursor: 'pointer',
                transition: 'all 0.3s ease',
                padding: 0,
              }}
            />
          )
        })}
      </div>

      {/* Caption Helper Text (Fades out after first interaction) */}
      <AnimatePresence>
        {!hasInteracted && (
          <motion.div
            initial={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            transition={{ duration: 0.4 }}
            style={{
              fontFamily: "'Inter', sans-serif",
              fontSize: '0.75rem',
              color: 'var(--text-muted)',
              marginTop: 'var(--space-3)',
            }}
          >
            Click the folder to browse exams
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  )
}
