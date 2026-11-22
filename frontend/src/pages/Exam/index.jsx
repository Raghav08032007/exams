/**
 * Exam page — category cards + "Official Website" card + Subject-wise segregation.
 * Route: /exam/:slug
 */
import { useEffect, useState } from 'react'
import { useParams, Link, useNavigate } from 'react-router-dom'
import { motion } from 'framer-motion'
import { fetchExam, fetchSubjects } from '../../api/client'
import { useAuthStore, useToastStore } from '../../store'
import { useReducedMotion } from '../../hooks/useReducedMotion'
import { useSEO } from '../../hooks/useSEO'
import { useTilt } from '../../hooks/useTilt'

// ── Animation variants ───────────────────────────────────────────────────────
const gridContainer = {
  hidden: {},
  visible: { transition: { staggerChildren: 0.08, delayChildren: 0.05 } },
}
const gridItem = {
  hidden:  { opacity: 0, y: 20, scale: 0.96 },
  visible: { opacity: 1, y: 0,  scale: 1, transition: { type: 'spring', stiffness: 300, damping: 26 } },
}

// Category icon map
const CATEGORY_ICONS = {
  'group-1':              '📜',
  'group-2a':             '📋',
  'group-2':              '📋',
  'group-4':              '📄',
  'vao':                  '🏘️',
  'prelims':              '📝',
  'mains':                '📚',
  'nda':                  '🎖️',
  'cds':                  '🛡️',
  'capf':                 '👮',
  'ifs':                  '🌲',
  'engineering-services': '⚙️',
  'cms':                  '🩺',
  'jee-main':             '🔬',
  'jee-advanced':         '⚗️',
  'neet-ug':              '🩺',
  'cbse-10':              '📘',
  'tn-sslc':              '🏫',
  'cbse-12':              '🎓',
  'tn-hsc':               '🏛️',
  'ap-board':             '🌴',
  'bihar-board':          '🏛️',
  'kerala-board':         '🥥',
  'mp-board':             '🌾',
  'maharashtra-board':    '🌊',
  'rajasthan-board':      '🏰',
  'tn-board':             '🛕',
  'telangana-board':      '💎',
  'up-board':             '🚩',
  'wb-board':             '🐅',
  'icse-board':           '🎓',
}

// Subject icon map
const SUBJECT_ICONS = {
  'Mathematics':     '📐',
  'Physics':         '⚛️',
  'Chemistry':       '🧪',
  'Biology':         '🧬',
  'General Studies': '🌍',
  'History':         '🏛️',
  'Geography':       '🗺️',
  'Polity':          '⚖️',
  'Economy':         '📈',
  'Economics':       '📊',
  'Social Science':  '🌐',
  'Science':         '🔬',
  'Computer Science':'💻',
  'English':         '📖',
  'Tamil':           '✍️',
  'General Tamil':   '✍️',
  'General English': '📖',
  'CSAT':            '🧠',
  'Aptitude':        '🧩',
  'Ethics':          '⚖️',
  'Essay':           '📝',
  'Accountancy':     '📑',
  'Environment':     '🌿',
  'Village Administration': '🏘️',
}

function getSubjectIcon(name) {
  if (!name) return '📚'
  for (const [key, icon] of Object.entries(SUBJECT_ICONS)) {
    if (name.toLowerCase().includes(key.toLowerCase())) return icon
  }
  return '📚'
}

// ── Tilt Card wrapper ────────────────────────────────────────────────────────
function TiltCard({ children, reduced, className, style, onClick }) {
  const { ref, tiltStyle } = useTilt({ max: 10, disabled: reduced })
  return (
    <div
      ref={ref}
      className={className}
      style={{ ...style, ...tiltStyle }}
      onClick={onClick}
    >
      {children}
    </div>
  )
}

