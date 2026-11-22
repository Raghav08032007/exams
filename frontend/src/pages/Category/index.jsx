/**
 * Category page — complete academic and exam hub for a selected exam category.
 * Route: /exam/:slug/:category
 *
 * Synchronizes:
 *  - Real GitHub PYQs from Shabber10/ALL-PYQ-Papers with live CDN streaming.
 *  - Official statutory syllabus documents and interactive unit/topic checklists.
 *  - Prescribed NCERT / Board textbooks synchronized from avallark/NCERT-TextBooks.
 *  - 3D Year & Session navigation cards.
 */
import { useEffect, useState, useMemo } from 'react'
import { useParams, Link, useNavigate } from 'react-router-dom'
import { motion, AnimatePresence } from 'framer-motion'
import {
  fetchExam,
  fetchYearSessions,
  fetchPapers,
  fetchCategoryCurriculum,
  fetchTextbooks,
  fetchChapters,
  getProxyPdfUrl,
  fetchUserSyllabusProgress,
  updateUserSyllabusProgress,
} from '../../api/client'
import { useAuthStore, useToastStore } from '../../store'
import { useReducedMotion } from '../../hooks/useReducedMotion'
import { useSEO } from '../../hooks/useSEO'
import { useTilt } from '../../hooks/useTilt'

// ── Year+Session Card ────────────────────────────────────────────────────────
function YearSessionCard({ year, session, accentColor, reduced, onClick }) {
  const { ref, tiltStyle } = useTilt({ max: 10, disabled: reduced })
  const label = session ? `${year} — ${session}` : `${year}`

  return (
    <div
      ref={ref}
      className="year-session-card"
      style={{
        '--exam-accent': accentColor,
        ...tiltStyle,
        cursor: 'pointer',
      }}
      onClick={onClick}
      role="button"
      tabIndex={0}
      aria-label={`Browse ${label} papers`}
      onKeyDown={(e) => e.key === 'Enter' && onClick()}
    >
      <div className="year-session-card-year mono">{year}</div>
      {session && (
        <div className="year-session-card-session">{session}</div>
      )}
      <div className="year-session-card-arrow" style={{ color: accentColor }}>→</div>
    </div>
  )
}

