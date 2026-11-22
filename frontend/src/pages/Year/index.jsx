/**
 * Year page — grid of CSS 3D flip cards for each paper.
 * Route: /exam/:slug/:category/:year  (optional ?session=)
 *
 * Animation layers:
 *  - FlipCard components: CSS 3D perspective flip (hover=tilt, click=full flip)
 *  - GSAP ScrollReveal: cards fade/rise in as grid scrolls into view
 *  - prefers-reduced-motion: FlipCard renders as plain list, ScrollReveal skipped
 */
import { useEffect, useState } from 'react'
import { useParams, useSearchParams, Link, useNavigate } from 'react-router-dom'
import { motion } from 'framer-motion'
import { fetchPapers, fetchExam } from '../../api/client'
import { useAuthStore, useToastStore } from '../../store'
import FlipCard    from '../../components/ui/FlipCard'
import ScrollReveal from '../../components/animations/ScrollReveal'
import { PageSkeleton } from '../../components/ui/Skeleton'
import { useReducedMotion } from '../../hooks/useReducedMotion'
import { useSEO } from '../../hooks/useSEO'

export default function YearPage() {
  const { slug, category, year } = useParams()
  const [searchParams] = useSearchParams()
  const session = searchParams.get('session') || ''
  const reduced = useReducedMotion()
  const navigate = useNavigate()
  const { user } = useAuthStore()
  const { addToast } = useToastStore()

  useEffect(() => {
    if (!user) {
      addToast('Please sign in or register to browse exam papers.', 'info')
      navigate('/login', { replace: true })
    }
  }, [user, navigate, addToast])

  const [exam,    setExam]    = useState(null)
  const [papers,  setPapers]  = useState([])
  const [selectedSubject, setSelectedSubject] = useState('')
  const [selectedType,    setSelectedType]    = useState('all') // 'all' | 'original' | 'sample'
  const [loading, setLoading] = useState(true)
  const [error,   setError]   = useState(null)

  useEffect(() => {
    setLoading(true)
    Promise.all([
      fetchExam(slug),
      fetchPapers({
        exam:     slug,
        category: category,
        year,
        ...(session ? { session } : {}),
        per_page: 100,
      }),
    ])
      .then(([examData, paperData]) => {
        setExam(examData)
        setPapers(paperData.papers || [])
      })
      .catch(() => setError('Failed to load papers.'))
      .finally(() => setLoading(false))
  }, [slug, category, year, session])

  const categoryObj  = exam?.categories?.find(c => c.slug === category)
  const categoryName = categoryObj?.name || category

  useSEO({
    title: exam ? `${exam.name} ${categoryName} ${year} Papers — ExamVault` : 'ExamVault',
    description: exam
      ? `Download ${exam.name} ${categoryName} previous year question papers from ${year}.`
      : '',
  })

  const accentColor = exam?.accent_color_hex || '#8FB9A8'

  // Extract distinct subjects available among these papers
  const availableSubjects = Array.from(new Set(
    papers.flatMap(p => (p.subjects || []).map(s => typeof s === 'object' ? s.name : s))
  )).filter(Boolean).sort()

  const originalCount = papers.filter(p => p.paper_type === 'original').length
  const sampleCount = papers.filter(p => p.paper_type === 'sample').length
  const withKeyCount = papers.filter(p => p.has_answer_key).length

  const displayedPapers = papers.filter(p => {
    const matchesSubject = !selectedSubject || (p.subjects || []).some(s =>
      (typeof s === 'object' ? s.name : s).toLowerCase() === selectedSubject.toLowerCase()
    )
    const matchesType = selectedType === 'all'
      ? true
      : selectedType === 'key'
        ? p.has_answer_key
        : p.paper_type === selectedType
    return matchesSubject && matchesType
  })

  // Human-readable heading label
  const headingLabel = session
    ? `${categoryName} ${year} — ${session}`
    : `${categoryName} ${year}`

  return (
    <div className="page-content" data-exam={slug}>
      <div className="container">

        {/* Breadcrumb */}
        <motion.div
          style={{ display: 'flex', gap: 8, alignItems: 'center', marginBottom: 'var(--space-5)', fontSize: '0.8125rem', color: 'var(--text-muted)', flexWrap: 'wrap' }}
          initial={reduced ? false : { opacity: 0, x: -10 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ duration: 0.3 }}
        >
          <Link to="/" style={{ color: 'var(--text-muted)', textDecoration: 'none' }}>Home</Link>
          <span>›</span>
          <Link to={`/exam/${slug}`} style={{ color: 'var(--text-muted)', textDecoration: 'none' }}>
            {exam?.name || slug.toUpperCase()}
          </Link>
          <span>›</span>
          <Link to={`/exam/${slug}/${category}`} style={{ color: 'var(--text-muted)', textDecoration: 'none' }}>
            {categoryName}
          </Link>
          <span>›</span>
          <span className="mono" style={{ color: 'var(--text-primary)', fontWeight: 500 }}>
            {year}{session ? ` — ${session}` : ''}
          </span>
        </motion.div>

        {/* Header */}
        <div className="page-header">
          <motion.div
            className="page-header-eyebrow"
            style={{ color: accentColor }}
            initial={reduced ? false : { opacity: 0, y: 8 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.35 }}
          >
            {exam?.name}
          </motion.div>
          <motion.h1
            initial={reduced ? false : { opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.38, delay: 0.06 }}
          >
            {headingLabel} Question Papers
          </motion.h1>
          {!loading && !error && (
            <motion.p
              style={{ marginTop: 8, color: 'var(--text-secondary)' }}
              initial={reduced ? false : { opacity: 0 }}
              animate={{ opacity: 1 }}
              transition={{ duration: 0.4, delay: 0.14 }}
            >
              {papers.length} paper{papers.length !== 1 ? 's' : ''} found
            </motion.p>
          )}
        </div>

        {/* Loading */}
        {loading && <PageSkeleton count={6} />}

        {/* Error */}
        {error && (
          <div className="empty-state">
            <div className="empty-state-icon">⚠️</div>
            <h3>Failed to load papers</h3>
            <p>{error}</p>
          </div>
        )}

        {/* Empty */}
        {!loading && !error && papers.length === 0 && (
          <div className="empty-state">
            <div className="empty-state-icon">📭</div>
            <h3>No papers yet</h3>
            <p>No question papers have been added for {headingLabel}.</p>
            <Link to={`/exam/${slug}/${category}`} className="btn btn-primary">
              ← Browse other years
            </Link>
          </div>
        )}

        {/* ── Paper Type Segregation Tabs (Original vs Sample) ── */}
        {!loading && !error && (originalCount > 0 && sampleCount > 0) && (
          <div style={{ marginBottom: 16, display: 'flex', alignItems: 'center', gap: 10, flexWrap: 'wrap' }}>
            <span style={{ fontSize: '0.8125rem', color: 'var(--text-muted)', fontWeight: 600 }}>Paper Classification:</span>
            <div className="filter-chips">
              <button
                className={`filter-chip ${selectedType === 'all' ? 'active' : ''}`}
                onClick={() => setSelectedType('all')}
              >
                All Papers ({papers.length})
              </button>
              <button
                className={`filter-chip ${selectedType === 'original' ? 'active' : ''}`}
                onClick={() => setSelectedType('original')}
                style={selectedType === 'original' ? { backgroundColor: 'rgba(16, 185, 129, 0.15)', borderColor: '#10B981', color: '#10B981' } : {}}
              >
                ✓ Original Exam Papers ({originalCount})
              </button>
              <button
                className={`filter-chip ${selectedType === 'sample' ? 'active' : ''}`}
                onClick={() => setSelectedType('sample')}
                style={selectedType === 'sample' ? { backgroundColor: 'rgba(139, 92, 246, 0.15)', borderColor: '#8B5CF6', color: '#8B5CF6' } : {}}
              >
                📝 Official Sample Papers ({sampleCount})
              </button>
              {withKeyCount > 0 && (
                <button
                  className={`filter-chip ${selectedType === 'key' ? 'active' : ''}`}
                  onClick={() => setSelectedType(selectedType === 'key' ? 'all' : 'key')}
                  style={selectedType === 'key' ? { backgroundColor: 'rgba(16, 185, 129, 0.15)', borderColor: '#10B981', color: '#10B981' } : {}}
                >
                  🔑 With Answer Key ({withKeyCount})
                </button>
              )}
            </div>
          </div>
        )}

        {/* ── Subject Filter Bar (when multiple subjects present) ── */}
        {!loading && !error && availableSubjects.length > 1 && (
          <div style={{ marginBottom: 'var(--space-6)', display: 'flex', alignItems: 'center', gap: 10, flexWrap: 'wrap' }}>
            <span style={{ fontSize: '0.8125rem', color: 'var(--text-muted)', fontWeight: 600 }}>Filter by Subject:</span>
            <div className="filter-chips">
              <button
                className={`filter-chip ${!selectedSubject ? 'active' : ''}`}
                onClick={() => setSelectedSubject('')}
              >
                All Subjects ({papers.length})
              </button>
              {availableSubjects.map((subName) => {
                const count = papers.filter(p => (p.subjects || []).some(s => (typeof s === 'object' ? s.name : s).toLowerCase() === subName.toLowerCase())).length
                return (
                  <button
                    key={subName}
                    className={`filter-chip ${selectedSubject === subName ? 'active' : ''}`}
                    onClick={() => setSelectedSubject(selectedSubject === subName ? '' : subName)}
                  >
                    {subName} ({count})
                  </button>
                )
              })}
            </div>
          </div>
        )}

        {/* ── Flip Card Grid ── */}
        {!loading && displayedPapers.length > 0 && (
          <>
            {reduced ? (
              <div className="papers-list">
                {displayedPapers.map(paper => (
                  <FlipCard key={paper.id} paper={paper} accentColor={accentColor} />
                ))}
              </div>
            ) : (
              <ScrollReveal className="flip-card-grid" stagger={0.055} y={24}>
                {displayedPapers.map(paper => (
                  <FlipCard key={paper.id} paper={paper} accentColor={accentColor} />
                ))}
              </ScrollReveal>
            )}
          </>
        )}

        {!loading && papers.length > 0 && displayedPapers.length === 0 && (
          <div className="empty-state">
            <div className="empty-state-icon">🔍</div>
            <h3>No papers found for {selectedSubject}</h3>
            <button className="btn btn-primary" onClick={() => setSelectedSubject('')}>
              Show All Subjects
            </button>
          </div>
        )}

      </div>
    </div>
  )
}