// ── Official Site Card ───────────────────────────────────────────────────────
function OfficialSiteCard({ url, examName, reduced }) {
  const { ref, tiltStyle } = useTilt({ max: 8, disabled: reduced })
  if (!url) return null
  return (
    <motion.div variants={reduced ? {} : gridItem}>
      <a
        ref={ref}
        href={url}
        target="_blank"
        rel="noopener noreferrer"
        className="official-site-card"
        style={tiltStyle}
        aria-label={`Visit the official ${examName} website (opens in new tab)`}
      >
        <div className="official-site-card-icon">🌐</div>
        <div className="official-site-card-content">
          <div className="official-site-card-label">Official Website</div>
          <div className="official-site-card-name">{examName}</div>
          <div className="official-site-card-url">{url.replace(/^https?:\/\//, '')}</div>
        </div>
        <div className="official-site-card-arrow">↗</div>
      </a>
    </motion.div>
  )
}

// ── Component ────────────────────────────────────────────────────────────────
export default function ExamPage() {
  const { slug }  = useParams()
  const navigate  = useNavigate()
  const reduced   = useReducedMotion()
  const { user }  = useAuthStore()
  const { addToast } = useToastStore()

  const [exam,      setExam]      = useState(null)
  const [subjects,  setSubjects]  = useState([])
  const [activeTab, setActiveTab] = useState('categories') // 'categories' | 'subjects'
  const [loading,   setLoading]   = useState(true)
  const [error,     setError]     = useState(null)

  useEffect(() => {
    if (!user) {
      addToast('Please sign in or register to browse exam papers.', 'info')
      navigate('/login', { replace: true })
    }
  }, [user, navigate, addToast])

  useEffect(() => {
    setLoading(true)
    setError(null)
    Promise.all([
      fetchExam(slug),
      fetchSubjects({ exam: slug }),
    ])
      .then(([examData, subjsData]) => {
        setExam(examData)
        setSubjects(subjsData || [])
      })
      .catch(() => setError('Failed to load exam.'))
      .finally(() => setLoading(false))
  }, [slug])

  useSEO({
    title: exam ? `${exam.name} Question Papers — ExamVault` : 'ExamVault',
    description: exam
      ? `Download ${exam.name} previous year question papers segregated by subject and category. ${exam.description}`
      : '',
  })

  const accentColor = exam?.accent_color_hex || '#8FB9A8'

  if (loading) {
    return (
      <div className="page-content container">
        <div className="skeleton" style={{ width: '30%', height: 14, marginBottom: 12 }} />
        <div className="skeleton" style={{ width: '55%', height: 40, marginBottom: 8 }} />
        <div className="skeleton" style={{ width: '75%', height: 18, marginBottom: 36 }} />
        <div className="category-cards-grid">
          {[1, 2, 3, 4].map(i => (
            <div key={i} className="skeleton" style={{ height: 140, borderRadius: 16 }} />
          ))}
        </div>
      </div>
    )
  }

  if (error) {
    return (
      <div className="page-content container">
        <div className="empty-state">
          <div className="empty-state-icon">⚠️</div>
          <h3>Exam not found</h3>
          <p>{error}</p>
          <Link to="/" className="btn btn-primary">← Back to Home</Link>
        </div>
      </div>
    )
  }

  const categories = exam?.categories || []

  return (
    <div className="page-content" data-exam={slug}>
      <div className="container">

        {/* Breadcrumb */}
        <Link
          to="/"
          style={{ fontSize: '0.8125rem', color: 'var(--text-muted)', display: 'inline-flex', alignItems: 'center', gap: 6, marginBottom: 20, textDecoration: 'none' }}
        >
          ← All exams
        </Link>

        {/* Header */}
        <div className="page-header">
          <motion.div
            className="page-header-eyebrow"
            style={{ color: accentColor }}
            initial={reduced ? false : { opacity: 0, x: -12 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ duration: 0.4, ease: 'easeOut' }}
          >
            {exam?.name}
          </motion.div>
          <motion.h1
            style={{ marginBottom: 'var(--space-3)' }}
            initial={reduced ? false : { opacity: 0, y: 12 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.45, ease: 'easeOut', delay: 0.06 }}
          >
            {exam?.name} Question Papers
          </motion.h1>
          <motion.p
            style={{ maxWidth: 650, color: 'var(--text-secondary)' }}
            initial={reduced ? false : { opacity: 0, y: 8 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.4, ease: 'easeOut', delay: 0.1 }}
          >
            {exam?.description}
          </motion.p>
        </div>

        {/* ── Mode Switcher: Categories vs Subject-wise ── */}
        <div style={{ display: 'flex', gap: 12, marginTop: 'var(--space-6)', marginBottom: 'var(--space-6)', borderBottom: '1px solid var(--color-border)', paddingBottom: 'var(--space-4)', flexWrap: 'wrap' }}>
          <button
            className={`btn ${activeTab === 'categories' ? 'btn-primary' : 'btn-ghost'}`}
            style={{
              borderRadius: '24px',
              padding: '8px 20px',
              fontSize: '0.875rem',
              backgroundColor: activeTab === 'categories' ? accentColor : 'transparent',
              borderColor: activeTab === 'categories' ? accentColor : 'var(--color-border)',
              color: activeTab === 'categories' ? '#fff' : 'var(--text-secondary)'
            }}
            onClick={() => setActiveTab('categories')}
          >
            📁 Browse by Category ({categories.length})
          </button>
          <button
            className={`btn ${activeTab === 'subjects' ? 'btn-primary' : 'btn-ghost'}`}
            style={{
              borderRadius: '24px',
              padding: '8px 20px',
              fontSize: '0.875rem',
              backgroundColor: activeTab === 'subjects' ? accentColor : 'transparent',
              borderColor: activeTab === 'subjects' ? accentColor : 'var(--color-border)',
              color: activeTab === 'subjects' ? '#fff' : 'var(--text-secondary)'
            }}
            onClick={() => setActiveTab('subjects')}
          >
            📚 Browse by Subject ({subjects.length})
          </button>

          <Link
            to={`/search?exam=${slug}&type=original`}
            className="btn btn-ghost"
            style={{
              borderRadius: '24px',
              padding: '8px 16px',
              fontSize: '0.875rem',
              color: '#10B981',
              border: '1px solid rgba(16, 185, 129, 0.3)',
              textDecoration: 'none',
              marginLeft: 'auto'
            }}
          >
            ✓ Original Exam Papers
          </Link>
          <Link
            to={`/search?exam=${slug}&type=sample`}
            className="btn btn-ghost"
            style={{
              borderRadius: '24px',
              padding: '8px 16px',
              fontSize: '0.875rem',
              color: '#8B5CF6',
              border: '1px solid rgba(139, 92, 246, 0.3)',
              textDecoration: 'none'
            }}
          >
            📝 Official Sample Papers
          </Link>
        </div>

        {/* ── TAB 1: BROWSE BY CATEGORY ── */}
        {activeTab === 'categories' && (
          <>
            <div className="section-label" style={{ marginBottom: 16 }}>
              Select Category
            </div>
            <motion.div
              className="category-cards-grid"
              variants={reduced ? {} : gridContainer}
              initial={reduced ? false : 'hidden'}
              animate="visible"
            >
              {categories.map((cat) => {
                const icon = CATEGORY_ICONS[cat.slug] || '📂'
                return (
                  <motion.div key={cat.id} variants={reduced ? {} : gridItem}>
                    <TiltCard
                      reduced={reduced}
                      className="category-card"
                      style={{ '--exam-accent': accentColor }}
                      onClick={() => navigate(`/exam/${slug}/${cat.slug}`)}
                    >
                      <div className="category-card-icon">{icon}</div>
                      <div className="category-card-name">{cat.name}</div>
                      <div className="category-card-cta" style={{ color: accentColor }}>
                        Browse papers →
                      </div>
                    </TiltCard>
                  </motion.div>
                )
              })}

              {/* Official site card */}
              <OfficialSiteCard
                url={exam?.official_site_url}
                examName={exam?.name}
                reduced={reduced}
              />
            </motion.div>

            {/* Quick subject filter chips right below */}
            {subjects.length > 0 && (
              <div style={{ marginTop: 'var(--space-10)', padding: '20px', backgroundColor: 'rgba(255,255,255,0.03)', borderRadius: '16px', border: '1px solid var(--color-border)' }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 12 }}>
                  <div style={{ fontSize: '0.875rem', fontWeight: 600, color: 'var(--text-primary)' }}>
                    📖 Direct Subject Access in {exam?.name}
                  </div>
                  <button
                    className="btn btn-ghost btn-sm"
                    style={{ fontSize: '0.75rem', color: accentColor }}
                    onClick={() => setActiveTab('subjects')}
                  >
                    View All Subjects Grid →
                  </button>
                </div>
                <div style={{ display: 'flex', gap: 8, flexWrap: 'wrap' }}>
                  {subjects.map((sub) => (
                    <Link
                      key={sub.id}
                      to={`/search?exam=${slug}&subject=${encodeURIComponent(sub.name)}`}
                      className="filter-chip"
                      style={{ textDecoration: 'none', display: 'inline-flex', alignItems: 'center', gap: 6 }}
                    >
                      <span>{getSubjectIcon(sub.name)}</span>
                      <span>{sub.name}</span>
                      <span style={{ fontSize: '0.7rem', opacity: 0.7, background: 'rgba(0,0,0,0.1)', padding: '1px 6px', borderRadius: '10px' }}>
                        {sub.paper_count}
                      </span>
                    </Link>
                  ))}
                </div>
              </div>
            )}
          </>
        )}

        {/* ── TAB 2: BROWSE BY SUBJECT (Subject-wise segregation) ── */}
        {activeTab === 'subjects' && (
          <>
            <div className="section-label" style={{ marginBottom: 16 }}>
              Select a Subject to view all corresponding question papers
            </div>
            <motion.div
              className="category-cards-grid"
              variants={reduced ? {} : gridContainer}
              initial={reduced ? false : 'hidden'}
              animate="visible"
            >
              {subjects.map((sub) => {
                const icon = getSubjectIcon(sub.name)
                return (
                  <motion.div key={sub.id} variants={reduced ? {} : gridItem}>
                    <TiltCard
                      reduced={reduced}
                      className="category-card"
                      style={{ '--exam-accent': accentColor }}
                      onClick={() => navigate(`/search?exam=${slug}&subject=${encodeURIComponent(sub.name)}`)}
                    >
                      <div className="category-card-icon">{icon}</div>
                      <div className="category-card-name">{sub.name}</div>
                      <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)', marginBottom: 8 }}>
                        {sub.paper_count} question paper{sub.paper_count !== 1 ? 's' : ''} available
                      </div>
                      <div className="category-card-cta" style={{ color: accentColor }}>
                        View {sub.name} Papers →
                      </div>
                    </TiltCard>
                  </motion.div>
                )
              })}
            </motion.div>

            {subjects.length === 0 && (
              <div className="empty-state">
                <div className="empty-state-icon">📚</div>
                <h3>No subjects indexed yet</h3>
                <p>Papers are currently being organized into subjects for this exam.</p>
              </div>
            )}
          </>
        )}

      </div>
    </div>
  )
}
