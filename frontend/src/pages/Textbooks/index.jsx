/**
 * Textbooks browse and reader hub — Classes 1 to 12 (NCERT & State Boards).
 * Route: /textbooks
 */
import { useEffect, useState, useCallback } from 'react'
import { Link, useSearchParams } from 'react-router-dom'
import { fetchTextbooks, fetchTextbookStandards } from '../../api/client'
import { PageSkeleton } from '../../components/ui/Skeleton'
import { useDebounce } from '../../hooks/useDebounce'
import { useSEO } from '../../hooks/useSEO'

const STANDARDS = [
  'All Classes',
  'Class 12',
  'Class 11',
  'Class 10',
  'Class 9',
  'Class 8',
  'Class 7',
  'Class 6',
  'Class 5',
  'Class 4',
  'Class 3',
  'Class 2',
  'Class 1',
]

const BOARDS = [
  { label: 'All Boards', value: '' },
  { label: 'CBSE / NCERT', value: 'CBSE' },
  { label: 'Tamil Nadu State Board', value: 'Tamil Nadu' },
  { label: 'ICSE / CISCE', value: 'ICSE' },
]

export default function TextbooksPage() {
  const [searchParams, setSearchParams] = useSearchParams()
  const initialStandard = searchParams.get('standard') || ''
  const initialBoard    = searchParams.get('board')    || ''
  const initialSubject  = searchParams.get('subject')  || ''
  const initialQ        = searchParams.get('q')        || ''

  const [standard, setStandard]   = useState(initialStandard)
  const [board, setBoard]         = useState(initialBoard)
  const [subject, setSubject]     = useState(initialSubject)
  const [search, setSearch]       = useState(initialQ)
  const [textbooks, setTextbooks] = useState([])
  const [standardsMeta, setStandardsMeta] = useState([])
  const [subjectsMeta, setSubjectsMeta]   = useState([])
  const [loading, setLoading]     = useState(true)
  const [total, setTotal]         = useState(0)
  const [activePreview, setActivePreview] = useState(null)

  const debouncedSearch = useDebounce(search, 350)

  useSEO({
    title: 'Textbooks (Class 1 to 12) — NCERT & State Board Books | ExamVault',
    description: 'Read and download official NCERT and Tamil Nadu Samacheer Kalvi textbooks from Class 1 to Class 12 for Mathematics, Science, Physics, Chemistry, Biology, and Social Sciences.',
  })

  // Load available standards and subjects metadata
  useEffect(() => {
    fetchTextbookStandards()
      .then(data => {
        setStandardsMeta(data.standards || [])
        setSubjectsMeta(data.subjects || [])
      })
      .catch(() => {})
  }, [])

  const loadBooks = useCallback(async (std, brd, subj, q) => {
    setLoading(true)
    try {
      const params = { per_page: 50 }
      if (std && std !== 'All Classes') params.standard = std
      if (brd) params.board = brd
      if (subj) params.subject = subj
      if (q) params.search = q
      const res = await fetchTextbooks(params)
      setTextbooks(res.textbooks || [])
      setTotal(res.pagination?.total || 0)
    } catch {
      setTextbooks([])
    } finally {
      setLoading(false)
    }
  }, [])

  useEffect(() => {
    loadBooks(standard, board, subject, debouncedSearch)
    setSearchParams({
      ...(standard && standard !== 'All Classes' ? { standard } : {}),
      ...(board ? { board } : {}),
      ...(subject ? { subject } : {}),
      ...(debouncedSearch ? { q: debouncedSearch } : {}),
    })
  }, [standard, board, subject, debouncedSearch, loadBooks, setSearchParams])

  return (
    <div className="page-content">
      <div className="container" style={{ maxWidth: 1100 }}>

        {/* Page Header */}
        <div style={{ marginBottom: 'var(--space-6)' }}>
          <div className="section-label" style={{ color: '#10B981', display: 'flex', alignItems: 'center', gap: 6 }}>
            <span>📚</span>
            <span>Digital Curriculum Library</span>
          </div>
          <h1 style={{ fontSize: 'clamp(1.5rem, 3vw, 2.25rem)', marginBottom: 8, color: 'var(--text-primary)' }}>
            Official Standard Textbooks (Classes 1 to 12)
          </h1>
          <p style={{ color: 'var(--text-secondary)', maxWidth: 750, fontSize: '0.9375rem', lineHeight: 1.5 }}>
            Verified, authentic textbooks from NCERT and State Educational Boards. Read online with integrated dual-view or download for offline study alongside question papers and marking schemes.
          </p>
        </div>

        {/* ── Search & Filter Panel ── */}
        <div style={{
          backgroundColor: 'var(--surface)',
          padding: '20px 24px',
          borderRadius: '16px',
          border: '1px solid var(--color-border)',
          marginBottom: 'var(--space-6)',
          display: 'flex',
          flexDirection: 'column',
          gap: 16
        }}>
          {/* Keyword Search */}
          <div style={{ display: 'flex', gap: 10, alignItems: 'center' }}>
            <span style={{ fontSize: '1.25rem' }}>🔍</span>
            <input
              type="text"
              placeholder="Search textbook title, author, or topic (e.g. Mathematics, Organic Chemistry, Economics)..."
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              className="search-input"
              style={{ flex: 1, height: 42, fontSize: '0.875rem' }}
            />
            {(search || standard || board || subject) && (
              <button
                className="btn btn-ghost btn-sm"
                onClick={() => {
                  setSearch('')
                  setStandard('')
                  setBoard('')
                  setSubject('')
                }}
              >
                Clear Filters ✕
              </button>
            )}
          </div>

          {/* Standards Filter Chips */}
          <div>
            <div className="section-label" style={{ marginBottom: 8, fontSize: '0.75rem' }}>Select Class / Standard:</div>
            <div className="filter-chips">
              {STANDARDS.map((s) => {
                const isActive = (s === 'All Classes' && !standard) || standard === s
                return (
                  <button
                    key={s}
                    className={`filter-chip ${isActive ? 'active' : ''}`}
                    onClick={() => setStandard(s === 'All Classes' ? '' : s)}
                  >
                    {s}
                  </button>
                )
              })}
            </div>
          </div>

          {/* Board Filter */}
          <div style={{ display: 'flex', gap: 20, flexWrap: 'wrap', alignItems: 'center' }}>
            <div style={{ display: 'flex', gap: 8, alignItems: 'center' }}>
              <span style={{ fontSize: '0.8125rem', color: 'var(--text-muted)', fontWeight: 600 }}>Education Board:</span>
              <div className="filter-chips">
                {BOARDS.map((b) => (
                  <button
                    key={b.label}
                    className={`filter-chip ${board === b.value ? 'active' : ''}`}
                    onClick={() => setBoard(b.value)}
                  >
                    {b.label}
                  </button>
                ))}
              </div>
            </div>

            {/* Subject Filter (Quick Chips) */}
            {subjectsMeta.length > 0 && (
              <div style={{ display: 'flex', gap: 8, alignItems: 'center', flexWrap: 'wrap' }}>
                <span style={{ fontSize: '0.8125rem', color: 'var(--text-muted)', fontWeight: 600 }}>Subject:</span>
                <div className="filter-chips">
                  <button
                    className={`filter-chip ${!subject ? 'active' : ''}`}
                    onClick={() => setSubject('')}
                  >
                    All
                  </button>
                  {subjectsMeta.slice(0, 6).map((sub) => (
                    <button
                      key={sub.subject_name}
                      className={`filter-chip ${subject === sub.subject_name ? 'active' : ''}`}
                      onClick={() => setSubject(subject === sub.subject_name ? '' : sub.subject_name)}
                    >
                      {sub.subject_name}
                    </button>
                  ))}
                </div>
              </div>
            )}
          </div>
        </div>

        {/* ── Active Inline Textbook Reader (When opened) ── */}
        {activePreview && (
          <div style={{
            marginBottom: 'var(--space-8)',
            backgroundColor: '#fff',
            borderRadius: '16px',
            border: '2px solid #10B981',
            overflow: 'hidden',
            boxShadow: 'var(--shadow-lg)'
          }}>
            <div style={{
              display: 'flex',
              justifyContent: 'space-between',
              alignItems: 'center',
              padding: '12px 18px',
              backgroundColor: '#f0fdf4',
              borderBottom: '1px solid #bbf7d0',
              flexWrap: 'wrap',
              gap: 10
            }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
                <span style={{ fontSize: '1.25rem' }}>📖</span>
                <div>
                  <strong style={{ fontSize: '0.9375rem', color: '#166534' }}>{activePreview.title}</strong>
                  <div style={{ fontSize: '0.75rem', color: '#15803d' }}>
                    {activePreview.standard_level} · {activePreview.board} · {activePreview.language}
                  </div>
                </div>
              </div>

              <div style={{ display: 'flex', gap: 8, alignItems: 'center' }}>
                <a
                  href={activePreview.pdf_url}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="btn btn-primary btn-sm"
                  download
                >
                  📥 Download PDF
                </a>
                <button
                  className="btn btn-ghost btn-sm"
                  onClick={() => setActivePreview(null)}
                >
                  ✕ Close Reader
                </button>
              </div>
            </div>

            <div style={{ height: '750px', backgroundColor: '#525659' }}>
              <iframe
                src={`${activePreview.pdf_url}#toolbar=1`}
                title={activePreview.title}
                width="100%"
                height="100%"
                style={{ border: 'none', display: 'block' }}
              />
            </div>
          </div>
        )}

        {/* ── Results Count ── */}
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 16 }}>
          <div className="section-label" style={{ fontSize: '0.8125rem' }}>
            {total} official textbook{total !== 1 ? 's' : ''} available
            {standard ? ` for ${standard}` : ''}
            {board ? ` under ${board}` : ''}
            {subject ? ` (${subject})` : ''}
          </div>
        </div>

        {/* ── Textbooks Grid ── */}
        {loading ? (
          <PageSkeleton count={6} />
        ) : textbooks.length === 0 ? (
          <div className="empty-state">
            <div className="empty-state-icon">📚</div>
            <h3>No textbooks match your filter</h3>
            <p style={{ color: 'var(--text-muted)' }}>Try selecting another class level or clearing active keyword filters.</p>
            <button className="btn btn-primary" onClick={() => { setStandard(''); setBoard(''); setSubject(''); setSearch(''); }}>
              Show All Textbooks
            </button>
          </div>
        ) : (
          <div style={{
            display: 'grid',
            gridTemplateColumns: 'repeat(auto-fill, minmax(320px, 1fr))',
            gap: 'var(--space-4)',
            marginBottom: 'var(--space-12)'
          }}>
            {textbooks.map((book) => (
              <div
                key={book.id}
                style={{
                  backgroundColor: 'var(--surface)',
                  borderRadius: '14px',
                  border: '1px solid var(--color-border)',
                  padding: '20px',
                  display: 'flex',
                  flexDirection: 'column',
                  justifyContent: 'space-between',
                  boxShadow: 'var(--shadow-sm)',
                  transition: 'transform 0.2s ease, box-shadow 0.2s ease',
                }}
              >
                <div>
                  {/* Standard & Board Pills */}
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 10, flexWrap: 'wrap', gap: 6 }}>
                    <span style={{
                      backgroundColor: 'rgba(16, 185, 129, 0.12)',
                      color: '#10B981',
                      border: '1px solid rgba(16, 185, 129, 0.25)',
                      padding: '3px 8px',
                      borderRadius: '6px',
                      fontSize: '0.75rem',
                      fontWeight: 700
                    }}>
                      {book.standard_level}
                    </span>
                    <span style={{
                      fontSize: '0.72rem',
                      color: 'var(--text-muted)',
                      backgroundColor: 'rgba(0,0,0,0.03)',
                      padding: '2px 7px',
                      borderRadius: '4px'
                    }}>
                      {book.board}
                    </span>
                  </div>

                  {/* Title */}
                  <h3 style={{ fontSize: '1rem', fontWeight: 700, lineHeight: 1.35, marginBottom: 8, color: 'var(--text-primary)' }}>
                    {book.title}
                  </h3>

                  {/* Subject Tag */}
                  <div style={{ display: 'flex', gap: 6, alignItems: 'center', marginBottom: 16 }}>
                    <span className="badge" style={{ backgroundColor: 'rgba(0,0,0,0.05)', fontSize: '0.75rem' }}>
                      🏷️ {book.subject_name}
                    </span>
                    <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>
                      • {book.language} Medium
                    </span>
                  </div>

                  {/* Official Source Info */}
                  {book.source_name && (
                    <div style={{ fontSize: '0.72rem', color: 'var(--text-muted)', marginBottom: 16, display: 'flex', alignItems: 'center', gap: 6 }}>
                      <span>🏛️</span>
                      <span>{book.source_name}</span>
                    </div>
                  )}
                </div>

                {/* Actions: In-platform Read + Download + Linked Question Papers */}
                <div style={{ display: 'flex', gap: 8, paddingTop: 12, borderTop: '1px solid var(--color-border)', flexWrap: 'wrap' }}>
                  <button
                    className="btn btn-primary btn-sm"
                    style={{ flex: 1, padding: '7px 12px', fontSize: '0.8125rem' }}
                    onClick={() => {
                      setActivePreview(book)
                      window.scrollTo({ top: 220, behavior: 'smooth' })
                    }}
                  >
                    📖 Read Book
                  </button>

                  <a
                    href={book.pdf_url}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="btn btn-ghost btn-sm"
                    style={{ padding: '7px 10px', fontSize: '0.8125rem' }}
                    download
                    title="Download textbook PDF"
                  >
                    📥 PDF
                  </a>

                  {/* Quick link to past question papers for this subject & class */}
                  <Link
                    to={`/search?subject=${encodeURIComponent(book.subject_name)}`}
                    className="btn btn-ghost btn-sm"
                    style={{ padding: '7px 10px', fontSize: '0.8125rem', color: '#6366F1' }}
                    title={`View past question papers for ${book.subject_name}`}
                  >
                    📑 PYQs →
                  </Link>
                </div>
              </div>
            ))}
          </div>
        )}

      </div>
    </div>
  )
}
