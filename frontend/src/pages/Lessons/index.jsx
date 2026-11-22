/**
 * Lessons & Chapter-Wise Learning Hub — Complete 4-Tier Categorization System:
 * 1. Education-Based Classification (School K-12, Entrances, Civil Services, Defence)
 * 2. Exam-Based Classification (CBSE, TN State Board, JEE, NEET, UPSC, TNPSC, ICSE)
 * 3. Class-Based Classification (Class 10, Class 12, UG Entrance, Graduate Level)
 * 4. Subject-Based Disciplinary Classification (Maths, Sciences, Social, Languages, Tech/Commerce, GS)
 *
 * Route: /lessons
 */
import { useEffect, useState, useCallback, useMemo } from 'react'
import { useSearchParams, Link } from 'react-router-dom'
import { fetchChapters, fetchChapterDetail, askGeminiDoubt, getProxyPdfUrl } from '../../api/client'
import { PageSkeleton } from '../../components/ui/Skeleton'
import { useToastStore } from '../../store'
import { useSEO } from '../../hooks/useSEO'

// ── 1. EDUCATION-BASED CLASSIFICATION ─────────────────────────────────────────
const EDUCATION_SECTORS = [
  { id: '', label: '🌐 All Education Systems', icon: '🌐', desc: 'Browse all academic domains' },
  { id: 'school', label: '🏫 School Education (K-12 Boards)', icon: '🏫', desc: 'CBSE, ICSE & State Boards (Class 10 & 12)' },
  { id: 'entrance', label: '🎯 National Competitive Entrances', icon: '🎯', desc: 'Engineering (JEE) & Medical (NEET UG)' },
  { id: 'civil_services', label: '🏛️ Civil & Public Administrative Services', icon: '🏛️', desc: 'UPSC (IAS/IPS/IFS) & TNPSC (Group 1, 2, 4, VAO)' },
  { id: 'defence', label: '🛡️ Defence & Technical Services', icon: '🛡️', desc: 'NDA, CDS, CAPF, ESE/IES, CMS' },
]

// ── 2. EXAM-BASED CLASSIFICATION ──────────────────────────────────────────────
const EXAM_TYPES = [
  { id: '', label: 'All Examinations', badge: 'All' },
  { id: 'cbse', label: 'CBSE Board (Class 10 & 12)', badge: 'CBSE' },
  { id: 'tn-board', label: 'Tamil Nadu State Board (SSLC & HSC)', badge: 'TN DGE' },
  { id: 'jee', label: 'JEE (Main & Advanced)', badge: 'NTA' },
  { id: 'neet', label: 'NEET UG (Medical Entrance)', badge: 'NTA' },
  { id: 'upsc', label: 'UPSC Civil Services (Prelims & Mains)', badge: 'UPSC' },
  { id: 'tnpsc', label: 'TNPSC (Group 1, 2, 4 & VAO)', badge: 'TNPSC' },
  { id: 'icse', label: 'CISCE (ICSE Class 10 & ISC 12)', badge: 'ICSE' },
  { id: 'state-boards', label: 'Other State Boards (UP, Bihar, Maharashtra, Rajasthan)', badge: 'State' },
]

// ── 3. CLASS / LEVEL-BASED CLASSIFICATION ─────────────────────────────────────
const CLASS_LEVELS = [
  { id: '', label: 'All Standards / Levels', badge: 'All' },
  { id: 'Class 10', label: 'Class 10 (Secondary School Leaving Certificate / SSLC)', badge: '10th' },
  { id: 'Class 12', label: 'Class 12 (Higher Secondary / HSC / +2)', badge: '12th' },
  { id: 'JEE', label: 'Pre-University / Engineering Entrance Level', badge: 'UG Entrance' },
  { id: 'NEET', label: 'Pre-Medical / Medical Entrance Level', badge: 'Medical Entrance' },
  { id: 'UPSC', label: 'Graduate Level / All-India Civil Services', badge: 'Graduate' },
  { id: 'TNPSC', label: 'State Administrative / Group 1, 2, 4 & VAO Level', badge: 'State Level' },
]

// ── 4. SUBJECT-BASED DISCIPLINARY DOMAINS ────────────────────────────────────
const SUBJECT_DOMAINS = [
  {
    id: '',
    label: 'All Disciplinary Subjects',
    icon: '📚'
  },
  {
    id: 'math',
    label: '📐 Mathematics & Quantitative Aptitude',
    icon: '📐',
    subjects: ['Mathematics', 'Algebra', 'Geometry', 'Trigonometry', 'Calculus', 'Statistics', 'Aptitude']
  },
  {
    id: 'science',
    label: '🔬 Sciences & Applied Physics/Chemistry/Biology',
    icon: '🔬',
    subjects: ['Science', 'Physics', 'Chemistry', 'Biology', 'Botany', 'Zoology']
  },
  {
    id: 'social',
    label: '🌍 Social Sciences, History & Humanities',
    icon: '🌍',
    subjects: ['Social Science', 'History', 'Geography', 'Polity', 'Civics', 'Economics']
  },
  {
    id: 'languages',
    label: '🗣️ Languages & Literature',
    icon: '🗣️',
    subjects: ['English', 'Tamil', 'General Tamil', 'Hindi', 'Sanskrit', 'Arabic']
  },
  {
    id: 'tech_commerce',
    label: '💻 Computer Science, Commerce & Vocational',
    icon: '💻',
    subjects: ['Information Technology', 'Computer Science', 'Computer Applications', 'Artificial Intelligence', 'Accountancy', 'Business Studies']
  },
  {
    id: 'general_studies',
    label: '🏛️ General Studies, Governance & CSAT',
    icon: '🏛️',
    subjects: ['General Studies', 'CSAT', 'Mental Ability', 'Logical Reasoning', 'Current Affairs', 'General Knowledge']
  }
]