// ── Main Category Page Component ─────────────────────────────────────────────
export default function CategoryPage() {
  const { slug, category } = useParams()
  const navigate = useNavigate()
  const reduced  = useReducedMotion()
  const { user } = useAuthStore()
  const { addToast } = useToastStore()

  // State
  const [exam,         setExam]         = useState(null)
  const [yearSessions, setYearSessions] = useState([])
  const [papers,       setPapers]       = useState([])
  const [curricula,    setCurricula]    = useState([])
  const [textbooks,    setTextbooks]    = useState([])
  const [categoryLessons, setCategoryLessons] = useState([])
  const [lessonSubjectFilter, setLessonSubjectFilter] = useState('')
  const [completedTopics, setCompletedTopics] = useState(new Set())
  const [loading,      setLoading]      = useState(true)
  const [error,        setError]        = useState(null)

  // Active Tab: 'papers' | 'lessons' | 'syllabus' | 'textbooks' | 'years'
  const [activeTab,    setActiveTab]    = useState('papers')

  // Search & Filter state for papers
  const [searchQuery,     setSearchQuery]     = useState('')
  const [selectedSubject, setSelectedSubject] = useState('')
  const [selectedYear,    setSelectedYear]    = useState('')
  const [selectedType,    setSelectedType]    = useState('all')
  const [selectedStatus,  setSelectedStatus]  = useState('all')
  const [currentPage,     setCurrentPage]     = useState(1)
  const [totalPapers,     setTotalPapers]     = useState(0)
  const [totalPages,      setTotalPages]      = useState(1)
  const [papersLoading,   setPapersLoading]   = useState(false)

  useEffect(() => {
    if (!user) {
      addToast('Please sign in or register to browse exam papers.', 'info')
      navigate('/login', { replace: true })
    }
  }, [user, navigate, addToast])

  // Derive standard name for textbooks
  const standardLevel = useMemo(() => {
    if (slug === 'class-10' || category.includes('10')) return 'Class 10'
    if (slug === 'class-12' || category.includes('12')) return 'Class 12'
    if (slug === 'jee') return 'Class 12'
    if (slug === 'neet') return 'Class 12'
    return 'Class 10'
  }, [slug, category])

  // Load category metadata, syllabi, textbooks, and lessons
  useEffect(() => {
    setLoading(true)
    setError(null)

    Promise.all([
      fetchExam(slug),
      fetchYearSessions(slug, category),
      fetchCategoryCurriculum(slug, category).catch(() => ({ curricula: [] })),
      fetchTextbooks({ standard: standardLevel, per_page: 24 }).catch(() => ({ textbooks: [] })),
      fetchChapters({ standard: standardLevel }).catch(() => ({ chapters: [] })),
      fetchUserSyllabusProgress({ exam: slug }).catch(() => ({ completed_topics: [] })),
    ])
      .then(([examData, ysData, currData, tbData, lessonsData, progData]) => {
        setExam(examData)
        setYearSessions(ysData || [])
        setCurricula(currData?.curricula || [])
        setTextbooks(tbData?.textbooks || [])
        setCategoryLessons(lessonsData?.chapters || [])
        setCompletedTopics(new Set(progData?.completed_topics || []))
      })
      .catch(() => setError('Failed to load category listings.'))
      .finally(() => setLoading(false))
  }, [slug, category, standardLevel])

  // Dynamic Server-Side Papers Fetcher based on Year, Subject, Status, Query, and Page
  useEffect(() => {
    let isCancelled = false
    setPapersLoading(true)

    const params = {
      exam: slug,
      category,
      page: currentPage,
      per_page: 48,
    }
    if (selectedYear) params.year = parseInt(selectedYear, 10)
    if (selectedSubject) params.subject = selectedSubject
    if (searchQuery) params.search = searchQuery
    if (selectedType !== 'all') {
      if (selectedType === 'key') params.has_answer_key = 'true'
      else params.paper_type = selectedType
    }
    if (selectedStatus !== 'all') {
      params.status = selectedStatus
    }

    fetchPapers(params)
      .then((res) => {
        if (isCancelled) return
        const paperList = res.papers || []
        const total = res.pagination?.total ?? res.total ?? paperList.length
        const totalPages = res.pagination?.pages ?? res.total_pages ?? Math.ceil(total / (params.per_page || 48))
        setPapers(paperList)
        setTotalPapers(total)
        setTotalPages(Math.max(1, totalPages))
      })
      .catch(() => {})
      .finally(() => {
        if (!isCancelled) setPapersLoading(false)
      })

    return () => { isCancelled = true }
  }, [slug, category, selectedYear, selectedSubject, searchQuery, selectedType, selectedStatus, currentPage])

  const categoryObj  = exam?.categories?.find(c => c.slug === category)
  const categoryName = categoryObj?.name || category
  const accentColor  = exam?.accent_color_hex || '#8FB9A8'

  useSEO({
    title: exam
      ? `${exam.name} ${categoryName} — Question Papers, Syllabus & Textbooks | ExamVault`
      : 'ExamVault',
    description: exam
      ? `Browse all ${exam.name} ${categoryName} previous year question papers, official syllabus documents, and prescribed NCERT textbooks.`
      : '',
  })

  // Extract available years from yearSessions
  const availableYears = useMemo(() => {
    const set = new Set()
    yearSessions.forEach(ys => {
      if (ys.year) set.add(ys.year)
    })
    return Array.from(set).sort((a, b) => b - a)
  }, [yearSessions])

  // Extract or provide available subjects from papers and standard curriculum
  const availableSubjects = useMemo(() => {
    const set = new Set([
      'Mathematics', 'Science', 'Social Science', 'English', 'Tamil',
      'Hindi', 'Physics', 'Chemistry', 'Biology'
    ])
    papers.forEach(p => {
      (p.subjects || []).forEach(s => {
        set.add(typeof s === 'object' ? s.name : s)
      })
    })
    return Array.from(set).filter(Boolean).sort()
  }, [papers])

  // Filtered papers (client-side pass for instantaneous keyword refinements)
  const filteredPapers = useMemo(() => {
    return papers.filter(p => {
      const matchesSearch = !searchQuery || p.title.toLowerCase().includes(searchQuery.toLowerCase())
      const matchesSubj = !selectedSubject || (p.subjects || []).length === 0 || (p.subjects || []).some(s => {
        const name = (typeof s === 'object' ? s.name : s).toLowerCase()
        const sel = selectedSubject.toLowerCase()
        if (sel.includes('math') && name.includes('math')) return true
        if (sel.includes('social') && name.includes('social')) return true
        return name.includes(sel) || sel.includes(name)
      }) || (p.title && p.title.toLowerCase().includes(selectedSubject.toLowerCase()))
      const matchesYear = !selectedYear || String(p.year) === String(selectedYear)
      const matchesType = selectedType === 'all'
        ? true
        : selectedType === 'key'
          ? p.has_answer_key
          : p.paper_type === selectedType
      const matchesStatus = selectedStatus === 'all'
        ? true
        : (p.verification_status || 'verified') === selectedStatus
      return matchesSearch && matchesSubj && matchesYear && matchesType && matchesStatus
    })
  }, [papers, searchQuery, selectedSubject, selectedYear, selectedType, selectedStatus])

  // Available subjects for lessons
  const availableLessonSubjects = useMemo(() => {
    const set = new Set()
    categoryLessons.forEach(l => {
      if (l.subject_name) set.add(l.subject_name)
    })
    return ['All Subjects', ...Array.from(set).sort()]
  }, [categoryLessons])

  // Filtered category lessons
  const filteredCategoryLessons = useMemo(() => {
    if (!lessonSubjectFilter) return categoryLessons
    return categoryLessons.filter(l => l.subject_name === lessonSubjectFilter)
  }, [categoryLessons, lessonSubjectFilter])

  // Toggle syllabus topic completion
  const handleToggleTopic = async (subjectName, topicName) => {
    const isNowCompleted = !completedTopics.has(topicName)
    const nextSet = new Set(completedTopics)
    if (isNowCompleted) {
      nextSet.add(topicName)
    } else {
      nextSet.delete(topicName)
    }
    setCompletedTopics(nextSet)

    try {
      await updateUserSyllabusProgress({
        exam_slug: slug,
        subject_name: subjectName,
        topic_name: topicName,
        is_completed: isNowCompleted,
      })
      addToast(isNowCompleted ? `Marked "${topicName}" as completed!` : `Unmarked "${topicName}"`, 'info')
    } catch {
      addToast('Failed to update progress.', 'error')
    }
  }

  const handleCardClick = (year, session) => {
    const base = `/exam/${slug}/${category}/${year}`
    navigate(session ? `${base}?session=${encodeURIComponent(session)}` : base)
  }

  if (loading) {
    return (
      <div className="page-content container">
        <div className="skeleton" style={{ width: '30%', height: 16, marginBottom: 12 }} />
        <div className="skeleton" style={{ width: '60%', height: 40, marginBottom: 20 }} />
        <div className="skeleton" style={{ width: '100%', height: 120, borderRadius: 16, marginBottom: 30 }} />
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(280px, 1fr))', gap: 16 }}>
          {[1, 2, 3, 4, 5, 6].map(i => (
            <div key={i} className="skeleton" style={{ height: 160, borderRadius: 14 }} />
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
          <h3>Could not load category</h3>
          <p>{error}</p>
          <Link to={`/exam/${slug}`} className="btn btn-primary">← Back to {exam?.name || 'Exam'}</Link>
        </div>
      </div>
    )
  }

  return (
    <div className="page-content" data-exam={slug}>
      <div className="container">

        {/* Breadcrumb */}
        <motion.div
          style={{ display: 'flex', gap: 8, alignItems: 'center', marginBottom: 'var(--space-4)', fontSize: '0.8125rem', color: 'var(--text-muted)', flexWrap: 'wrap' }}
          initial={reduced ? false : { opacity: 0, x: -10 }}
          animate={{ opacity: 1, x: 0 }}
        >
          <Link to="/" style={{ color: 'var(--text-muted)', textDecoration: 'none' }}>Home</Link>
          <span>›</span>
          <Link to={`/exam/${slug}`} style={{ color: 'var(--text-muted)', textDecoration: 'none' }}>
            {exam?.name || slug.toUpperCase()}
          </Link>
          <span>›</span>
          <span style={{ color: 'var(--text-primary)', fontWeight: 600 }}>{categoryName}</span>
        </motion.div>

        {/* Hero Card with Live GitHub Sync Badge */}
        <div style={{
          backgroundColor: 'var(--color-surface)',
          border: '1px solid var(--color-border)',
          borderRadius: 20,
          padding: '28px 32px',
          marginBottom: 28,
          boxShadow: '0 4px 20px rgba(0,0,0,0.02)',
          position: 'relative'
        }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', flexWrap: 'wrap', gap: 16 }}>
            <div>
              <div style={{ display: 'flex', alignItems: 'center', gap: 10, marginBottom: 8, flexWrap: 'wrap' }}>
                <span
                  className="page-header-eyebrow"
                  style={{ color: accentColor, fontWeight: 700, margin: 0 }}
                >
                  {exam?.name}
                </span>
                <span style={{ color: 'var(--text-muted)' }}>•</span>
                <span style={{
                  display: 'inline-flex',
                  alignItems: 'center',
                  gap: 6,
                  fontSize: '0.75rem',
                  fontWeight: 600,
                  backgroundColor: 'rgba(99, 102, 241, 0.1)',
                  color: '#6366F1',
                  padding: '3px 10px',
                  borderRadius: 12
                }}>
                  <span>🐙</span>
                  <span>GitHub Synchronized (Shabber10/ALL-PYQ-Papers & avallark/NCERT)</span>
                </span>
              </div>

              <h1 style={{ fontSize: '2rem', fontWeight: 800, margin: '0 0 10px', letterSpacing: '-0.02em' }}>
                {categoryName}
              </h1>
              <p style={{ color: 'var(--text-secondary)', margin: 0, fontSize: '0.95rem', maxWidth: 720 }}>
                Access verified past year question papers, official syllabus blueprints, and prescribed NCERT textbooks synchronized directly from open repositories with live CDN rendering.
              </p>
            </div>

            {/* Quick KPI Stats */}
            <div style={{ display: 'flex', gap: 16, flexWrap: 'wrap' }}>
              <div style={{
                backgroundColor: 'var(--color-bg)',
                border: '1px solid var(--color-border)',
                borderRadius: 12,
                padding: '10px 16px',
                textAlign: 'center'
              }}>
                <div style={{ fontSize: '1.25rem', fontWeight: 800, color: 'var(--text-primary)' }}>{papers.length}</div>
                <div style={{ fontSize: '0.72rem', color: 'var(--text-muted)', textTransform: 'uppercase', fontWeight: 600 }}>Papers</div>
              </div>
              <div style={{
                backgroundColor: 'var(--color-bg)',
                border: '1px solid var(--color-border)',
                borderRadius: 12,
                padding: '10px 16px',
                textAlign: 'center'
              }}>
                <div style={{ fontSize: '1.25rem', fontWeight: 800, color: '#10B981' }}>{yearSessions.length}</div>
                <div style={{ fontSize: '0.72rem', color: 'var(--text-muted)', textTransform: 'uppercase', fontWeight: 600 }}>Years</div>
              </div>
              <div style={{
                backgroundColor: 'var(--color-bg)',
                border: '1px solid var(--color-border)',
                borderRadius: 12,
                padding: '10px 16px',
                textAlign: 'center'
              }}>
                <div style={{ fontSize: '1.25rem', fontWeight: 800, color: '#F59E0B' }}>{curricula.length}</div>
                <div style={{ fontSize: '0.72rem', color: 'var(--text-muted)', textTransform: 'uppercase', fontWeight: 600 }}>Syllabi</div>
              </div>
              <div style={{
                backgroundColor: 'var(--color-bg)',
                border: '1px solid var(--color-border)',
                borderRadius: 12,
                padding: '10px 16px',
                textAlign: 'center'
              }}>
                <div style={{ fontSize: '1.25rem', fontWeight: 800, color: '#8B5CF6' }}>{categoryLessons.length}</div>
                <div style={{ fontSize: '0.72rem', color: 'var(--text-muted)', textTransform: 'uppercase', fontWeight: 600 }}>Lessons</div>
              </div>
              <div style={{
                backgroundColor: 'var(--color-bg)',
                border: '1px solid var(--color-border)',
                borderRadius: 12,
                padding: '10px 16px',
                textAlign: 'center'
              }}>
                <div style={{ fontSize: '1.25rem', fontWeight: 800, color: '#EC4899' }}>{textbooks.length}</div>
                <div style={{ fontSize: '0.72rem', color: 'var(--text-muted)', textTransform: 'uppercase', fontWeight: 600 }}>Books</div>
              </div>
            </div>
          </div>
        </div>

        {/* Tab Navigation */}
        <div style={{
          display: 'flex',
          gap: 10,
          borderBottom: '1px solid var(--color-border)',
          marginBottom: 24,
          overflowX: 'auto',
          paddingBottom: 2
        }}>
          {[
            { id: 'papers', label: `📑 Question Papers (${papers.length})` },
            { id: 'lessons', label: `📖 Lessons & Question Bank (${categoryLessons.length})` },
            { id: 'syllabus', label: `📘 Official Syllabus & Curriculum (${curricula.length})` },
            { id: 'textbooks', label: `📚 Prescribed Textbooks (${textbooks.length})` },
            { id: 'years', label: `📅 Browse by Year (${yearSessions.length})` },
          ].map(tab => (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id)}
              style={{
                padding: '10px 18px',
                border: 'none',
                background: 'none',
                cursor: 'pointer',
                fontWeight: activeTab === tab.id ? 700 : 500,
                fontSize: '0.9rem',
                color: activeTab === tab.id ? accentColor : 'var(--text-secondary)',
                borderBottom: activeTab === tab.id ? `2px solid ${accentColor}` : '2px solid transparent',
                transition: 'all 0.15s ease',
                whiteSpace: 'nowrap'
              }}
            >
              {tab.label}
            </button>
          ))}
        </div>

        {/* ── TAB 1: QUESTION PAPERS ── */}
        {activeTab === 'papers' && (
          <div>
            {/* Filter Bar */}
            <div style={{
              display: 'flex',
              gap: 12,
              flexWrap: 'wrap',
              marginBottom: 14,
              backgroundColor: 'var(--color-surface)',
              border: '1px solid var(--color-border)',
              borderRadius: 14,
              padding: '14px 18px',
              alignItems: 'center'
            }}>
              <input
                type="text"
                placeholder="Search papers by title, subject..."
                value={searchQuery}
                onChange={e => { setSearchQuery(e.target.value); setCurrentPage(1) }}
                style={{
                  flex: 1,
                  minWidth: 180,
                  padding: '8px 14px',
                  borderRadius: 8,
                  border: '1px solid var(--color-border)',
                  backgroundColor: 'var(--color-bg)',
                  color: 'var(--text-primary)',
                  fontSize: '0.875rem'
                }}
              />

              {/* Year Dropdown */}
              <select
                value={selectedYear}
                onChange={e => { setSelectedYear(e.target.value); setCurrentPage(1) }}
                style={{
                  padding: '8px 12px',
                  borderRadius: 8,
                  border: '1px solid var(--color-border)',
                  backgroundColor: 'var(--color-bg)',
                  color: 'var(--text-primary)',
                  fontSize: '0.875rem',
                  fontWeight: selectedYear ? 700 : 500
                }}
              >
                <option value="">All Exam Years</option>
                {availableYears.map(yr => (
                  <option key={yr} value={yr}>Year {yr}</option>
                ))}
              </select>

              {availableSubjects.length > 0 && (
                <select
                  value={selectedSubject}
                  onChange={e => { setSelectedSubject(e.target.value); setCurrentPage(1) }}
                  style={{
                    padding: '8px 12px',
                    borderRadius: 8,
                    border: '1px solid var(--color-border)',
                    backgroundColor: 'var(--color-bg)',
                    color: 'var(--text-primary)',
                    fontSize: '0.875rem',
                    fontWeight: selectedSubject ? 700 : 500
                  }}
                >
                  <option value="">All Subjects ({availableSubjects.length})</option>
                  {availableSubjects.map(s => (
                    <option key={s} value={s}>{s}</option>
                  ))}
                </select>
              )}

              <select
                value={selectedType}
                onChange={e => { setSelectedType(e.target.value); setCurrentPage(1) }}
                style={{
                  padding: '8px 12px',
                  borderRadius: 8,
                  border: '1px solid var(--color-border)',
                  backgroundColor: 'var(--color-bg)',
                  color: 'var(--text-primary)',
                  fontSize: '0.875rem'
                }}
              >
                <option value="all">All Paper Types</option>
                <option value="key">With Co-located Answer Key</option>
                <option value="original">Original Board Papers</option>
                <option value="sample">Sample Question Papers</option>
              </select>

              <select
                value={selectedStatus}
                onChange={e => { setSelectedStatus(e.target.value); setCurrentPage(1) }}
                style={{
                  padding: '8px 12px',
                  borderRadius: 8,
                  border: '1px solid var(--color-border)',
                  backgroundColor: 'var(--color-bg)',
                  color: 'var(--text-primary)',
                  fontSize: '0.875rem'
                }}
              >
                <option value="all">All Statuses</option>
                <option value="verified">🟢 Verified Only</option>
                <option value="unverified">🟡 Provisional</option>
              </select>

              <span style={{ fontSize: '0.8125rem', color: 'var(--text-muted)', marginLeft: 'auto' }}>
                {papersLoading ? '⏳ Loading...' : `Showing ${filteredPapers.length} of ${totalPapers || filteredPapers.length} papers`}
              </span>
            </div>

            {/* Quick Year Navigation Bar */}
            {availableYears.length > 0 && (
              <div style={{
                display: 'flex',
                gap: 8,
                flexWrap: 'wrap',
                marginBottom: 20,
                alignItems: 'center',
                padding: '8px 14px',
                backgroundColor: 'rgba(0,0,0,0.015)',
                borderRadius: 10,
                border: '1px solid var(--color-border)'
              }}>
                <span style={{ fontSize: '0.78125rem', fontWeight: 700, color: 'var(--text-secondary)' }}>
                  📅 Quick Year:
                </span>
                <button
                  type="button"
                  onClick={() => { setSelectedYear(''); setCurrentPage(1) }}
                  style={{
                    padding: '3px 10px',
                    borderRadius: 14,
                    border: '1px solid',
                    borderColor: !selectedYear ? accentColor : 'var(--color-border)',
                    backgroundColor: !selectedYear ? `${accentColor}20` : 'transparent',
                    color: !selectedYear ? accentColor : 'var(--text-secondary)',
                    fontSize: '0.75rem',
                    fontWeight: !selectedYear ? 700 : 500,
                    cursor: 'pointer'
                  }}
                >
                  All Years
                </button>
                {availableYears.slice(0, 15).map(yr => (
                  <button
                    key={yr}
                    type="button"
                    onClick={() => { setSelectedYear(String(yr)); setCurrentPage(1) }}
                    style={{
                      padding: '3px 10px',
                      borderRadius: 14,
                      border: '1px solid',
                      borderColor: selectedYear === String(yr) ? accentColor : 'var(--color-border)',
                      backgroundColor: selectedYear === String(yr) ? `${accentColor}20` : 'transparent',
                      color: selectedYear === String(yr) ? accentColor : 'var(--text-secondary)',
                      fontSize: '0.75rem',
                      fontWeight: selectedYear === String(yr) ? 700 : 500,
                      cursor: 'pointer'
                    }}
                  >
                    {yr}
                  </button>
                ))}
              </div>
            )}

            {/* Quick Core Subject Pills Bar */}
            <div style={{
              display: 'flex',
              gap: 8,
              flexWrap: 'wrap',
              marginBottom: 24,
              alignItems: 'center',
              padding: '8px 14px',
              backgroundColor: 'rgba(99, 102, 241, 0.04)',
              borderRadius: 10,
              border: '1px solid rgba(99, 102, 241, 0.18)'
            }}>
              <span style={{ fontSize: '0.78125rem', fontWeight: 700, color: '#4338ca' }}>
                🎯 Core Subject:
              </span>
              {['All Subjects', 'Mathematics', 'Science', 'Social Science', 'English', 'Tamil', 'Hindi'].map(sub => {
                const isSelected = sub === 'All Subjects' ? !selectedSubject : selectedSubject.toLowerCase() === sub.toLowerCase()
                return (
                  <button
                    key={sub}
                    type="button"
                    onClick={() => {
                      setSelectedSubject(sub === 'All Subjects' ? '' : sub)
                      setCurrentPage(1)
                    }}
                    style={{
                      padding: '4px 12px',
                      borderRadius: 14,
                      border: '1px solid',
                      borderColor: isSelected ? '#4f46e5' : 'var(--color-border)',
                      backgroundColor: isSelected ? '#4f46e5' : '#ffffff',
                      color: isSelected ? '#ffffff' : 'var(--text-primary)',
                      fontSize: '0.78125rem',
                      fontWeight: isSelected ? 700 : 500,
                      cursor: 'pointer',
                      transition: 'all 0.15s ease'
                    }}
                  >
                    {sub}
                  </button>
                )
              })}
            </div>

            {/* Papers Grid */}
            {filteredPapers.length === 0 ? (
              <div className="empty-state">
                <div className="empty-state-icon">🔍</div>
                <h3>No papers match your filters</h3>
                <p>Try resetting the subject, type, or verification status query.</p>
                <button
                  className="btn btn-secondary"
                  onClick={() => { setSearchQuery(''); setSelectedSubject(''); setSelectedType('all'); setSelectedStatus('all') }}
                >
                  Reset Filters
                </button>
              </div>
            ) : (
              <div style={{
                display: 'grid',
                gridTemplateColumns: 'repeat(auto-fill, minmax(320px, 1fr))',
                gap: 18,
                marginBottom: 36
              }}>
                {filteredPapers.map(paper => (
                  <div
                    key={paper.id}
                    style={{
                      backgroundColor: 'var(--color-surface)',
                      border: '1px solid var(--color-border)',
                      borderRadius: 16,
                      padding: '20px',
                      display: 'flex',
                      flexDirection: 'column',
                      boxShadow: '0 2px 12px rgba(0,0,0,0.02)',
                      position: 'relative'
                    }}
                  >
                    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: 10 }}>
                      <span style={{
                        fontWeight: 700,
                        fontSize: '0.8125rem',
                        color: accentColor,
                        backgroundColor: `${accentColor}15`,
                        padding: '2px 8px',
                        borderRadius: 8
                      }}>
                        {paper.year} {paper.session ? `· ${paper.session}` : ''}
                      </span>

                      <div style={{ display: 'flex', gap: 6, alignItems: 'center' }}>
                        {paper.verification_status === 'verified' ? (
                          <span style={{
                            fontSize: '0.72rem',
                            fontWeight: 700,
                            color: '#059669',
                            backgroundColor: 'rgba(16, 185, 129, 0.12)',
                            padding: '2px 8px',
                            borderRadius: 8,
                            display: 'inline-flex',
                            alignItems: 'center',
                            gap: 4
                          }}>
                            <span>✓</span> Verified Official
                          </span>
                        ) : (
                          <span style={{
                            fontSize: '0.72rem',
                            fontWeight: 700,
                            color: '#D97706',
                            backgroundColor: 'rgba(245, 158, 11, 0.12)',
                            padding: '2px 8px',
                            borderRadius: 8,
                            display: 'inline-flex',
                            alignItems: 'center',
                            gap: 4
                          }}>
                            <span>⚠️</span> Provisional / Unverified
                          </span>
                        )}

                        {paper.has_answer_key && (
                          <span style={{
                            fontSize: '0.72rem',
                            fontWeight: 700,
                            color: '#10B981',
                            backgroundColor: 'rgba(16, 185, 129, 0.1)',
                            padding: '2px 8px',
                            borderRadius: 8
                          }}>
                            🔑 Key
                          </span>
                        )}
                      </div>
                    </div>

                    <h3 style={{ fontSize: '1.05rem', fontWeight: 700, margin: '0 0 10px', lineHeight: 1.4 }}>
                      <Link to={`/paper/${paper.id}`} style={{ color: 'var(--text-primary)', textDecoration: 'none' }}>
                        {paper.title}
                      </Link>
                    </h3>

                    {/* Subjects & Origin */}
                    <div style={{ display: 'flex', flexWrap: 'wrap', gap: 6, marginBottom: 14 }}>
                      {(paper.subjects || []).map(s => (
                        <span key={typeof s === 'object' ? s.name : s} className="badge" style={{ backgroundColor: 'var(--color-bg)', fontSize: '0.72rem' }}>
                          {typeof s === 'object' ? s.name : s}
                        </span>
                      ))}
                      <span className="badge" style={{ backgroundColor: 'rgba(99, 102, 241, 0.08)', color: '#6366F1', fontSize: '0.72rem' }}>
                        🐙 GitHub Raw CDN
                      </span>
                    </div>

                    {/* Single-Card Co-located Actions */}
                    <div style={{ marginTop: 'auto', display: 'flex', gap: 8 }}>
                      <Link
                        to={`/paper/${paper.id}`}
                        className="btn btn-primary"
                        style={{ flex: 1, fontSize: '0.8125rem', textAlign: 'center', padding: '8px 12px' }}
                      >
                        📄 Open PDF
                      </Link>

                      <a
                        href={paper.pdf_url}
                        target="_blank"
                        rel="noreferrer"
                        className="btn btn-secondary"
                        style={{ fontSize: '0.8125rem', padding: '8px 10px' }}
                        title="Direct Raw PDF Download"
                      >
                        ⬇️
                      </a>

                      <Link
                        to={`/paper/${paper.id}?doubt=true`}
                        className="btn btn-secondary"
                        style={{ fontSize: '0.8125rem', padding: '8px 10px' }}
                        title="Ask Gemini AI Tutor"
                      >
                        🤖
                      </Link>
                    </div>
                  </div>
                ))}
              </div>
            )}

            {/* Pagination Controls for Question Papers */}
            {totalPages > 1 && (
              <div style={{
                display: 'flex',
                justifyContent: 'center',
                alignItems: 'center',
                gap: 14,
                marginTop: 24,
                marginBottom: 36,
                padding: '12px 20px',
                backgroundColor: 'var(--color-surface)',
                borderRadius: 12,
                border: '1px solid var(--color-border)',
                flexWrap: 'wrap'
              }}>
                <button
                  className="btn btn-secondary btn-sm"
                  disabled={currentPage <= 1 || papersLoading}
                  onClick={() => { setCurrentPage(p => Math.max(1, p - 1)); window.scrollTo({ top: 400, behavior: 'smooth' }) }}
                  style={{ fontWeight: 600 }}
                >
                  ← Previous Page
                </button>

                <span style={{ fontSize: '0.875rem', fontWeight: 600, color: 'var(--text-primary)' }}>
                  Page {currentPage} of {totalPages} <span style={{ color: 'var(--text-muted)', fontWeight: 400 }}>({totalPapers} total papers)</span>
                </span>

                <button
                  className="btn btn-secondary btn-sm"
                  disabled={currentPage >= totalPages || papersLoading}
                  onClick={() => { setCurrentPage(p => Math.min(totalPages, p + 1)); window.scrollTo({ top: 400, behavior: 'smooth' }) }}
                  style={{ fontWeight: 600 }}
                >
                  Next Page →
                </button>
              </div>
            )}
          </div>
        )}

        {/* ── TAB: MODULAR LESSONS & CHAPTER-WISE QUESTIONS ── */}
        {activeTab === 'lessons' && (
          <div>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', flexWrap: 'wrap', gap: 14, marginBottom: 20 }}>
              <div>
                <h2 style={{ fontSize: '1.4rem', fontWeight: 700, margin: '0 0 6px' }}>
                  Curriculum Lessons & Chapter-Wise Question Bank
                </h2>
                <p style={{ color: 'var(--text-secondary)', fontSize: '0.9rem', margin: 0, maxWidth: 800 }}>
                  Each subject is segregated into modular lessons. Each lesson co-locates official textbook content, 
                  past 10-year board questions, step-by-step marking scheme solutions, and an interactive Gemini AI doubt tutor.
                </p>
              </div>

              <Link
                to={`/lessons?standard=${encodeURIComponent(standardLevel)}`}
                className="btn btn-primary"
                style={{ backgroundColor: '#8B5CF6', borderColor: '#8B5CF6', fontSize: '0.85rem' }}
              >
                🚀 Open Full Interactive Lessons Workspace →
              </Link>
            </div>

            {/* Subject Filter Chips for Lessons */}
            {availableLessonSubjects.length > 1 && (
              <div style={{ marginBottom: 20 }}>
                <div className="section-label" style={{ marginBottom: 8 }}>Filter Lessons by Subject</div>
                <div className="filter-chips">
                  {availableLessonSubjects.map(sub => {
                    const val = sub === 'All Subjects' ? '' : sub
                    const isActive = lessonSubjectFilter === val
                    return (
                      <button
                        key={sub}
                        className={`filter-chip ${isActive ? 'active' : ''}`}
                        onClick={() => setLessonSubjectFilter(val)}
                        style={isActive ? { backgroundColor: '#8B5CF6', borderColor: '#8B5CF6', color: '#fff' } : {}}
                      >
                        {sub}
                      </button>
                    )
                  })}
                </div>
              </div>
            )}

            {filteredCategoryLessons.length === 0 ? (
              <div className="empty-state">
                <div className="empty-state-icon">📖</div>
                <h3>No lessons found</h3>
                <p>Curriculum lessons are being indexed for {categoryName}.</p>
              </div>
            ) : (
              <div style={{
                display: 'grid',
                gridTemplateColumns: 'repeat(auto-fill, minmax(320px, 1fr))',
                gap: 20
              }}>
                {filteredCategoryLessons.map(l => (
                  <div
                    key={l.id}
                    style={{
                      backgroundColor: 'var(--color-surface)',
                      border: '1px solid var(--color-border)',
                      borderRadius: 14,
                      padding: '20px',
                      display: 'flex',
                      flexDirection: 'column',
                      justifyContent: 'space-between',
                      gap: 12,
                      boxShadow: 'var(--shadow-sm)'
                    }}
                  >
                    <div>
                      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 8 }}>
                        <span style={{
                          fontSize: '0.72rem',
                          fontWeight: 700,
                          padding: '2px 8px',
                          borderRadius: '4px',
                          backgroundColor: '#EDE9FE',
                          color: '#6D28D9'
                        }}>
                          {l.subject_name}
                        </span>
                        <span style={{ fontSize: '0.75rem', fontWeight: 600, color: '#059669', backgroundColor: '#ECFDF5', padding: '2px 8px', borderRadius: '4px' }}>
                          {l.marks_weightage}
                        </span>
                      </div>

                      <h3 style={{ fontSize: '1.05rem', margin: '0 0 8px 0', color: 'var(--text-primary)', lineHeight: 1.35 }}>
                        Ch {l.chapter_number}: {l.chapter_title}
                      </h3>

                      <p style={{ fontSize: '0.8125rem', color: 'var(--text-secondary)', margin: 0, lineHeight: 1.45, maxHeight: '58px', overflow: 'hidden' }}>
                        {l.summary_notes}
                      </p>
                    </div>

                    <div style={{ borderTop: '1px solid var(--color-border)', paddingTop: 12, display: 'flex', flexDirection: 'column', gap: 8 }}>
                      <div style={{ fontSize: '0.75rem', color: '#6B7280', fontWeight: 600 }}>
                        ❓ {l.question_count} Curated Questions & Solutions
                      </div>

                      <div style={{ display: 'flex', gap: 8 }}>
                        {l.textbook_chapter_url && (
                          <a
                            href={l.textbook_chapter_url}
                            target="_blank"
                            rel="noreferrer"
                            className="btn btn-secondary btn-sm"
                            style={{ flex: 1, fontSize: '0.75rem', textAlign: 'center' }}
                            title="Read prescribed textbook chapter"
                          >
                            📖 Read Book
                          </a>
                        )}

                        <Link
                          to={`/lessons?standard=${encodeURIComponent(standardLevel)}&subject=${encodeURIComponent(l.subject_name)}`}
                          className="btn btn-primary btn-sm"
                          style={{ flex: 1.2, fontSize: '0.75rem', textAlign: 'center', backgroundColor: '#8B5CF6', borderColor: '#8B5CF6' }}
                        >
                          Explore Questions →
                        </Link>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        )}

        {/* ── TAB 2: OFFICIAL SYLLABUS & CURRICULUM ── */}
        {activeTab === 'syllabus' && (
          <div>
            <div style={{ marginBottom: 20 }}>
              <h2 style={{ fontSize: '1.4rem', fontWeight: 700, margin: '0 0 6px' }}>
                Official Statutory Syllabus & Curriculum Blueprints
              </h2>
              <p style={{ color: 'var(--text-secondary)', fontSize: '0.9rem', margin: 0 }}>
                Statutory academic curricula gazetted by official examination authorities. Track your unit-by-unit study progress below.
              </p>
            </div>

            {curricula.length === 0 ? (
              <div className="empty-state">
                <div className="empty-state-icon">📘</div>
                <h3>Syllabus being indexed for {categoryName}</h3>
                <p>Curriculum blueprints are populated automatically from official examination board gazettes.</p>
              </div>
            ) : (
              <div style={{ display: 'flex', flexDirection: 'column', gap: 24, marginBottom: 36 }}>
                {curricula.map(curr => {
                  const allTopics = (curr.units || []).flatMap(u => u.topics || [])
                  const completedInThis = allTopics.filter(t => completedTopics.has(t)).length
                  const pct = allTopics.length > 0 ? Math.round((completedInThis / allTopics.length) * 100) : 0

                  return (
                    <div
                      key={curr.id}
                      style={{
                        backgroundColor: 'var(--color-surface)',
                        border: '1px solid var(--color-border)',
                        borderRadius: 18,
                        padding: '24px',
                        boxShadow: '0 2px 14px rgba(0,0,0,0.02)'
                      }}
                    >
                      {/* Syllabus Header */}
                      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', flexWrap: 'wrap', gap: 14, marginBottom: 16 }}>
                        <div>
                          <div style={{ display: 'flex', gap: 8, alignItems: 'center', marginBottom: 6 }}>
                            <span style={{
                              fontWeight: 700,
                              fontSize: '0.75rem',
                              color: '#6366F1',
                              backgroundColor: 'rgba(99, 102, 241, 0.1)',
                              padding: '3px 10px',
                              borderRadius: 12
                            }}>
                              {curr.subject_name} · Academic Year {curr.academic_year}
                            </span>
                            <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>
                              Marks: {curr.total_marks} | Duration: {curr.exam_duration}
                            </span>
                          </div>
                          <h3 style={{ fontSize: '1.25rem', fontWeight: 800, margin: 0 }}>
                            {curr.curriculum_title}
                          </h3>
                          <div style={{ fontSize: '0.8125rem', color: 'var(--text-muted)', marginTop: 4 }}>
                            Source: {curr.source_name}
                          </div>
                        </div>

                        {/* Official PDF Action */}
                        <a
                          href={curr.official_pdf_url}
                          target="_blank"
                          rel="noreferrer"
                          className="btn btn-primary"
                          style={{ display: 'inline-flex', alignItems: 'center', gap: 8, fontSize: '0.85rem' }}
                        >
                          <span>📄</span>
                          <span>View Official Gazette PDF</span>
                        </a>
                      </div>

                      {/* Progress Bar */}
                      {allTopics.length > 0 && (
                        <div style={{
                          backgroundColor: 'var(--color-bg)',
                          borderRadius: 12,
                          padding: '12px 16px',
                          marginBottom: 20,
                          border: '1px solid var(--color-border)'
                        }}>
                          <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.8125rem', marginBottom: 6 }}>
                            <span style={{ fontWeight: 600, color: 'var(--text-primary)' }}>
                              Syllabus Completion Progress
                            </span>
                            <span style={{ fontWeight: 700, color: pct === 100 ? '#10B981' : accentColor }}>
                              {completedInThis} of {allTopics.length} topics ({pct}%)
                            </span>
                          </div>
                          <div style={{
                            width: '100%',
                            height: 8,
                            backgroundColor: 'var(--color-border)',
                            borderRadius: 4,
                            overflow: 'hidden'
                          }}>
                            <div style={{
                              width: `${pct}%`,
                              height: '100%',
                              backgroundColor: pct === 100 ? '#10B981' : accentColor,
                              transition: 'width 0.3s ease'
                            }} />
                          </div>
                        </div>
                      )}

                      {/* Units & Topics List */}
                      <div style={{ display: 'flex', flexDirection: 'column', gap: 14 }}>
                        {(curr.units || []).map((unit, uIdx) => (
                          <div
                            key={`${unit.unit_no}-${uIdx}`}
                            style={{
                              border: '1px solid var(--color-border)',
                              borderRadius: 12,
                              padding: '14px 18px',
                              backgroundColor: 'var(--color-bg)'
                            }}
                          >
                            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 10 }}>
                              <div style={{ fontWeight: 700, fontSize: '0.925rem', color: 'var(--text-primary)' }}>
                                Unit {unit.unit_no}: {unit.name}
                              </div>
                              {unit.marks && (
                                <span style={{
                                  fontSize: '0.75rem',
                                  fontWeight: 700,
                                  color: '#F59E0B',
                                  backgroundColor: 'rgba(245, 158, 11, 0.1)',
                                  padding: '2px 8px',
                                  borderRadius: 8
                                }}>
                                  {unit.marks} Marks
                                </span>
                              )}
                            </div>

                            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(240px, 1fr))', gap: 8 }}>
                              {(unit.topics || []).map(topic => {
                                const isDone = completedTopics.has(topic)
                                return (
                                  <label
                                    key={topic}
                                    style={{
                                      display: 'flex',
                                      alignItems: 'center',
                                      gap: 10,
                                      fontSize: '0.8125rem',
                                      color: isDone ? 'var(--text-muted)' : 'var(--text-primary)',
                                      textDecoration: isDone ? 'line-through' : 'none',
                                      cursor: 'pointer',
                                      padding: '4px 6px',
                                      borderRadius: 6
                                    }}
                                  >
                                    <input
                                      type="checkbox"
                                      checked={isDone}
                                      onChange={() => handleToggleTopic(curr.subject_name, topic)}
                                      style={{ cursor: 'pointer', accentColor: '#10B981' }}
                                    />
                                    <span>{topic}</span>
                                  </label>
                                )
                              })}
                            </div>
                          </div>
                        ))}
                      </div>

                    </div>
                  )
                })}
              </div>
            )}
          </div>
        )}

        {/* ── TAB 3: PRESCRIBED TEXTBOOKS ── */}
        {activeTab === 'textbooks' && (
          <div>
            <div style={{ marginBottom: 20 }}>
              <h2 style={{ fontSize: '1.4rem', fontWeight: 700, margin: '0 0 6px' }}>
                Prescribed NCERT & State Board Textbooks
              </h2>
              <p style={{ color: 'var(--text-secondary)', fontSize: '0.9rem', margin: 0 }}>
                Synchronized directly from <strong>avallark/NCERT-TextBooks</strong> and statutory educational repositories.
              </p>
            </div>

            {textbooks.length === 0 ? (
              <div className="empty-state">
                <div className="empty-state-icon">📚</div>
                <h3>No textbooks indexed yet</h3>
                <p>Standard curriculum textbooks for {standardLevel} are being synchronized.</p>
              </div>
            ) : (
              <div style={{
                display: 'grid',
                gridTemplateColumns: 'repeat(auto-fill, minmax(280px, 1fr))',
                gap: 18,
                marginBottom: 36
              }}>
                {textbooks.map(tb => (
                  <div
                    key={tb.id}
                    style={{
                      backgroundColor: 'var(--color-surface)',
                      border: '1px solid var(--color-border)',
                      borderRadius: 16,
                      padding: '20px',
                      display: 'flex',
                      flexDirection: 'column',
                      boxShadow: '0 2px 10px rgba(0,0,0,0.02)'
                    }}
                  >
                    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 10 }}>
                      <span className="badge" style={{ backgroundColor: 'rgba(16, 185, 129, 0.1)', color: '#059669', fontSize: '0.72rem' }}>
                        {tb.board}
                      </span>
                      <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>
                        {tb.standard_level}
                      </span>
                    </div>

                    <h4 style={{ fontSize: '1rem', fontWeight: 700, margin: '0 0 6px', lineHeight: 1.4 }}>
                      {tb.title}
                    </h4>

                    <div style={{ fontSize: '0.8125rem', color: 'var(--text-secondary)', marginBottom: 14 }}>
                      Subject: <strong>{tb.subject_name || 'General'}</strong>
                    </div>

                    <div style={{ marginTop: 'auto', display: 'flex', gap: 8 }}>
                      <a
                        href={tb.pdf_url}
                        target="_blank"
                        rel="noreferrer"
                        className="btn btn-primary"
                        style={{ flex: 1, fontSize: '0.8125rem', textAlign: 'center', padding: '8px 12px' }}
                      >
                        📖 Read Textbook PDF
                      </a>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        )}

        {/* ── TAB 4: BROWSE BY YEAR ── */}
        {activeTab === 'years' && (
          <div>
            <div style={{ marginBottom: 20 }}>
              <h2 style={{ fontSize: '1.4rem', fontWeight: 700, margin: '0 0 6px' }}>
                Select Examination Year or Session
              </h2>
              <p style={{ color: 'var(--text-secondary)', fontSize: '0.9rem', margin: 0 }}>
                Open dedicated flip-card view for each session and year.
              </p>
            </div>

            {yearSessions.length === 0 ? (
              <div className="empty-state">
                <div className="empty-state-icon">📭</div>
                <h3>No years available</h3>
                <p>No verified question papers have been uploaded for {categoryName}.</p>
              </div>
            ) : (
              <motion.div
                className="year-sessions-grid"
                initial={reduced ? false : { opacity: 0 }}
                animate={{ opacity: 1 }}
              >
                {yearSessions.map((ys, idx) => (
                  <YearSessionCard
                    key={`${ys.year}-${ys.session ?? 'null'}-${idx}`}
                    year={ys.year}
                    session={ys.session}
                    accentColor={accentColor}
                    reduced={reduced}
                    onClick={() => handleCardClick(ys.year, ys.session)}
                  />
                ))}
              </motion.div>
            )}
          </div>
        )}

      </div>
    </div>
  )
}
