/**
 * Search page — keyword search with exam, subject, and year filters.
 * Route: /search?q=&exam=&subject=&year=
 */
import { useEffect, useState, useCallback } from 'react'
import { Link, useSearchParams, useNavigate, useLocation } from 'react-router-dom'
import { fetchPapers, fetchSubjects } from '../../api/client'
import { useAuthStore, useToastStore } from '../../store'
import { AnswerKeyBadge, LanguageBadge, PaperTypeBadge } from '../../components/ui/Badges'
import { PageSkeleton } from '../../components/ui/Skeleton'
import { useDebounce } from '../../hooks/useDebounce'
import { useSEO } from '../../hooks/useSEO'

const EXAMS = [
  { label: 'All Exams', slug: '' },
  { label: 'Class 10', slug: 'class-10' },
  { label: 'Class 12', slug: 'class-12' },
  { label: 'JEE', slug: 'jee' },
  { label: 'NEET', slug: 'neet' },
  { label: 'TNPSC', slug: 'tnpsc' },
  { label: 'UPSC', slug: 'upsc' },
]
const YEARS = Array.from({ length: 10 }, (_, i) => 2024 - i)

export default function SearchPage() {
  const navigate = useNavigate()
  const location = useLocation()
  const { user } = useAuthStore()
  const { addToast } = useToastStore()

  useEffect(() => {
    if (!user) {
      addToast('Please sign in or register to search question papers.', 'info')
      navigate('/login', { state: { from: location }, replace: true })
    }
  }, [user, navigate, addToast, location])

  const [searchParams, setSearchParams] = useSearchParams()
  const initialQ       = searchParams.get('q')       || ''
  const initialExam    = searchParams.get('exam')    || ''
  const initialSubject = searchParams.get('subject') || ''
  const initialYear    = searchParams.get('year')    || ''
  const initialType    = searchParams.get('type')    || ''
  const initialKey     = searchParams.get('key')     || ''

  const [query, setQuery]         = useState(initialQ)
  const [exam, setExam]           = useState(initialExam)
  const [subject, setSubject]     = useState(initialSubject)
  const [year, setYear]           = useState(initialYear)
  const [paperType, setPaperType] = useState(initialType)
  const [keyFilter, setKeyFilter] = useState(initialKey)
  const [availableSubjects, setAvailableSubjects] = useState([])
  const [results, setResults]     = useState([])
  const [loading, setLoading]     = useState(false)
  const [total, setTotal]         = useState(null)
  const [searched, setSearched]   = useState(false)

  const debouncedQuery = useDebounce(query, 400)

  // Fetch subjects available for current exam selection
  useEffect(() => {
    fetchSubjects(exam ? { exam, paper_type: paperType } : { paper_type: paperType })
      .then(subjs => setAvailableSubjects(subjs || []))
      .catch(() => setAvailableSubjects([]))
  }, [exam, paperType])

  const doSearch = useCallback(async (q, e, s, y, t, k) => {
    setLoading(true)
    setSearched(true)
    try {
      const params = { per_page: 50 }
      if (q) params.search = q
      if (e) params.exam = e.toLowerCase()
      if (s) params.subject = s
      if (y) params.year = y
      if (t) params.paper_type = t
      if (k === 'with_key') params.has_answer_key = '1'
      else if (k === 'no_key') params.has_answer_key = '0'
      const data = await fetchPapers(params)
      setResults(data.papers || [])
      setTotal(data.pagination?.total ?? null)
    } catch {
      setResults([])
    } finally {
      setLoading(false)
    }
  }, [])

  useSEO({
    title: 'Search & Browse Question Papers — ExamVault',
    description: 'Search across previous year question papers for Class 10, Class 12, JEE, NEET, TNPSC, and UPSC segregated by subject and year.',
  })

  useEffect(() => {
    if (initialQ || initialExam || initialSubject || initialYear || initialType || initialKey) {
      doSearch(initialQ, initialExam, initialSubject, initialYear, initialType, initialKey)
    }
  }, []) // eslint-disable-line

  useEffect(() => {
    if (!debouncedQuery && !exam && !subject && !year && !paperType && !keyFilter) return
    doSearch(debouncedQuery, exam, subject, year, paperType, keyFilter)
    setSearchParams({
      ...(debouncedQuery ? { q: debouncedQuery } : {}),
      ...(exam ? { exam }  : {}),
      ...(subject ? { subject } : {}),
      ...(year ? { year }  : {}),
      ...(paperType ? { type: paperType } : {}),
      ...(keyFilter ? { key: keyFilter } : {}),
    })
  }, [debouncedQuery, exam, subject, year, paperType, keyFilter]) // eslint-disable-line

  return (
    <div className="page-content">
      <div className="container">
        <div className="page-header">
          <div className="page-header-eyebrow">The Archive</div>
          <h1>Search & Subject-Wise Papers</h1>
          <p>Find real previous year question papers segregated by subject, exam, and year.</p>
        </div>

        {/* Search input */}
        <div className="search-container" style={{ marginBottom: 'var(--space-5)' }}>
          <svg className="search-icon" fill="none" stroke="currentColor" viewBox="0 0 24 24" aria-hidden="true">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
          </svg>
          <input
            id="search-input"
            type="search"
            className="search-input"
            placeholder="Search by title, subject (e.g. Mathematics, Physics, General Studies)..."
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            autoFocus
          />
        </div>

        {/* Filter chips container */}
        <div style={{ display: 'flex', flexDirection: 'column', gap: 'var(--space-4)', marginBottom: 'var(--space-8)' }}>
          
          {/* 1. Exam filter */}
          <div>
            <div className="section-label" style={{ marginBottom: 8 }}>Filter by Exam</div>
            <div className="filter-chips">
              {EXAMS.map((item) => (
                <button
                  key={item.slug}
                  className={`filter-chip ${exam === item.slug ? 'active' : ''}`}
                  onClick={() => {
                    setExam(item.slug)
                    // Reset subject if not in selected exam
                  }}
                >
                  {item.label}
                </button>
              ))}
            </div>
          </div>

          {/* 2. Subject filter (Subject-Wise Segregation) */}
          {availableSubjects.length > 0 && (
            <div>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 8 }}>
                <div className="section-label">
                  📚 Segregate by Subject {exam ? `(${exam.toUpperCase()})` : ''}
                </div>
                {subject && (
                  <button
                    className="btn btn-ghost btn-sm"
                    style={{ fontSize: '0.75rem', color: 'var(--color-primary)' }}
                    onClick={() => setSubject('')}
                  >
                    Clear Subject Filter ✕
                  </button>
                )}
              </div>
              <div className="filter-chips" style={{ maxHeight: '110px', overflowY: 'auto', paddingBottom: 4 }}>
                <button
                  className={`filter-chip ${!subject ? 'active' : ''}`}
                  onClick={() => setSubject('')}
                >
                  All Subjects
                </button>
                {availableSubjects.slice(0, 15).map((sub) => (
                  <button
                    key={sub.id}
                    className={`filter-chip ${subject.toLowerCase() === sub.name.toLowerCase() ? 'active' : ''}`}
                    onClick={() => setSubject(subject.toLowerCase() === sub.name.toLowerCase() ? '' : sub.name)}
                    style={{ display: 'inline-flex', alignItems: 'center', gap: 6 }}
                  >
                    <span>{sub.name}</span>
                    <span style={{ fontSize: '0.7rem', opacity: 0.75, background: 'rgba(0,0,0,0.1)', padding: '1px 5px', borderRadius: '8px' }}>
                      {sub.paper_count}
                    </span>
                  </button>
                ))}
              </div>
            </div>
          )}

          {/* 3. Paper Classification filter */}
          <div>
            <div className="section-label" style={{ marginBottom: 8 }}>Paper Classification</div>
            <div className="filter-chips">
              <button
                className={`filter-chip ${!paperType ? 'active' : ''}`}
                onClick={() => setPaperType('')}
              >
                All Papers
              </button>
              <button
                className={`filter-chip ${paperType === 'original' ? 'active' : ''}`}
                onClick={() => setPaperType(paperType === 'original' ? '' : 'original')}
                style={paperType === 'original' ? { backgroundColor: 'rgba(16, 185, 129, 0.15)', borderColor: '#10B981', color: '#10B981' } : {}}
              >
                ✓ Original Exam Papers
              </button>
              <button
                className={`filter-chip ${paperType === 'sample' ? 'active' : ''}`}
                onClick={() => setPaperType(paperType === 'sample' ? '' : 'sample')}
                style={paperType === 'sample' ? { backgroundColor: 'rgba(139, 92, 246, 0.15)', borderColor: '#8B5CF6', color: '#8B5CF6' } : {}}
              >
                📝 Official Sample Papers
              </button>
            </div>
          </div>

          {/* 4. Answer Key Availability Filter */}
          <div>
            <div className="section-label" style={{ marginBottom: 8 }}>Answer Key Segregation</div>
            <div className="filter-chips">
              <button
                className={`filter-chip ${!keyFilter ? 'active' : ''}`}
                onClick={() => setKeyFilter('')}
              >
                All Papers
              </button>
              <button
                className={`filter-chip ${keyFilter === 'with_key' ? 'active' : ''}`}
                onClick={() => setKeyFilter(keyFilter === 'with_key' ? '' : 'with_key')}
                style={keyFilter === 'with_key' ? { backgroundColor: 'rgba(16, 185, 129, 0.15)', borderColor: '#10B981', color: '#10B981' } : {}}
              >
                🔑 With Official Answer Key
              </button>
              <button
                className={`filter-chip ${keyFilter === 'no_key' ? 'active' : ''}`}
                onClick={() => setKeyFilter(keyFilter === 'no_key' ? '' : 'no_key')}
              >
                📄 Question Paper Only
              </button>
            </div>
          </div>

          {/* 5. Year filter */}
          <div>
            <div className="section-label" style={{ marginBottom: 8 }}>Year</div>
            <div className="filter-chips">
              <button className={`filter-chip ${!year ? 'active' : ''}`} onClick={() => setYear('')}>Any</button>
              {YEARS.map((y) => (
                <button
                  key={y}
                  className={`filter-chip ${year === String(y) ? 'active' : ''}`}
                  onClick={() => setYear(year === String(y) ? '' : String(y))}
                >
                  {y}
                </button>
              ))}
            </div>
          </div>

        </div>

        {/* Textbook discovery callout */}
        <div style={{
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between',
          padding: '12px 18px',
          backgroundColor: 'rgba(59, 130, 246, 0.05)',
          border: '1px solid rgba(59, 130, 246, 0.2)',
          borderRadius: '10px',
          marginBottom: 'var(--space-6)',
          flexWrap: 'wrap',
          gap: 10
        }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
            <span style={{ fontSize: '1.25rem' }}>📚</span>
            <div>
              <span style={{ fontWeight: 600, fontSize: '0.875rem', color: 'var(--text-primary)' }}>
                Looking for NCERT & State Board Textbooks?
              </span>
              <p style={{ margin: 0, fontSize: '0.78125rem', color: 'var(--text-secondary)' }}>
                Browse official Class 1 to 12 curriculum books directly alongside question papers.
              </p>
            </div>
          </div>
          <Link
            to={subject ? `/textbooks?search=${encodeURIComponent(subject)}` : '/textbooks'}
            className="btn btn-ghost btn-sm"
            style={{ color: '#2563EB', borderColor: 'rgba(37, 99, 235, 0.3)', fontWeight: 600 }}
          >
            {subject ? `Browse ${subject} Textbooks →` : 'Browse Textbooks →'}
          </Link>
        </div>

        {/* Results */}
        {loading && <PageSkeleton count={6} />}

        {!loading && searched && total !== null && (
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 'var(--space-4)' }}>
            <div className="section-label">
              {total} question paper{total !== 1 ? 's' : ''} found
              {paperType ? ` [${paperType === 'original' ? 'Official Exam Papers' : 'Sample Papers'}]` : ''}
              {keyFilter ? ` [${keyFilter === 'with_key' ? 'With Answer Key' : 'Question Only'}]` : ''}
              {subject ? ` for ${subject}` : ''}
              {exam ? ` in ${exam.toUpperCase()}` : ''}
              {year ? ` (${year})` : ''}
            </div>
            {(exam || subject || year || query || paperType || keyFilter) && (
              <button
                className="btn btn-ghost btn-sm"
                style={{ fontSize: '0.75rem' }}
                onClick={() => {
                  setQuery('')
                  setExam('')
                  setSubject('')
                  setYear('')
                  setPaperType('')
                  setKeyFilter('')
                }}
              >
                Reset All Filters ✕
              </button>
            )}
          </div>
        )}

        {!loading && results.length === 0 && searched && (
          <div className="empty-state">
            <div className="empty-state-icon">🔍</div>
            <h3>No papers found</h3>
            <p>Try clearing subject or exam filters to view more question papers.</p>
            <button
              className="btn btn-primary"
              style={{ marginTop: 12 }}
              onClick={() => {
                setQuery('')
                setExam('')
                setSubject('')
                setYear('')
              }}
            >
              Reset Filters
            </button>
          </div>
        )}

        {!loading && !searched && (
          <div className="empty-state">
            <div className="empty-state-icon">📚</div>
            <h3>Select a Subject or Exam above</h3>
            <p>Browse authentic past papers segregated by Mathematics, Physics, Chemistry, Biology, General Studies, and more.</p>
          </div>
        )}

        {!loading && results.length > 0 && (
          <div className="papers-list">
            {results.map((paper) => {
              const slug = paper.exam?.slug || ''
              const accentColor = paper.exam?.accent_color_hex || '#8FB9A8'
              return (
                <div
                  key={paper.id}
                  className="paper-item"
                  data-exam={slug}
                  style={{ display: 'flex', alignItems: 'center', gap: 16 }}
                >
                  <Link
                    to={`/paper/${paper.id}`}
                    style={{ textDecoration: 'none', display: 'flex', alignItems: 'center', gap: 16, flex: 1, minWidth: 0 }}
                  >
                    <div className="paper-item-year mono" style={{ color: accentColor, minWidth: 50 }}>
                      {paper.year}
                    </div>
                    <div className="paper-item-content" style={{ flex: 1, minWidth: 0 }}>
                      <div className="paper-item-title" style={{ fontSize: '0.9375rem', fontWeight: 600, color: 'var(--text-primary)' }}>
                        {paper.title}
                      </div>

                      {/* Subject Badges */}
                      {Array.isArray(paper.subjects) && paper.subjects.length > 0 && (
                        <div style={{ display: 'flex', gap: 6, flexWrap: 'wrap', marginTop: 6, marginBottom: 6 }}>
                          {paper.subjects.map((sub) => {
                            const sName = typeof sub === 'object' ? sub.name : sub
                            return (
                              <span
                                key={sName}
                                className="badge"
                                style={{
                                  backgroundColor: 'rgba(0,0,0,0.05)',
                                  border: '1px solid var(--color-border)',
                                  fontSize: '0.7rem',
                                  padding: '2px 8px',
                                  borderRadius: '6px',
                                  color: 'var(--text-secondary)',
                                  cursor: 'pointer'
                                }}
                                onClick={(e) => {
                                  e.preventDefault()
                                  e.stopPropagation()
                                  setSubject(sName)
                                }}
                                title={`Filter papers by ${sName}`}
                              >
                                🏷️ {sName}
                              </span>
                            )
                          })}
                        </div>
                      )}

                      <div className="paper-item-meta" style={{ display: 'flex', gap: 8, alignItems: 'center', flexWrap: 'wrap' }}>
                        <PaperTypeBadge paperType={paper.paper_type} />
                        {paper.exam && (
                          <span className="badge badge-exam" style={{ '--exam-accent': accentColor, background: `${accentColor}26`, color: accentColor }}>
                            {paper.exam.name}
                          </span>
                        )}
                        <LanguageBadge language={paper.language} />
                        <AnswerKeyBadge hasKey={paper.has_answer_key} />
                        {paper.source_name && (
                          <span className="badge" style={{ fontSize: '0.7rem', opacity: 0.85, background: 'rgba(0,0,0,0.04)' }}>
                            🏛️ {paper.source_name}
                          </span>
                        )}
                        <span className="mono" style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>
                          ↓ {paper.download_count?.toLocaleString() || 0}
                        </span>
                      </div>
                    </div>
                  </Link>

                  {/* Direct Actions */}
                  <div style={{ display: 'flex', gap: 6, flexWrap: 'wrap' }}>
                    <Link to={`/paper/${paper.id}`} className="btn btn-primary btn-sm" style={{ padding: '6px 12px', fontSize: '0.8125rem' }}>
                      View Paper →
                    </Link>
                    {paper.has_answer_key && (
                      <Link
                        to={`/paper/${paper.id}?tab=key`}
                        className="btn btn-ghost btn-sm"
                        style={{ padding: '6px 10px', fontSize: '0.8125rem', color: '#10B981', borderColor: 'rgba(16,185,129,0.4)', fontWeight: 600 }}
                        title="View Official Answer Key directly"
                      >
                        🔑 Key
                      </Link>
                    )}
                  </div>
                </div>
              )
            })}
          </div>
        )}
      </div>
    </div>
  )
}
