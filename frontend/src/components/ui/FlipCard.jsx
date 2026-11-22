/**
 * FlipCard — CSS 3D index card for papers on the Year page.
 * Light theme — Phase 5 redesign.
 *
 * Front: Year (mono, large), session (if present), title, language + answer-key badges.
 * Back:  Subjects, language, download count, session, "Open Paper →" CTA.
 *
 * Interaction:
 *   - Hover (desktop): cursor-position tilt via useTilt hook
 *   - Click front: flip to back (JS state)
 *   - Click back / CTA: navigate to paper detail
 *   - Click "← Back" button: unflip
 *   - prefers-reduced-motion: falls back to plain paper-item list row
 */
import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { AnswerKeyBadge, LanguageBadge, PaperTypeBadge } from './Badges'
import { useReducedMotion } from '../../hooks/useReducedMotion'
import { useTilt } from '../../hooks/useTilt'

function fmtSize(bytes) {
  if (!bytes) return null
  return bytes < 1048576
    ? `${(bytes / 1024).toFixed(0)} KB`
    : `${(bytes / 1048576).toFixed(1)} MB`
}

export default function FlipCard({ paper, accentColor = '#8FB9A8' }) {
  const navigate = useNavigate()
  const reduced  = useReducedMotion()
  const [flipped, setFlipped] = useState(false)
  const { ref: tiltRef, tiltStyle } = useTilt({ max: 9, disabled: reduced || flipped })

  // ── Reduced-motion fallback: plain list row ───────────────
  if (reduced) {
    return (
      <a
        href={`/paper/${paper.id}`}
        className="paper-item"
        style={{ textDecoration: 'none' }}
        onClick={(e) => { e.preventDefault(); navigate(`/paper/${paper.id}`) }}
      >
        <div className="paper-item-year mono" style={{ color: accentColor }}>
          {paper.year}
          {paper.session && (
            <span style={{ fontSize: '0.625rem', marginLeft: 4, color: 'var(--text-muted)', display: 'block', fontWeight: 500 }}>
              {paper.session}
            </span>
          )}
        </div>
        <div className="paper-item-content">
          <div className="paper-item-title">{paper.title}</div>
          <div className="paper-item-meta" style={{ display: 'flex', gap: 6, alignItems: 'center', flexWrap: 'wrap' }}>
            <PaperTypeBadge paperType={paper.paper_type} />
            <LanguageBadge language={paper.language} />
            {paper.has_answer_key && <AnswerKeyBadge />}
          </div>
        </div>
        <span className="btn btn-ghost btn-sm">View →</span>
      </a>
    )
  }

  // ── Animated flip card ────────────────────────────────────
  return (
    <div
      className={`flip-card-container ${flipped ? 'is-flipped' : ''}`}
      aria-label={paper.title}
    >
      <div className="flip-card-inner">

        {/* ── Front Face — Index Card ── */}
        <div
          ref={tiltRef}
          className="flip-card-face flip-card-front"
          style={!flipped ? tiltStyle : undefined}
          onClick={() => setFlipped(true)}
          role="button"
          tabIndex={flipped ? -1 : 0}
          aria-label={`${paper.title}. Click to see details.`}
          onKeyDown={(e) => e.key === 'Enter' && setFlipped(true)}
        >
          {/* Accent stripe */}
          <div className="flip-card-stripe" style={{ background: accentColor }} />

          <div className="flip-card-front-body" style={{ display: 'flex', flexDirection: 'column', height: '100%', padding: '20px' }}>
            {/* Header meta row */}
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 8, gap: 6, flexWrap: 'wrap' }}>
              <div className="flip-card-year mono" style={{ color: accentColor, fontSize: '1.25rem', fontWeight: 700 }}>
                {paper.year}
              </div>
              <div style={{ display: 'flex', gap: 6, alignItems: 'center' }}>
                <PaperTypeBadge paperType={paper.paper_type} />
                <span className="badge badge-language" style={{ backgroundColor: 'rgba(16, 185, 129, 0.12)', color: '#10B981', fontSize: '0.7rem', fontWeight: 600 }}>
                  📄 PDF
                </span>
              </div>
            </div>

            {/* Session sub-label */}
            {paper.session && (
              <div style={{
                fontSize: '0.75rem',
                color: accentColor,
                fontFamily: 'var(--font-mono)',
                fontWeight: 600,
                letterSpacing: '0.04em',
                marginBottom: 6,
              }}>
                {paper.session}
              </div>
            )}

            {/* Paper Title */}
            <div className="flip-card-title" style={{ fontSize: '1rem', fontWeight: 700, lineHeight: 1.35, marginBottom: 8, color: 'var(--text-primary)' }}>
              {paper.title}
            </div>

            {/* Official Source Pill */}
            {paper.source_name && (
              <div style={{
                fontSize: '0.7rem',
                color: 'var(--text-muted)',
                marginBottom: 8,
                display: 'inline-flex',
                alignItems: 'center',
                gap: 5,
                background: 'rgba(255,255,255,0.05)',
                padding: '2px 8px',
                borderRadius: '4px',
                border: '1px solid var(--color-border)'
              }}>
                <span>🏛️</span>
                <span>{paper.source_name}</span>
              </div>
            )}

            {/* Subject Badges */}
            {Array.isArray(paper.subjects) && paper.subjects.length > 0 && (
              <div style={{ display: 'flex', gap: 6, flexWrap: 'wrap', marginBottom: 10 }}>
                {paper.subjects.slice(0, 3).map((sub) => {
                  const sName = typeof sub === 'object' ? sub.name : sub
                  return (
                    <span
                      key={sName}
                      className="badge"
                      style={{
                        fontSize: '0.6875rem',
                        padding: '2px 8px',
                        borderRadius: '6px',
                        backgroundColor: `${accentColor}18`,
                        color: accentColor,
                        fontWeight: 600,
                        border: `1px solid ${accentColor}33`,
                      }}
                    >
                      {sName}
                    </span>
                  )
                })}
                {paper.subjects.length > 3 && (
                  <span style={{ fontSize: '0.6875rem', color: 'var(--text-muted)', alignSelf: 'center' }}>
                    +{paper.subjects.length - 3}
                  </span>
                )}
              </div>
            )}

            {/* Cover Image / PDF Thumbnail Preview */}
            {paper.cover_image_url ? (
              <div style={{ width: '100%', height: '90px', borderRadius: '8px', overflow: 'hidden', marginBottom: 12, border: '1px solid var(--color-border)' }}>
                <img src={paper.cover_image_url} alt={paper.title} style={{ width: '100%', height: '100%', objectFit: 'cover' }} />
              </div>
            ) : (
              <div style={{
                width: '100%',
                padding: '10px 12px',
                borderRadius: '8px',
                backgroundColor: 'rgba(0,0,0,0.03)',
                border: '1px border-dashed var(--color-border)',
                marginBottom: 12,
                display: 'flex',
                alignItems: 'center',
                gap: 10,
                fontSize: '0.78125rem',
                color: 'var(--text-secondary)',
              }}>
                <span style={{ fontSize: '1.4rem' }}>📑</span>
                <span style={{ flex: 1, fontWeight: 500, whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis' }}>
                  Official {paper.year} Question Paper PDF
                </span>
              </div>
            )}

            {/* Badges */}
            <div className="flip-card-badges" style={{ marginBottom: 12, display: 'flex', gap: 6, flexWrap: 'wrap', alignItems: 'center' }}>
              <LanguageBadge language={paper.language} />
              {paper.has_answer_key && <AnswerKeyBadge />}
              {paper.textbooks?.length > 0 && (
                <span className="badge" style={{ backgroundColor: 'rgba(37, 99, 235, 0.1)', color: '#2563EB', border: '1px solid rgba(37, 99, 235, 0.25)', fontSize: '0.7rem', fontWeight: 600 }}>
                  📚 Textbook
                </span>
              )}
            </div>

            {/* Action buttons on front */}
            <div style={{ display: 'flex', gap: 6, marginTop: 'auto', width: '100%', flexWrap: 'wrap' }}>
              <button
                className="btn btn-primary btn-sm"
                style={{ flex: 1, backgroundColor: accentColor, borderColor: accentColor, color: '#fff', fontWeight: 600, padding: '8px 10px', minWidth: 90 }}
                onClick={(e) => { e.stopPropagation(); navigate(`/paper/${paper.id}`) }}
              >
                👁️ View PDF →
              </button>
              {paper.has_answer_key && (
                <button
                  className="btn btn-ghost btn-sm"
                  style={{ color: '#10B981', borderColor: 'rgba(16,185,129,0.4)', fontWeight: 600, padding: '8px 10px' }}
                  onClick={(e) => { e.stopPropagation(); navigate(`/paper/${paper.id}?tab=key`) }}
                  title="Open Official Answer Key directly"
                >
                  🔑 Key
                </button>
              )}
              {paper.pdf_url && (
                <a
                  href={paper.pdf_url}
                  download
                  className="btn btn-ghost btn-sm"
                  style={{ textDecoration: 'none', border: '1px solid var(--color-border)', padding: '8px 10px' }}
                  onClick={(e) => e.stopPropagation()}
                >
                  📥
                </a>
              )}
            </div>
          </div>

          {/* Corner stamp */}
          <div className="flip-card-stamp" style={{ borderColor: accentColor, color: accentColor }}>
            PYQ
          </div>
        </div>

        {/* ── Back Face — Details ── */}
        <div
          className="flip-card-face flip-card-back"
          style={{ '--exam-accent': accentColor }}
          role="button"
          tabIndex={flipped ? 0 : -1}
          aria-label={`Open ${paper.title}`}
          onKeyDown={(e) => e.key === 'Enter' && navigate(`/paper/${paper.id}`)}
        >
          <div className="flip-card-back-body" style={{ padding: '20px', display: 'flex', flexDirection: 'column', height: '100%' }}>
            {/* Title Header */}
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', gap: 8, marginBottom: 10 }}>
              <div style={{ fontSize: '0.9375rem', fontWeight: 700, color: 'var(--text-primary)', lineHeight: 1.3 }}>
                {paper.title}
              </div>
              <PaperTypeBadge paperType={paper.paper_type} />
            </div>

            {/* Subjects */}
            <div className="flip-card-back-section" style={{ marginBottom: 10 }}>
              <div className="flip-card-back-label">Subjects</div>
              <div className="flip-card-back-value" style={{ fontWeight: 600 }}>
                {Array.isArray(paper.subjects) && paper.subjects.length > 0
                  ? paper.subjects.map(s => typeof s === 'object' ? s.name : s).join(' · ')
                  : 'General Studies'}
              </div>
            </div>

            {/* Language & Session */}
            <div style={{ display: 'flex', gap: 16, marginBottom: 10 }}>
              <div>
                <div className="flip-card-back-label">Language</div>
                <div className="flip-card-back-value" style={{ fontWeight: 600 }}>{paper.language}</div>
              </div>
              {paper.session && (
                <div>
                  <div className="flip-card-back-label">Session</div>
                  <div className="flip-card-back-value" style={{ fontWeight: 600 }}>{paper.session}</div>
                </div>
              )}
            </div>

            {/* Stats row */}
            <div style={{ display: 'flex', gap: 10, flexWrap: 'wrap', alignItems: 'center', marginBottom: 14 }}>
              {paper.has_answer_key && (
                <span style={{ fontSize: '0.75rem', color: '#16a34a', fontWeight: 600 }}>✓ Answer Key Included</span>
              )}
              {paper.textbooks?.length > 0 && (
                <span style={{ fontSize: '0.75rem', color: '#2563EB', fontWeight: 600 }}>📚 Textbook Attached</span>
              )}
              <span className="mono" style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>
                ↓ {(paper.download_count || 0).toLocaleString()} downloads
              </span>
              {fmtSize(paper.file_size) && (
                <span className="mono" style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>
                  ({fmtSize(paper.file_size)})
                </span>
              )}
            </div>

            {/* CTA Buttons */}
            <div style={{ display: 'flex', gap: 6, width: '100%', marginTop: 'auto', flexWrap: 'wrap' }}>
              <button
                className="flip-card-cta"
                style={{ flex: 1, background: accentColor, color: '#fff', padding: '9px 12px', fontSize: '0.8125rem', fontWeight: 600, minWidth: 90 }}
                onClick={(e) => { e.stopPropagation(); navigate(`/paper/${paper.id}`) }}
              >
                👁️ View PDF →
              </button>
              {paper.has_answer_key && (
                <button
                  className="btn btn-ghost btn-sm"
                  style={{ color: '#10B981', borderColor: 'rgba(16,185,129,0.4)', padding: '9px 10px', fontWeight: 600 }}
                  onClick={(e) => { e.stopPropagation(); navigate(`/paper/${paper.id}?tab=key`) }}
                  title="Open Answer Key"
                >
                  🔑 Key
                </button>
              )}
              {paper.pdf_url && (
                <a
                  href={paper.pdf_url}
                  download
                  className="btn btn-ghost btn-sm"
                  style={{ textDecoration: 'none', border: '1px solid var(--color-border)', padding: '9px 10px', fontWeight: 600 }}
                  onClick={(e) => e.stopPropagation()}
                >
                  📥
                </a>
              )}
            </div>

            {/* Unflip */}
            <button
              className="flip-card-back-btn"
              style={{ marginTop: 8 }}
              onClick={(e) => { e.stopPropagation(); setFlipped(false) }}
            >
              ← Flip back
            </button>
          </div>
        </div>

      </div>
    </div>
  )
}