export default function LessonsPage() {
  const [searchParams, setSearchParams] = useSearchParams()
  const initialStd = searchParams.get('standard') || ''
  const initialSubj = searchParams.get('subject') || ''
  const initialEdu = searchParams.get('education') || ''
  const initialExam = searchParams.get('exam') || ''
  const initialDomain = searchParams.get('domain') || ''

  // 4-Axis Classification State
  const [activeTier, setActiveTier] = useState('education') // 'education' | 'exam' | 'class' | 'subject'
  const [educationFilter, setEducationFilter] = useState(initialEdu)
  const [examFilter, setExamFilter] = useState(initialExam)
  const [classFilter, setClassFilter] = useState(initialStd)
  const [domainFilter, setDomainFilter] = useState(initialDomain)
  const [subjectFilter, setSubjectFilter] = useState(initialSubj)
  const [searchQuery, setSearchQuery] = useState('')

  const [chapters, setChapters] = useState([])
  const [loading, setLoading] = useState(true)

  // Selected Chapter Modal / Workspace
  const [activeChapterId, setActiveChapterId] = useState(null)
  const [chapterDetail, setChapterDetail] = useState(null)
  const [detailLoading, setDetailLoading] = useState(false)
  const [activeTab, setActiveTab] = useState('questions') // 'questions' | 'textbook' | 'ai'

  // Question Answer Reveals
  const [revealedAnswers, setRevealedAnswers] = useState({})

  // Gemini AI on this Lesson
  const [aiPrompt, setAiPrompt] = useState('')
  const [aiLoading, setAiLoading] = useState(false)
  const [aiResponse, setAiResponse] = useState(null)

  const { addToast } = useToastStore()

  useSEO({
    title: 'Curriculum Lessons Hub — 4-Tier Academic Classification | ExamVault',
    description: 'Master every lesson across School Education, Entrance Exams, Civil Services, and Defence. Explore textbook chapters, past board questions, and verified marking scheme solutions.',
  })

  // Load all curriculum chapters
  const loadChapters = useCallback(async () => {
    setLoading(true)
    try {
      const res = await fetchChapters()
      setChapters(res.chapters || [])
    } catch {
      setChapters([])
    } finally {
      setLoading(false)
    }
  }, [])

  useEffect(() => {
    loadChapters()
  }, [loadChapters])

  // Sync state to URL search params
  useEffect(() => {
    const params = {}
    if (educationFilter) params.education = educationFilter
    if (examFilter) params.exam = examFilter
    if (classFilter) params.standard = classFilter
    if (domainFilter) params.domain = domainFilter
    if (subjectFilter) params.subject = subjectFilter
    setSearchParams(params, { replace: true })
  }, [educationFilter, examFilter, classFilter, domainFilter, subjectFilter, setSearchParams])

  // Extract distinct available subjects across loaded chapters
  const allUniqueSubjects = useMemo(() => {
    const set = new Set()
    chapters.forEach(c => {
      if (c.subject_name) set.add(c.subject_name)
    })
    return Array.from(set).sort()
  }, [chapters])

  // Filter chapters across all 4 Classification Axes + Search
  const filteredChapters = useMemo(() => {
    return chapters.filter(c => {
      // 1. Education Sector Filter
      if (educationFilter === 'school') {
        if (!['Class 10', 'Class 12'].includes(c.standard_level)) return false
      } else if (educationFilter === 'entrance') {
        if (!['JEE', 'NEET'].includes(c.standard_level)) return false
      } else if (educationFilter === 'civil_services') {
        if (!['UPSC', 'TNPSC'].includes(c.standard_level)) return false
      } else if (educationFilter === 'defence') {
        if (!['NDA', 'CDS', 'Defence'].includes(c.standard_level)) return false
      }

      // 2. Exam Filter
      if (examFilter === 'cbse') {
        if (!c.board.includes('CBSE') && !c.exam_slug.includes('class-10') && !c.exam_slug.includes('class-12')) return false
      } else if (examFilter === 'tn-board') {
        if (!c.board.includes('State') && c.exam_slug !== 'tnpsc' && !c.subject_name.includes('Tamil')) return false
      } else if (examFilter === 'jee') {
        if (c.standard_level !== 'JEE' && c.exam_slug !== 'jee') return false
      } else if (examFilter === 'neet') {
        if (c.standard_level !== 'NEET' && c.exam_slug !== 'neet') return false
      } else if (examFilter === 'upsc') {
        if (c.standard_level !== 'UPSC' && c.exam_slug !== 'upsc') return false
      } else if (examFilter === 'tnpsc') {
        if (c.standard_level !== 'TNPSC' && c.exam_slug !== 'tnpsc') return false
      } else if (examFilter === 'icse') {
        if (!c.board.includes('ICSE') && !c.exam_slug.includes('icse')) return false
      } else if (examFilter === 'state-boards') {
        if (!c.board.includes('State')) return false
      }

      // 3. Class / Standard Filter
      if (classFilter && c.standard_level !== classFilter) {
        return false
      }

      // 4. Disciplinary Domain Filter
      if (domainFilter) {
        const domainObj = SUBJECT_DOMAINS.find(d => d.id === domainFilter)
        if (domainObj && domainObj.subjects && !domainObj.subjects.includes(c.subject_name)) {
          return false
        }
      }

      // 5. Specific Subject Filter
      if (subjectFilter && c.subject_name.toLowerCase() !== subjectFilter.toLowerCase()) {
        return false
      }

      // 6. Search Query
      if (searchQuery) {
        const q = searchQuery.toLowerCase().trim()
        const matchTitle = c.chapter_title.toLowerCase().includes(q)
        const matchNotes = c.summary_notes && c.summary_notes.toLowerCase().includes(q)
        const matchSubj = c.subject_name && c.subject_name.toLowerCase().includes(q)
        const matchBoard = c.board && c.board.toLowerCase().includes(q)
        if (!matchTitle && !matchNotes && !matchSubj && !matchBoard) return false
      }

      return true
    })
  }, [chapters, educationFilter, examFilter, classFilter, domainFilter, subjectFilter, searchQuery])

  // Count active filters
  const activeFiltersCount = useMemo(() => {
    let count = 0
    if (educationFilter) count++
    if (examFilter) count++
    if (classFilter) count++
    if (domainFilter) count++
    if (subjectFilter) count++
    if (searchQuery) count++
    return count
  }, [educationFilter, examFilter, classFilter, domainFilter, subjectFilter, searchQuery])

  const clearAllFilters = () => {
    setEducationFilter('')
    setExamFilter('')
    setClassFilter('')
    setDomainFilter('')
    setSubjectFilter('')
    setSearchQuery('')
    addToast('Filters reset to show all curriculum lessons.', 'info')
  }

  const handleOpenChapter = async (chapId, tab = 'questions') => {
    setActiveChapterId(chapId)
    setActiveTab(tab)
    setDetailLoading(true)
    setAiResponse(null)
    setAiPrompt('')
    try {
      const detail = await fetchChapterDetail(chapId)
      setChapterDetail(detail)
    } catch {
      addToast('Could not load chapter details', 'error')
    } finally {
      setDetailLoading(false)
    }
  }

  const toggleAnswer = (qId) => {
    setRevealedAnswers(prev => ({ ...prev, [qId]: !prev[qId] }))
  }

  const handleAskGemini = async (preset = null) => {
    const query = preset || aiPrompt
    if (!query) {
      addToast('Please enter your doubt or question', 'error')
      return
    }
    setAiLoading(true)
    try {
      const res = await askGeminiDoubt({
        question_text: `Lesson: ${chapterDetail?.chapter_title} (${chapterDetail?.standard_level} - ${chapterDetail?.subject_name})`,
        user_query: query,
        mode: 'step_by_step'
      })
      setAiResponse(res.solution)
      addToast('AI explanation generated!', 'success')
    } catch {
      addToast('Gemini AI request failed. Please try again.', 'error')
    } finally {
      setAiLoading(false)
    }
  }

  return (
    <div className="page-content">
      <div className="container" style={{ maxWidth: 1200 }}>

        {/* ── HEADER & BREADCRUMBS ────────────────────────────────────────── */}
        <div style={{ marginBottom: 24 }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: 12, marginBottom: 8 }}>
            <span style={{ fontSize: '2rem' }}>📑</span>
            <div>
              <h1 style={{ fontSize: 'clamp(1.6rem, 3.2vw, 2.3rem)', margin: 0, color: 'var(--text-primary)', fontWeight: 800 }}>
                Curriculum Lessons & Academic Knowledge Base
              </h1>
              <p style={{ color: 'var(--text-secondary)', fontSize: '0.95rem', margin: '4px 0 0', lineHeight: 1.5 }}>
                Categorized across <strong>Education Systems</strong>, <strong>Examinations</strong>, <strong>Classes / Standards</strong>, and <strong>Disciplinary Subject Domains</strong>.
                Nothing left outside.
              </p>
            </div>
          </div>
        </div>

        {/* ── 4-TIER CLASSIFICATION NAVIGATION PANEL ──────────────────────── */}
        <div style={{
          backgroundColor: '#ffffff',
          borderRadius: '16px',
          border: '1px solid var(--color-border)',
          boxShadow: '0 4px 20px rgba(0,0,0,0.03)',
          padding: '20px 24px',
          marginBottom: 28
        }}>
          {/* Top Axis Tabs */}
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: 14, borderBottom: '1px solid #E5E7EB', paddingBottom: 14, marginBottom: 18 }}>
            <div style={{ display: 'flex', gap: 8, flexWrap: 'wrap' }}>
              {[
                { id: 'education', label: '🏫 1. Education-Based', count: EDUCATION_SECTORS.length - 1 },
                { id: 'exam', label: '📝 2. Exam-Based', count: EXAM_TYPES.length - 1 },
                { id: 'class', label: '🎓 3. Class-Based', count: CLASS_LEVELS.length - 1 },
                { id: 'subject', label: '📚 4. Subject-Based', count: allUniqueSubjects.length },
              ].map(tier => (
                <button
                  key={tier.id}
                  onClick={() => setActiveTier(tier.id)}
                  style={{
                    padding: '8px 16px',
                    borderRadius: '8px',
                    border: 'none',
                    fontWeight: activeTier === tier.id ? 700 : 500,
                    fontSize: '0.875rem',
                    cursor: 'pointer',
                    backgroundColor: activeTier === tier.id ? '#8B5CF6' : '#F3F4F6',
                    color: activeTier === tier.id ? '#ffffff' : '#4B5563',
                    transition: 'all 0.15s ease'
                  }}
                >
                  {tier.label}
                </button>
              ))}
            </div>

            {/* Quick Live Search Bar */}
            <div style={{ display: 'flex', alignItems: 'center', gap: 8, flex: '1 1 260px', maxWidth: 360 }}>
              <input
                type="text"
                placeholder="Search across all 76 lessons & topics..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                style={{
                  width: '100%',
                  padding: '8px 14px',
                  borderRadius: '8px',
                  border: '1px solid var(--color-border)',
                  backgroundColor: 'var(--color-bg)',
                  fontSize: '0.85rem',
                  color: 'var(--text-primary)'
                }}
              />
              {searchQuery && (
                <button
                  onClick={() => setSearchQuery('')}
                  style={{ border: 'none', background: 'none', cursor: 'pointer', fontSize: '1rem', color: '#9CA3AF' }}
                  title="Clear search"
                >
                  ✕
                </button>
              )}
            </div>
          </div>

          {/* ── TIER 1: EDUCATION-BASED CONTROLS ── */}
          {activeTier === 'education' && (
            <div>
              <div style={{ fontSize: '0.8125rem', fontWeight: 600, color: 'var(--text-muted)', marginBottom: 10, textTransform: 'uppercase', letterSpacing: '0.04em' }}>
                Select Educational Sector / Domain
              </div>
              <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(220px, 1fr))', gap: 12 }}>
                {EDUCATION_SECTORS.map(sec => {
                  const isSelected = educationFilter === sec.id
                  return (
                    <div
                      key={sec.id}
                      onClick={() => setEducationFilter(sec.id)}
                      style={{
                        padding: '12px 16px',
                        borderRadius: '12px',
                        border: isSelected ? '2px solid #8B5CF6' : '1px solid var(--color-border)',
                        backgroundColor: isSelected ? '#F5F3FF' : '#FAFAFA',
                        cursor: 'pointer',
                        transition: 'all 0.15s ease'
                      }}
                    >
                      <div style={{ fontWeight: 700, fontSize: '0.9rem', color: isSelected ? '#6D28D9' : 'var(--text-primary)', marginBottom: 4 }}>
                        {sec.label}
                      </div>
                      <div style={{ fontSize: '0.75rem', color: 'var(--text-secondary)', lineHeight: 1.3 }}>
                        {sec.desc}
                      </div>
                    </div>
                  )
                })}
              </div>
            </div>
          )}

          {/* ── TIER 2: EXAM-BASED CONTROLS ── */}
          {activeTier === 'exam' && (
            <div>
              <div style={{ fontSize: '0.8125rem', fontWeight: 600, color: 'var(--text-muted)', marginBottom: 10, textTransform: 'uppercase', letterSpacing: '0.04em' }}>
                Filter by Statutory Examination Authority
              </div>
              <div className="filter-chips">
                {EXAM_TYPES.map(ex => {
                  const isSelected = examFilter === ex.id
                  return (
                    <button
                      key={ex.id}
                      className={`filter-chip ${isSelected ? 'active' : ''}`}
                      onClick={() => setExamFilter(ex.id)}
                      style={isSelected ? { backgroundColor: '#8B5CF6', borderColor: '#8B5CF6', color: '#fff' } : {}}
                    >
                      {ex.label}
                    </button>
                  )
                })}
              </div>
            </div>
          )}

          {/* ── TIER 3: CLASS / LEVEL-BASED CONTROLS ── */}
          {activeTier === 'class' && (
            <div>
              <div style={{ fontSize: '0.8125rem', fontWeight: 600, color: 'var(--text-muted)', marginBottom: 10, textTransform: 'uppercase', letterSpacing: '0.04em' }}>
                Filter by Academic Class / Standard / Level
              </div>
              <div className="filter-chips">
                {CLASS_LEVELS.map(cl => {
                  const isSelected = classFilter === cl.id
                  return (
                    <button
                      key={cl.id}
                      className={`filter-chip ${isSelected ? 'active' : ''}`}
                      onClick={() => setClassFilter(cl.id)}
                      style={isSelected ? { backgroundColor: '#8B5CF6', borderColor: '#8B5CF6', color: '#fff' } : {}}
                    >
                      {cl.label}
                    </button>
                  )
                })}
              </div>
            </div>
          )}

          {/* ── TIER 4: SUBJECT-BASED DISCIPLINARY CONTROLS ── */}
          {activeTier === 'subject' && (
            <div>
              <div style={{ fontSize: '0.8125rem', fontWeight: 600, color: 'var(--text-muted)', marginBottom: 10, textTransform: 'uppercase', letterSpacing: '0.04em' }}>
                Disciplinary Domains (No Subject Left Outside)
              </div>
              <div className="filter-chips" style={{ marginBottom: 14 }}>
                {SUBJECT_DOMAINS.map(dom => {
                  const isSelected = domainFilter === dom.id
                  return (
                    <button
                      key={dom.id}
                      className={`filter-chip ${isSelected ? 'active' : ''}`}
                      onClick={() => {
                        setDomainFilter(dom.id)
                        setSubjectFilter('')
                      }}
                      style={isSelected ? { backgroundColor: '#8B5CF6', borderColor: '#8B5CF6', color: '#fff' } : {}}
                    >
                      {dom.label}
                    </button>
                  )
                })}
              </div>

              {/* Individual Subject Chips */}
              <div style={{ fontSize: '0.75rem', fontWeight: 600, color: '#6B7280', marginBottom: 8 }}>
                Specific Subject:
              </div>
              <div className="filter-chips">
                <button
                  className={`filter-chip ${subjectFilter === '' ? 'active' : ''}`}
                  onClick={() => setSubjectFilter('')}
                >
                  All ({allUniqueSubjects.length} Subjects)
                </button>
                {allUniqueSubjects.map(sub => {
                  const isSelected = subjectFilter.toLowerCase() === sub.toLowerCase()
                  return (
                    <button
                      key={sub}
                      className={`filter-chip ${isSelected ? 'active' : ''}`}
                      onClick={() => setSubjectFilter(sub)}
                      style={isSelected ? { backgroundColor: '#10B981', borderColor: '#10B981', color: '#fff' } : {}}
                    >
                      {sub}
                    </button>
                  )
                })}
              </div>
            </div>
          )}

          {/* ── ACTIVE FILTER BREADCRUMB BADGES & CLEAR BUTTON ── */}
          {activeFiltersCount > 0 && (
            <div style={{ marginTop: 16, paddingTop: 14, borderTop: '1px solid #F3F4F6', display: 'flex', alignItems: 'center', justifyContent: 'space-between', flexWrap: 'wrap', gap: 10 }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: 8, flexWrap: 'wrap', fontSize: '0.8125rem' }}>
                <span style={{ fontWeight: 600, color: '#6B7280' }}>Active Filters ({activeFiltersCount}):</span>
                {educationFilter && (
                  <span style={{ backgroundColor: '#EDE9FE', color: '#6D28D9', padding: '3px 9px', borderRadius: '12px', fontWeight: 600 }}>
                    Edu: {educationFilter} <span style={{ cursor: 'pointer', marginLeft: 4 }} onClick={() => setEducationFilter('')}>✕</span>
                  </span>
                )}
                {examFilter && (
                  <span style={{ backgroundColor: '#EDE9FE', color: '#6D28D9', padding: '3px 9px', borderRadius: '12px', fontWeight: 600 }}>
                    Exam: {examFilter} <span style={{ cursor: 'pointer', marginLeft: 4 }} onClick={() => setExamFilter('')}>✕</span>
                  </span>
                )}
                {classFilter && (
                  <span style={{ backgroundColor: '#EDE9FE', color: '#6D28D9', padding: '3px 9px', borderRadius: '12px', fontWeight: 600 }}>
                    Class: {classFilter} <span style={{ cursor: 'pointer', marginLeft: 4 }} onClick={() => setClassFilter('')}>✕</span>
                  </span>
                )}
                {domainFilter && (
                  <span style={{ backgroundColor: '#EDE9FE', color: '#6D28D9', padding: '3px 9px', borderRadius: '12px', fontWeight: 600 }}>
                    Domain: {domainFilter} <span style={{ cursor: 'pointer', marginLeft: 4 }} onClick={() => setDomainFilter('')}>✕</span>
                  </span>
                )}
                {subjectFilter && (
                  <span style={{ backgroundColor: '#D1FAE5', color: '#065F46', padding: '3px 9px', borderRadius: '12px', fontWeight: 600 }}>
                    Subject: {subjectFilter} <span style={{ cursor: 'pointer', marginLeft: 4 }} onClick={() => setSubjectFilter('')}>✕</span>
                  </span>
                )}
                {searchQuery && (
                  <span style={{ backgroundColor: '#FEF3C7', color: '#92400E', padding: '3px 9px', borderRadius: '12px', fontWeight: 600 }}>
                    Keyword: "{searchQuery}" <span style={{ cursor: 'pointer', marginLeft: 4 }} onClick={() => setSearchQuery('')}>✕</span>
                  </span>
                )}
              </div>

              <button
                className="btn btn-ghost btn-sm"
                onClick={clearAllFilters}
                style={{ fontSize: '0.78rem', color: '#EF4444', borderColor: '#FECACA' }}
              >
                Clear All Filters
              </button>
            </div>
          )}
        </div>

        {/* ── ACTIVE LESSON MODAL / WORKSPACE ────────────────────────────── */}
        {activeChapterId && chapterDetail && (
          <div style={{
            marginBottom: 32,
            padding: '24px',
            backgroundColor: '#ffffff',
            borderRadius: '16px',
            border: '2px solid #8B5CF6',
            boxShadow: '0 8px 30px rgba(139, 92, 246, 0.12)'
          }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', flexWrap: 'wrap', gap: 12, marginBottom: 16 }}>
              <div>
                <div style={{ display: 'flex', gap: 8, alignItems: 'center', marginBottom: 6 }}>
                  <span style={{
                    fontSize: '0.72rem',
                    fontWeight: 700,
                    padding: '3px 8px',
                    borderRadius: '6px',
                    backgroundColor: '#EDE9FE',
                    color: '#6D28D9'
                  }}>
                    {chapterDetail.standard_level} · {chapterDetail.subject_name}
                  </span>
                  <span style={{
                    fontSize: '0.72rem',
                    fontWeight: 600,
                    padding: '3px 8px',
                    borderRadius: '6px',
                    backgroundColor: '#F3F4F6',
                    color: '#374151'
                  }}>
                    Weightage: {chapterDetail.marks_weightage}
                  </span>
                  <span style={{
                    fontSize: '0.72rem',
                    fontWeight: 600,
                    padding: '3px 8px',
                    borderRadius: '6px',
                    backgroundColor: '#ECFDF5',
                    color: '#065F46'
                  }}>
                    {chapterDetail.board}
                  </span>
                </div>
                <h2 style={{ fontSize: '1.45rem', margin: 0, color: '#1F2937' }}>
                  Chapter {chapterDetail.chapter_number}: {chapterDetail.chapter_title}
                </h2>
              </div>

              <button
                className="btn btn-ghost btn-sm"
                onClick={() => {
                  setActiveChapterId(null)
                  setChapterDetail(null)
                }}
                style={{ fontSize: '0.85rem' }}
              >
                ✕ Close Lesson
              </button>
            </div>

            {/* Lesson Summary Notes */}
            {chapterDetail.summary_notes && (
              <div style={{
                padding: '12px 16px',
                backgroundColor: '#F9FAFB',
                borderRadius: '8px',
                border: '1px solid #E5E7EB',
                marginBottom: 18,
                fontSize: '0.875rem',
                color: '#4B5563',
                lineHeight: 1.5
              }}>
                <strong style={{ color: '#111827' }}>💡 Chapter Blueprint & Core Concepts: </strong>
                {chapterDetail.summary_notes}
              </div>
            )}

            {/* Tab Navigation */}
            <div style={{ display: 'flex', gap: 10, borderBottom: '1px solid #E5E7EB', paddingBottom: 10, marginBottom: 20 }}>
              <button
                className={`btn ${activeTab === 'questions' ? 'btn-primary' : 'btn-ghost'} btn-sm`}
                onClick={() => setActiveTab('questions')}
                style={{ fontWeight: 600 }}
              >
                ❓ Curated Past Board Questions ({chapterDetail.questions?.length || 0})
              </button>
              <button
                className={`btn ${activeTab === 'textbook' ? 'btn-primary' : 'btn-ghost'} btn-sm`}
                onClick={() => setActiveTab('textbook')}
                style={{ fontWeight: 600 }}
              >
                📖 Read Prescribed Textbook Chapter PDF
              </button>
              <button
                className={`btn ${activeTab === 'ai' ? 'btn-primary' : 'btn-ghost'} btn-sm`}
                onClick={() => setActiveTab('ai')}
                style={{
                  fontWeight: 600,
                  backgroundColor: activeTab === 'ai' ? '#7C3AED' : 'transparent',
                  borderColor: '#7C3AED',
                  color: activeTab === 'ai' ? '#fff' : '#7C3AED'
                }}
              >
                ✨ Ask Gemini AI on this Lesson
              </button>
            </div>

            {/* TAB 1: QUESTIONS & STEP-BY-STEP SOLUTIONS */}
            {activeTab === 'questions' && (
              <div style={{ display: 'flex', flexDirection: 'column', gap: 16 }}>
                {chapterDetail.questions?.length === 0 ? (
                  <div className="empty-state">
                    <p>No curated questions recorded for this lesson yet.</p>
                  </div>
                ) : (
                  chapterDetail.questions?.map((q, idx) => (
                    <div
                      key={q.id}
                      style={{
                        padding: '16px 20px',
                        backgroundColor: '#F9FAFB',
                        borderRadius: '12px',
                        border: '1px solid #E5E7EB'
                      }}
                    >
                      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 10, flexWrap: 'wrap', gap: 6 }}>
                        <div style={{ display: 'flex', gap: 6, alignItems: 'center' }}>
                          <span style={{ fontWeight: 700, fontSize: '0.85rem', color: '#1F2937' }}>
                            Q{idx + 1} ({q.question_type})
                          </span>
                          <span style={{ fontSize: '0.72rem', backgroundColor: '#E0E7FF', color: '#4338CA', padding: '2px 7px', borderRadius: '4px', fontWeight: 600 }}>
                            {q.marks} Mark{q.marks > 1 ? 's' : ''}
                          </span>
                          <span style={{ fontSize: '0.72rem', backgroundColor: '#FEF3C7', color: '#92400E', padding: '2px 7px', borderRadius: '4px', fontWeight: 600 }}>
                            {q.difficulty}
                          </span>
                        </div>
                        <span style={{ fontSize: '0.75rem', color: '#6B7280', fontStyle: 'italic' }}>
                          🏛️ {q.source_publication} {q.year ? `(${q.year})` : ''}
                        </span>
                      </div>

                      <div style={{ fontSize: '0.9375rem', color: '#111827', fontWeight: 500, lineHeight: 1.5, marginBottom: 12 }}>
                        {q.question_text}
                      </div>

                      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                        <button
                          className="btn btn-ghost btn-sm"
                          onClick={() => toggleAnswer(q.id)}
                          style={{ fontSize: '0.78rem', color: '#4F46E5', borderColor: '#C7D2FE', fontWeight: 600 }}
                        >
                          {revealedAnswers[q.id] ? '▲ Hide Solution' : '▼ View Step-by-Step Solution'}
                        </button>
                        <button
                          className="btn btn-ghost btn-sm"
                          onClick={() => {
                            setActiveTab('ai')
                            setAiPrompt(`Explain the solution and concepts for this question: "${q.question_text}"`)
                            handleAskGemini(`Explain the solution and concepts for this question: "${q.question_text}"`)
                          }}
                          style={{ fontSize: '0.75rem', color: '#7C3AED' }}
                        >
                          ✨ Ask AI to Explain
                        </button>
                      </div>

                      {revealedAnswers[q.id] && (
                        <div style={{
                          marginTop: 12,
                          padding: '12px 16px',
                          backgroundColor: '#F0FDF4',
                          border: '1px solid #BBF7D0',
                          borderRadius: '8px',
                          fontSize: '0.875rem',
                          lineHeight: 1.6,
                          color: '#166534'
                        }}>
                          <strong>Official Solution / Marking Criteria:</strong>
                          <div style={{ marginTop: 6, whiteSpace: 'pre-wrap' }}>
                            {q.answer_explanation}
                          </div>
                        </div>
                      )}
                    </div>
                  ))
                )}
              </div>
            )}

            {/* TAB 2: TEXTBOOK CHAPTER PDF */}
            {activeTab === 'textbook' && (
              <div>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 12 }}>
                  <span style={{ fontSize: '0.85rem', fontWeight: 600, color: '#374151' }}>
                    📖 Prescribed Textbook Chapter PDF
                  </span>
                  {chapterDetail.textbook_chapter_url && (
                    <a
                      href={chapterDetail.textbook_chapter_url}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="btn btn-primary btn-sm"
                      style={{ fontSize: '0.75rem' }}
                    >
                      ↗ Open Full Screen in New Tab
                    </a>
                  )}
                </div>
                {chapterDetail.textbook_chapter_url ? (
                  <div style={{ height: '750px', backgroundColor: '#525659', borderRadius: '10px', overflow: 'hidden' }}>
                    <iframe
                      src={`${getProxyPdfUrl(chapterDetail.textbook_chapter_url)}#toolbar=1&navpanes=0`}
                      title={chapterDetail.chapter_title}
                      width="100%"
                      height="100%"
                      style={{ border: 'none', display: 'block' }}
                    />
                  </div>
                ) : (
                  <div className="empty-state">
                    <p>Textbook chapter stream is being synchronized for this lesson.</p>
                  </div>
                )}
              </div>
            )}

            {/* TAB 3: ASK GEMINI AI */}
            {activeTab === 'ai' && (
              <div style={{
                padding: '18px 20px',
                backgroundColor: '#F5F3FF',
                borderRadius: '12px',
                border: '1px solid #DDD6FE'
              }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: 8, marginBottom: 10 }}>
                  <span style={{ fontSize: '1.25rem' }}>✨</span>
                  <span style={{ fontWeight: 700, fontSize: '0.95rem', color: '#5B21B6' }}>
                    Gemini AI Lesson Tutor: Chapter {chapterDetail.chapter_number}
                  </span>
                </div>
                <textarea
                  value={aiPrompt}
                  onChange={(e) => setAiPrompt(e.target.value)}
                  placeholder="Ask any doubt about this lesson (e.g. 'Explain the reaction mechanism with balanced equations', 'Give 3 practice questions on this topic')..."
                  rows={3}
                  style={{
                    width: '100%',
                    padding: '10px 12px',
                    borderRadius: '8px',
                    border: '1px solid #C4B5FD',
                    fontFamily: 'inherit',
                    fontSize: '0.875rem',
                    marginBottom: 10,
                    backgroundColor: '#fff'
                  }}
                />
                <div style={{ display: 'flex', justifyContent: 'flex-end', gap: 8 }}>
                  <button
                    className="btn btn-primary btn-sm"
                    style={{ backgroundColor: '#7C3AED', borderColor: '#7C3AED', fontWeight: 600 }}
                    onClick={() => handleAskGemini()}
                    disabled={aiLoading}
                  >
                    {aiLoading ? '⏳ Generating Explanation...' : '✨ Ask Gemini'}
                  </button>
                </div>

                {aiResponse && (
                  <div style={{
                    marginTop: 16,
                    padding: '14px 18px',
                    backgroundColor: '#ffffff',
                    border: '1px solid #C4B5FD',
                    borderRadius: '8px',
                    fontSize: '0.875rem',
                    lineHeight: 1.65,
                    color: '#1F2937',
                    whiteSpace: 'pre-wrap'
                  }}>
                    {aiResponse}
                  </div>
                )}
              </div>
            )}
          </div>
        )}

        {/* ── CHAPTERS GRID HEADER & COUNT ─────────────────────────────────── */}
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 18, flexWrap: 'wrap', gap: 10 }}>
          <div style={{ fontWeight: 700, fontSize: '1.1rem', color: 'var(--text-primary)' }}>
            Showing {filteredChapters.length} Curriculum Lessons
          </div>
          <div style={{ fontSize: '0.8125rem', color: 'var(--text-muted)' }}>
            Total Curriculum Base: <strong>{chapters.length} Lessons</strong> across <strong>{allUniqueSubjects.length} Subjects</strong>
          </div>
        </div>

        {/* ── CHAPTERS LISTING ────────────────────────────────────────────── */}
        {loading && <PageSkeleton count={6} />}

        {!loading && filteredChapters.length === 0 && (
          <div className="empty-state">
            <div className="empty-state-icon">📚</div>
            <h3>No lessons found matching these criteria</h3>
            <p>
              {activeFiltersCount > 0
                ? 'Try broadening your filters or click "Clear All Filters" to view all curriculum lessons.'
                : 'No lessons currently recorded in database.'}
            </p>
            {activeFiltersCount > 0 && (
              <button
                className="btn btn-primary btn-sm"
                onClick={clearAllFilters}
                style={{ marginTop: 12 }}
              >
                Reset All Filters
              </button>
            )}
          </div>
        )}

        {!loading && filteredChapters.length > 0 && (
          <div style={{
            display: 'grid',
            gridTemplateColumns: 'repeat(auto-fill, minmax(340px, 1fr))',
            gap: 20
          }}>
            {filteredChapters.map((chap) => (
              <div
                key={chap.id}
                style={{
                  backgroundColor: '#ffffff',
                  borderRadius: '14px',
                  border: activeChapterId === chap.id ? '2px solid #8B5CF6' : '1px solid var(--color-border)',
                  padding: '18px 22px',
                  boxShadow: 'var(--shadow-sm)',
                  display: 'flex',
                  flexDirection: 'column',
                  justifyContent: 'space-between',
                  gap: 14,
                  transition: 'transform 0.15s ease, box-shadow 0.15s ease'
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
                      {chap.standard_level} · {chap.subject_name}
                    </span>
                    <span style={{ fontSize: '0.75rem', fontWeight: 600, color: '#059669', backgroundColor: '#ECFDF5', padding: '2px 8px', borderRadius: '4px' }}>
                      {chap.marks_weightage}
                    </span>
                  </div>

                  <h3 style={{ fontSize: '1.05rem', margin: '0 0 8px 0', color: 'var(--text-primary)', lineHeight: 1.35 }}>
                    Ch {chap.chapter_number}: {chap.chapter_title}
                  </h3>

                  <p style={{ fontSize: '0.8125rem', color: 'var(--text-secondary)', margin: 0, lineHeight: 1.45, maxHeight: '60px', overflow: 'hidden' }}>
                    {chap.summary_notes}
                  </p>
                </div>

                <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', borderTop: '1px solid #F3F4F6', paddingTop: 12 }}>
                  <span style={{ fontSize: '0.75rem', color: '#6B7280', fontWeight: 600 }}>
                    ❓ {chap.question_count} Curated Questions
                  </span>

                  <div style={{ display: 'flex', gap: 6 }}>
                    <button
                      className="btn btn-ghost btn-sm"
                      style={{ fontSize: '0.75rem', padding: '5px 10px', height: 'auto', color: '#2563EB', borderColor: '#BFDBFE' }}
                      onClick={() => handleOpenChapter(chap.id, 'textbook')}
                      title="Read official textbook chapter"
                    >
                      📖 Book
                    </button>
                    <button
                      className="btn btn-primary btn-sm"
                      style={{ fontSize: '0.75rem', padding: '5px 12px', height: 'auto', backgroundColor: '#8B5CF6', borderColor: '#8B5CF6' }}
                      onClick={() => handleOpenChapter(chap.id, 'questions')}
                    >
                      Explore Lesson →
                    </button>
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}

      </div>
    </div>
  )
}
