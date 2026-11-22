/**
 * Home page — "The Archive Cabinet" landing.
 *
 * Animation layers:
 *  1. Three.js hero cabinet (lazy-loaded, prefers-reduced-motion skips it)
 *  2. Framer Motion stagger entrance for the exam cards below
 *  3. Static fallback card grid for reduced-motion users
 */
import { useEffect, useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { motion } from 'framer-motion'
import { fetchExams } from '../../api/client'
import { useAuthStore, useToastStore } from '../../store'
import { ExamCardSkeleton } from '../../components/ui/Skeleton'
import { useReducedMotion } from '../../hooks/useReducedMotion'
import { useSEO } from '../../hooks/useSEO'
import ExamHero from '../../components/hero/ExamHero'

// ── Exam card Framer Motion variants ─────────────────────────
const cardContainer = {
  hidden: {},
  visible: { transition: { staggerChildren: 0.09, delayChildren: 0.1 } },
}
const cardItem = {
  hidden:  { opacity: 0, y: 24, scale: 0.97 },
  visible: { opacity: 1, y: 0,  scale: 1, transition: { type: 'spring', stiffness: 260, damping: 24 } },
}

const EXAM_META = {
  tnpsc: { emoji: '📋', label: 'State Civil Services' },
  upsc:  { emoji: '🏛️', label: 'Civil Services & Defence (NDA/CDS/CAPF)'  },
  jee:   { emoji: '⚗️', label: 'Engineering Entrance'  },
  neet:  { emoji: '🩺', label: 'Medical Entrance'      },
  'class-10': { emoji: '📘', label: '10th Secondary Board' },
  'class-12': { emoji: '🎓', label: '12th Higher Secondary Board' },
  'state-boards': { emoji: '🗺️', label: '11+ State Secondary Boards' },
}

// ── Component ─────────────────────────────────────────────────
export default function HomePage() {
  const navigate = useNavigate()
  const { user } = useAuthStore()
  const { addToast } = useToastStore()
  const reduced = useReducedMotion()
  const [exams, setExams]     = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError]     = useState(null)

  useSEO({
    title: 'ExamVault — Previous Year Question Papers | TNPSC UPSC JEE NEET',
    description: 'Download previous year question papers for TNPSC, UPSC, JEE, and NEET. Organized by exam, category, and year.',
    schema: {
      '@context': 'https://schema.org',
      '@type': 'WebSite',
      name: 'ExamVault',
      url: 'https://examvault.in',
      description: 'Searchable previous year question papers for TNPSC, UPSC, JEE, and NEET.'
    }
  })

  useEffect(() => {
    fetchExams()
      .then(setExams)
      .catch(() => setError('Failed to load exams. Is the backend running?'))
      .finally(() => setLoading(false))
  }, [])

  const handleSearchClick = (e) => {
    if (!user) {
      e.preventDefault()
      addToast('Please sign in or register to search question papers.', 'info')
      navigate('/login')
    }
  }

  const handleBrowseClick = (e) => {
    if (!user) {
      e.preventDefault()
      addToast('Please sign in or register to browse exam papers.', 'info')
      navigate('/login')
    }
  }

  const handleCardClick = (e, slug) => {
    if (!user) {
      e.preventDefault()
      addToast('Please sign in or register to access question papers.', 'info')
      navigate('/login')
    }
  }

  return (
    <main>
      {/* ── ExamVault Hero Section (Archive Cabinet Card-Cycle) ──── */}
      <ExamHero />

      {/* ── Exam Cards ────────────────────────────────────────── */}
      <section id="exams" className="container" style={{ paddingBottom: 'var(--space-16)' }}>
        <div className="section-label">All exams</div>

        {loading && (
          <div className="exams-grid">
            {[1, 2, 3, 4].map(i => <ExamCardSkeleton key={i} />)}
          </div>
        )}

        {error && (
          <div className="empty-state">
            <div className="empty-state-icon">⚠️</div>
            <h3>Could not load exams</h3>
            <p>{error}</p>
            <button className="btn btn-ghost" onClick={() => window.location.reload()}>Retry</button>
          </div>
        )}

        {!loading && !error && (
          <motion.div
            className="exams-grid"
            variants={reduced ? {} : cardContainer}
            initial={reduced ? false : 'hidden'}
            whileInView={reduced ? false : 'visible'}
            viewport={{ once: true, amount: 0.2 }}
          >
            {exams.map((exam) => {
              const meta = EXAM_META[exam.slug] || {}
              return (
                <motion.div
                  key={exam.id}
                  variants={reduced ? {} : cardItem}
                >
                  <Link
                    to={`/exam/${exam.slug}`}
                    onClick={(e) => handleCardClick(e, exam.slug)}
                    className="exam-card"
                    data-exam={exam.slug}
                    style={{ '--exam-accent': exam.accent_color_hex, display: 'flex', flexDirection: 'column' }}
                  >
                    <div className="exam-card-icon">{meta.emoji || '📄'}</div>
                    <div className="exam-card-name">{exam.name}</div>
                    <h2 className="exam-card-title">{meta.label}</h2>
                    <p className="exam-card-desc">{exam.description}</p>
                    <div className="exam-card-meta" style={{ marginTop: 'auto' }}>
                      <span className="exam-card-meta-item mono">Browse Archive →</span>
                    </div>
                  </Link>
                </motion.div>
              )
            })}
          </motion.div>
        )}
      </section>

      {/* ── Curriculum Textbooks Feature Section (Classes 1 - 12) ── */}
      <section className="container" style={{ paddingBottom: 'var(--space-12)' }}>
        <div style={{
          background: 'linear-gradient(135deg, rgba(59, 130, 246, 0.08) 0%, rgba(99, 102, 241, 0.05) 100%)',
          border: '1px solid rgba(59, 130, 246, 0.25)',
          borderRadius: '20px',
          padding: '30px 32px',
          display: 'flex',
          flexDirection: 'column',
          gap: 20
        }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', flexWrap: 'wrap', gap: 16 }}>
            <div>
              <div style={{ display: 'flex', alignItems: 'center', gap: 8, marginBottom: 6 }}>
                <span style={{ fontSize: '1.25rem' }}>📚</span>
                <span className="section-label" style={{ margin: 0, color: '#2563EB' }}>
                  Curriculum Textbooks (Class 1 to 12)
                </span>
              </div>
              <h2 style={{ fontSize: 'clamp(1.25rem, 2.5vw, 1.75rem)', fontWeight: 700, margin: 0 }}>
                Standard Board Textbooks & Syllabus
              </h2>
              <p style={{ color: 'var(--text-secondary)', fontSize: '0.875rem', marginTop: 6, maxWidth: 650 }}>
                Access verified NCERT, CBSE, and State Board (Tamil Nadu DGE) prescribed textbooks co-located with previous year question papers and solutions.
              </p>
            </div>
            <Link
              to="/textbooks"
              className="btn btn-primary"
              style={{ backgroundColor: '#2563EB', borderColor: '#2563EB', fontWeight: 600, padding: '10px 22px' }}
            >
              Browse All Textbooks →
            </Link>
          </div>

          <div style={{
            display: 'grid',
            gridTemplateColumns: 'repeat(auto-fit, minmax(140px, 1fr))',
            gap: 12
          }}>
            {[
              { std: 'Class 12', label: 'Higher Secondary', count: '10+ Books', icon: '🎓' },
              { std: 'Class 11', label: 'Senior Secondary', count: '6+ Books', icon: '📖' },
              { std: 'Class 10', label: 'Secondary SSLC', count: '12+ Books', icon: '📘' },
              { std: 'Class 9',  label: 'High School', count: '8+ Books', icon: '📗' },
              { std: 'Class 8',  label: 'Middle School', count: '6+ Books', icon: '📙' },
              { std: 'Class 1-7', label: 'Primary & Middle', count: 'NCERT Series', icon: '🎒' },
            ].map(({ std, label, count, icon }) => (
              <Link
                key={std}
                to={`/textbooks?standard=${encodeURIComponent(std)}`}
                style={{
                  background: '#ffffff',
                  border: '1px solid var(--color-border)',
                  borderRadius: '12px',
                  padding: '16px 14px',
                  textDecoration: 'none',
                  display: 'flex',
                  flexDirection: 'column',
                  gap: 4,
                  boxShadow: 'var(--shadow-sm)',
                  transition: 'transform 0.2s ease, box-shadow 0.2s ease'
                }}
              >
                <div style={{ fontSize: '1.4rem' }}>{icon}</div>
                <div style={{ fontWeight: 700, fontSize: '0.9375rem', color: 'var(--text-primary)' }}>{std}</div>
                <div style={{ fontSize: '0.72rem', color: 'var(--text-muted)' }}>{label}</div>
                <div style={{ fontSize: '0.7rem', fontWeight: 600, color: '#2563EB', marginTop: 'auto' }}>{count}</div>
              </Link>
            ))}
          </div>
        </div>
      </section>

      {/* ── Subject-Wise Question Papers Section ────────────── */}
      <section className="container" style={{ paddingBottom: 'var(--space-12)' }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-end', marginBottom: 'var(--space-6)', flexWrap: 'wrap', gap: 12 }}>
          <div>
            <div className="section-label">Subject Segregation</div>
            <h2 style={{ fontSize: 'clamp(1.25rem, 2.5vw, 1.75rem)', fontWeight: 700 }}>Browse Papers by Subject</h2>
            <p style={{ color: 'var(--text-secondary)', fontSize: '0.875rem', marginTop: 4 }}>
              Jump straight to authentic past papers across all examinations for your core subjects.
            </p>
          </div>
          <Link to="/search" className="btn btn-ghost btn-sm" style={{ color: 'var(--color-primary)' }}>
            All Subjects Search →
          </Link>
        </div>

        <div style={{
          display: 'grid',
          gridTemplateColumns: 'repeat(auto-fill, minmax(170px, 1fr))',
          gap: 'var(--space-3)',
        }}>
          {[
            { name: 'Mathematics', icon: '📐', desc: 'Class 10, 12 & JEE' },
            { name: 'Physics',     icon: '⚛️', desc: 'Class 12, JEE & NEET' },
            { name: 'Chemistry',   icon: '🧪', desc: 'Class 12, JEE & NEET' },
            { name: 'Biology',     icon: '🧬', desc: 'Class 12 & NEET UG' },
            { name: 'General Studies', icon: '🌍', desc: 'UPSC & TNPSC' },
            { name: 'CSAT',        icon: '🧠', desc: 'UPSC Prelims & Aptitude' },
            { name: 'Science',     icon: '🔬', desc: 'Class 10 Board Exams' },
            { name: 'Social Science', icon: '🌐', desc: 'Class 10 Board Exams' },
            { name: 'Economics',   icon: '📈', desc: 'Class 12 & TN HSC' },
            { name: 'Accountancy', icon: '📊', desc: 'Class 12 & TN HSC' },
            { name: 'General Tamil', icon: '✍️', desc: 'TNPSC & TN SSLC' },
            { name: 'English',     icon: '📖', desc: 'Class 10, 12 & TNPSC' },
          ].map(({ name, icon, desc }) => (
            <Link
              key={name}
              to={`/search?subject=${encodeURIComponent(name)}`}
              className="category-card"
              style={{
                padding: '16px',
                borderRadius: '12px',
                textDecoration: 'none',
                display: 'flex',
                flexDirection: 'column',
                gap: 6,
                backgroundColor: 'rgba(255,255,255,0.02)',
                border: '1px solid var(--color-border)',
                transition: 'all 0.2s ease',
              }}
            >
              <div style={{ fontSize: '1.5rem', marginBottom: 2 }}>{icon}</div>
              <div style={{ fontWeight: 700, fontSize: '0.9375rem', color: 'var(--text-primary)' }}>{name}</div>
              <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>{desc}</div>
            </Link>
          ))}
        </div>
      </section>

      {/* ── Stats strip ───────────────────────────────────────── */}
      <section style={{
        background: 'var(--color-bg-raised)',
        borderTop: '1px solid var(--color-border)',
        borderBottom: '1px solid var(--color-border)',
        padding: 'var(--space-8) 0',
      }}>
        <div className="container">
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(160px, 1fr))', gap: 'var(--space-6)', textAlign: 'center' }}>
            {[
              { val: '6',        label: 'Exams Covered'     },
              { val: '160+',     label: 'Question Papers'   },
              { val: '3,800+',   label: 'Total Pages'       },
              { val: '100%',     label: 'Verified Archive'  },
            ].map(({ val, label }) => (
              <div key={label}>
                <div className="mono" style={{ fontSize: '1.75rem', fontWeight: 600, color: 'var(--text-primary)', marginBottom: 4 }}>{val}</div>
                <div style={{ fontSize: '0.8125rem', color: 'var(--text-muted)', textTransform: 'uppercase', letterSpacing: '0.08em' }}>{label}</div>
              </div>
            ))}
          </div>
        </div>
      </section>
    </main>
  )
}
