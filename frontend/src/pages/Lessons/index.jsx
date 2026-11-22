/**
 * Lessons & Curriculum Learning Hub
 * Multi-Tier Academic Categorization:
 *  1. Exam / Board: CBSE, Tamil Nadu State Board, All State Boards, JEE, NEET, UPSC, TNPSC
 *  2. Class / Standard: Class 10, Class 12, Entrance Level, Graduate Level
 *  3. Subject: Mathematics, Science, Social Science, English, Tamil, Physics, Chemistry, Biology, etc.
 *  4. Education Sector: School K-12, National Entrances, Civil Services, Defence
 *
 * Route: /lessons
 */
import { useEffect, useState, useCallback, useMemo } from 'react'
import { useSearchParams, Link } from 'react-router-dom'
import { fetchChapters, fetchChapterDetail, askGeminiDoubt, getProxyPdfUrl } from '../../api/client'
import { PageSkeleton } from '../../components/ui/Skeleton'
import { useToastStore } from '../../store'
import { useSEO } from '../../hooks/useSEO'

// ── 1. EXAM & BOARD OPTIONS ──────────────────────────────────────────────────
const EXAM_OPTIONS = [
  { id: '', label: 'All Exams & Boards', icon: '📝' },
  { id: 'cbse', label: 'CBSE Board', icon: '🏛️', badge: 'CBSE' },
  { id: 'tn-board', label: 'Tamil Nadu State Board', icon: '🌴', badge: 'TN DGE' },
  { id: 'state-boards', label: 'State Boards (UP/MH/Bihar/RJ)', icon: '🗺️', badge: 'State' },
  { id: 'jee', label: 'JEE (Main & Adv)', icon: '⚛️', badge: 'NTA' },
  { id: 'neet', label: 'NEET UG', icon: '🩺', badge: 'NTA' },
  { id: 'upsc', label: 'UPSC Civil Services', icon: '🇮🇳', badge: 'UPSC' },
  { id: 'tnpsc', label: 'TNPSC Group Exams', icon: '📜', badge: 'TNPSC' },
]

// ── 2. CLASS / STANDARD OPTIONS ─────────────────────────────────────────────
const CLASS_OPTIONS = [
  { id: '', label: 'All Classes' },
  { id: 'Class 10', label: 'Class 10 (SSLC / Secondary)' },
  { id: 'Class 12', label: 'Class 12 (HSC / +2)' },
  { id: 'JEE', label: 'Pre-Engineering (Class 11-12)' },
  { id: 'NEET', label: 'Pre-Medical (Class 11-12)' },
  { id: 'UPSC', label: 'Graduate Civil Services' },
  { id: 'TNPSC', label: 'State Services Level' },
]

// ── 3. EDUCATION SECTOR OPTIONS ─────────────────────────────────────────────
const EDUCATION_OPTIONS = [
  { id: '', label: 'All Education Streams' },
  { id: 'school', label: '🏫 School Education (K-12)' },
  { id: 'entrance', label: '🎯 National Entrances' },
  { id: 'civil_services', label: '🏛️ Civil Services' },
  { id: 'defence', label: '🛡️ Defence & Technical' },
]

// ── SUBJECT COLOR THEMES & ICONS ────────────────────────────────────────────
const SUBJECT_META = {
  'Mathematics': { icon: '📐', bg: '#EFF6FF', border: '#BFDBFE', text: '#1D4ED8', accent: '#3B82F6' },
  'Science': { icon: '🔬', bg: '#ECFDF5', border: '#A7F3D0', text: '#047857', accent: '#10B981' },
  'Social Science': { icon: '🌍', bg: '#FFFBEB', border: '#FDE68A', text: '#B45309', accent: '#F59E0B' },
  'Tamil': { icon: '✍️', bg: '#FAF5FF', border: '#E9D5FF', text: '#7E22CE', accent: '#9333EA' },
  'English': { icon: '📖', bg: '#EEF2FF', border: '#C7D2FE', text: '#4338CA', accent: '#6366F1' },
  'Physics': { icon: '⚛️', bg: '#F0FDF4', border: '#BBF7D0', text: '#15803D', accent: '#22C55E' },
  'Chemistry': { icon: '🧪', bg: '#FFF1F2', border: '#FECDD3', text: '#BE123C', accent: '#F43F5E' },
  'Biology': { icon: '🧬', bg: '#F0FDFA', border: '#99F6E4', text: '#0F766E', accent: '#14B8A6' },
  'General Studies': { icon: '🏛️', bg: '#F8FAFC', border: '#E2E8F0', text: '#334155', accent: '#64748B' },
  'CSAT': { icon: '🧠', bg: '#FDF4FF', border: '#F0ABFC', text: '#86198F', accent: '#C026D3' },
  'Information Technology': { icon: '💻', bg: '#F0F9FF', border: '#BAE6FD', text: '#0369A1', accent: '#0284C7' },
  'Accountancy': { icon: '📊', bg: '#ECFDF5', border: '#A7F3D0', text: '#065F46', accent: '#059669' },
}

export default function LessonsPage() {
  const [searchParams, setSearchParams] = useSearchParams()
  const initialExam = searchParams.get('exam') || ''
  const initialClass = searchParams.get('standard') || ''
  const initialSubject = searchParams.get('subject') || ''
  const initialEdu = searchParams.get('education') || ''

  // Filter state
  const [selectedExam, setSelectedExam] = useState(initialExam)
  const [selectedClass, setSelectedClass] = useState(initialClass)
  const [selectedSubject, setSelectedSubject] = useState(initialSubject)
  const [selectedEdu, setSelectedEdu] = useState(initialEdu)
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
    title: 'Curriculum Lessons Hub — Chapter Questions & Solutions | ExamVault',
    description: 'Master lessons across CBSE, Tamil Nadu State Board, JEE, NEET, and UPSC. Explore syllabus chapters, past board questions, and verified step-by-step solutions.',
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
    if (selectedExam) params.exam = selectedExam
    if (selectedClass) params.standard = selectedClass
    if (selectedSubject) params.subject = selectedSubject
    if (selectedEdu) params.education = selectedEdu
    setSearchParams(params, { replace: true })
  }, [selectedExam, selectedClass, selectedSubject, selectedEdu, setSearchParams])

  // Extract distinct available subjects across loaded chapters
  const allUniqueSubjects = useMemo(() => {
    const set = new Set()
    chapters.forEach(c => {
      if (c.subject_name) set.add(c.subject_name)
    })
    return Array.from(set).sort()
  }, [chapters])

  // Filter chapters
  const filteredChapters = useMemo(() => {
    return chapters.filter(c => {
      // 1. Exam Filter
      if (selectedExam === 'cbse') {
        if (!c.board.includes('CBSE') && !c.exam_slug.includes('class-10') && !c.exam_slug.includes('class-12')) return false
      } else if (selectedExam === 'tn-board') {
        if (!c.board.includes('State') && c.exam_slug !== 'tnpsc' && !c.subject_name.includes('Tamil')) return false
      } else if (selectedExam === 'jee') {
        if (c.standard_level !== 'JEE' && c.exam_slug !== 'jee') return false
      } else if (selectedExam === 'neet') {
        if (c.standard_level !== 'NEET' && c.exam_slug !== 'neet') return false
      } else if (selectedExam === 'upsc') {
        if (c.standard_level !== 'UPSC' && c.exam_slug !== 'upsc') return false
      } else if (selectedExam === 'tnpsc') {
        if (c.standard_level !== 'TNPSC' && c.exam_slug !== 'tnpsc') return false
      } else if (selectedExam === 'state-boards') {
        if (!c.board.includes('State')) return false
      }

      // 2. Class / Standard Filter
      if (selectedClass && c.standard_level !== selectedClass) {
        return false
      }

      // 3. Subject Filter
      if (selectedSubject && c.subject_name.toLowerCase() !== selectedSubject.toLowerCase()) {
        return false
      }

      // 4. Education Sector Filter
      if (selectedEdu === 'school') {
        if (!['Class 10', 'Class 12'].includes(c.standard_level)) return false
      } else if (selectedEdu === 'entrance') {
        if (!['JEE', 'NEET'].includes(c.standard_level)) return false
      } else if (selectedEdu === 'civil_services') {
        if (!['UPSC', 'TNPSC'].includes(c.standard_level)) return false
      } else if (selectedEdu === 'defence') {
        if (!['NDA', 'CDS', 'Defence'].includes(c.standard_level)) return false
      }

      // 5. Search Query
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
  }, [chapters, selectedExam, selectedClass, selectedSubject, selectedEdu, searchQuery])

  // Count active filters
  const activeFiltersCount = useMemo(() => {
    let count = 0
    if (selectedExam) count++
    if (selectedClass) count++
    if (selectedSubject) count++
    if (selectedEdu) count++
    if (searchQuery) count++
    return count
  }, [selectedExam, selectedClass, selectedSubject, selectedEdu, searchQuery])

  const clearAllFilters = () => {
    setSelectedExam('')
    setSelectedClass('')
    setSelectedSubject('')
    setSelectedEdu('')
    setSearchQuery('')
    addToast('Filters reset.', 'info')
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

        {/* ── HEADER ──────────────────────────────────────────────────────── */}
        <div style={{ marginBottom: 24 }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: 12, marginBottom: 8 }}>
            <span style={{ fontSize: '2.2rem' }}>📑</span>
            <div>
              <h1 style={{ fontSize: 'clamp(1.6rem, 3.2vw, 2.2rem)', margin: 0, color: 'var(--text-primary)', fontWeight: 800, letterSpacing: '-0.02em' }}>
                Curriculum Lessons & Question Bank
              </h1>
              <p style={{ color: 'var(--text-secondary)', fontSize: '0.95rem', margin: '4px 0 0', lineHeight: 1.5 }}>
                Structured chapter-wise learning across CBSE, State Boards, JEE, NEET, and UPSC with past board questions, official marking schemes, and textbook readers.
              </p>
            </div>
          </div>
        </div>

        {/* ── CLEAN MULTI-TIER FILTER DASHBOARD ────────────────────────────── */}
        <div style={{
          backgroundColor: '#ffffff',
          borderRadius: '16px',
          border: '1px solid var(--color-border)',
          boxShadow: '0 4px 20px rgba(0,0,0,0.03)',
          padding: '20px 24px',
          marginBottom: 28
        }}>
          
          {/* Row 1: Search & Quick Reset */}
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: 12, marginBottom: 18, borderBottom: '1px solid #F3F4F6', paddingBottom: 14 }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: 10, flex: '1 1 300px' }}>
              <span style={{ fontSize: '1.1rem' }}>🔍</span>
              <input
                type="text"
                placeholder="Search lessons, chapter names, key topics..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                style={{
                  width: '100%',
                  padding: '9px 14px',
                  borderRadius: '10px',
                  border: '1px solid var(--color-border)',
                  backgroundColor: 'var(--color-bg)',
                  fontSize: '0.875rem',
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

            {activeFiltersCount > 0 && (
              <button
                className="btn btn-ghost btn-sm"
                onClick={clearAllFilters}
                style={{ color: '#EF4444', borderColor: '#FECACA', fontSize: '0.8125rem' }}
              >
                Clear All Filters ({activeFiltersCount})
              </button>
            )}
          </div>

          {/* Row 2: 4-Axis Selectors */}
          <div style={{
            display: 'grid',
            gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))',
            gap: 14,
            marginBottom: 16
          }}>
            {/* 1. Exam Selector */}
            <div>
              <label style={{ display: 'block', fontSize: '0.75rem', fontWeight: 700, color: '#4B5563', marginBottom: 6, textTransform: 'uppercase' }}>
                1. Examination / Board
              </label>
              <select
                value={selectedExam}
                onChange={(e) => setSelectedExam(e.target.value)}
                style={{
                  width: '100%',
                  padding: '9px 12px',
                  borderRadius: '8px',
                  border: '1px solid var(--color-border)',
                  backgroundColor: 'var(--color-bg)',
                  fontSize: '0.875rem',
                  color: 'var(--text-primary)',
                  fontWeight: selectedExam ? 600 : 400
                }}
              >
                {EXAM_OPTIONS.map(ex => (
                  <option key={ex.id} value={ex.id}>{ex.label}</option>
                ))}
              </select>
            </div>

            {/* 2. Class / Standard Selector */}
            <div>
              <label style={{ display: 'block', fontSize: '0.75rem', fontWeight: 700, color: '#4B5563', marginBottom: 6, textTransform: 'uppercase' }}>
                2. Class / Standard Level
              </label>
              <select
                value={selectedClass}
                onChange={(e) => setSelectedClass(e.target.value)}
                style={{
                  width: '100%',
                  padding: '9px 12px',
                  borderRadius: '8px',
                  border: '1px solid var(--color-border)',
                  backgroundColor: 'var(--color-bg)',
                  fontSize: '0.875rem',
                  color: 'var(--text-primary)',
                  fontWeight: selectedClass ? 600 : 400
                }}
              >
                {CLASS_OPTIONS.map(cl => (
                  <option key={cl.id} value={cl.id}>{cl.label}</option>
                ))}
              </select>
            </div>

            {/* 3. Subject Selector */}
            <div>
              <label style={{ display: 'block', fontSize: '0.75rem', fontWeight: 700, color: '#4B5563', marginBottom: 6, textTransform: 'uppercase' }}>
                3. Subject
              </label>
              <select
                value={selectedSubject}
                onChange={(e) => setSelectedSubject(e.target.value)}
                style={{
                  width: '100%',
                  padding: '9px 12px',
                  borderRadius: '8px',
                  border: '1px solid var(--color-border)',
                  backgroundColor: 'var(--color-bg)',
                  fontSize: '0.875rem',
                  color: 'var(--text-primary)',
                  fontWeight: selectedSubject ? 600 : 400
                }}
              >
                <option value="">All Subjects ({allUniqueSubjects.length})</option>
                {allUniqueSubjects.map(sub => (
                  <option key={sub} value={sub}>{sub}</option>
                ))}
              </select>
            </div>

            {/* 4. Education Sector Selector */}
            <div>
              <label style={{ display: 'block', fontSize: '0.75rem', fontWeight: 700, color: '#4B5563', marginBottom: 6, textTransform: 'uppercase' }}>
                4. Education Stream
              </label>
              <select
                value={selectedEdu}
                onChange={(e) => setSelectedEdu(e.target.value)}
                style={{
                  width: '100%',
                  padding: '9px 12px',
                  borderRadius: '8px',
                  border: '1px solid var(--color-border)',
                  backgroundColor: 'var(--color-bg)',
                  fontSize: '0.875rem',
                  color: 'var(--text-primary)',
                  fontWeight: selectedEdu ? 600 : 400
                }}
              >
                {EDUCATION_OPTIONS.map(ed => (
                  <option key={ed.id} value={ed.id}>{ed.label}</option>
                ))}
              </select>
            </div>
          </div>

          {/* Quick Subject Pills for Core 10th Subjects */}
          <div style={{ display: 'flex', alignItems: 'center', gap: 6, flexWrap: 'wrap', paddingTop: 8 }}>
            <span style={{ fontSize: '0.75rem', color: '#6B7280', fontWeight: 600 }}>Quick Subjects:</span>
            {['Mathematics', 'Science', 'Social Science', 'English', 'Tamil'].map(sub => {
              const meta = SUBJECT_META[sub] || { icon: '📚' }
              const isSelected = selectedSubject.toLowerCase() === sub.toLowerCase()
              return (
                <button
                  key={sub}
                  onClick={() => setSelectedSubject(isSelected ? '' : sub)}
                  style={{
                    padding: '4px 10px',
                    borderRadius: '16px',
                    border: isSelected ? '1px solid #2563EB' : '1px solid #E5E7EB',
                    backgroundColor: isSelected ? '#EFF6FF' : '#F9FAFB',
                    color: isSelected ? '#1D4ED8' : '#374151',
                    fontSize: '0.78rem',
                    fontWeight: isSelected ? 700 : 500,
                    cursor: 'pointer',
                    display: 'inline-flex',
                    alignItems: 'center',
                    gap: 4,
                    transition: 'all 0.15s ease'
                  }}
                >
                  <span>{meta.icon}</span>
                  <span>{sub}</span>
                </button>
              )
            })}
          </div>

        </div>

        {/* ── ACTIVE LESSON MODAL / WORKSPACE ────────────────────────────── */}
        {activeChapterId && chapterDetail && (
          <div style={{
            marginBottom: 32,
            padding: '24px',
            backgroundColor: '#ffffff',
            borderRadius: '16px',
            border: '2px solid #3B82F6',
            boxShadow: '0 8px 30px rgba(59, 130, 246, 0.12)'
          }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', flexWrap: 'wrap', gap: 12, marginBottom: 16 }}>
              <div>
                <div style={{ display: 'flex', gap: 8, alignItems: 'center', marginBottom: 6, flexWrap: 'wrap' }}>
                  <span style={{
                    fontSize: '0.72rem',
                    fontWeight: 700,
                    padding: '3px 8px',
                    borderRadius: '6px',
                    backgroundColor: '#EFF6FF',
                    color: '#1D4ED8'
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
                    Marks Weightage: {chapterDetail.marks_weightage}
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
                <strong style={{ color: '#111827' }}>💡 Core Concepts & Summary: </strong>
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
                📖 Prescribed Textbook Chapter PDF
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
                          style={{ fontSize: '0.78rem', color: '#2563EB', borderColor: '#BFDBFE', fontWeight: 600 }}
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
                          <strong>Official Solution / Marking Scheme:</strong>
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
            {filteredChapters.map((chap) => {
              const meta = SUBJECT_META[chap.subject_name] || {
                icon: '📚',
                bg: '#F9FAFB',
                border: '#E5E7EB',
                text: '#374151',
                accent: '#6B7280'
              }

              return (
                <div
                  key={chap.id}
                  style={{
                    backgroundColor: '#ffffff',
                    borderRadius: '14px',
                    border: activeChapterId === chap.id ? '2px solid #3B82F6' : '1px solid var(--color-border)',
                    padding: '20px 22px',
                    boxShadow: 'var(--shadow-sm)',
                    display: 'flex',
                    flexDirection: 'column',
                    justifyContent: 'space-between',
                    gap: 14,
                    transition: 'transform 0.15s ease, box-shadow 0.15s ease',
                  }}
                >
                  <div>
                    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 10 }}>
                      <span style={{
                        fontSize: '0.75rem',
                        fontWeight: 700,
                        padding: '3px 9px',
                        borderRadius: '6px',
                        backgroundColor: meta.bg,
                        color: meta.text,
                        border: `1px solid ${meta.border}`,
                        display: 'inline-flex',
                        alignItems: 'center',
                        gap: 4
                      }}>
                        <span>{meta.icon}</span>
                        <span>{chap.subject_name}</span>
                        <span style={{ opacity: 0.6 }}>•</span>
                        <span>{chap.standard_level}</span>
                      </span>

                      <span style={{ fontSize: '0.72rem', fontWeight: 600, color: '#059669', backgroundColor: '#ECFDF5', padding: '2px 8px', borderRadius: '4px' }}>
                        {chap.marks_weightage}
                      </span>
                    </div>

                    <h3 style={{ fontSize: '1.1rem', margin: '0 0 8px 0', color: 'var(--text-primary)', lineHeight: 1.35, fontWeight: 700 }}>
                      Ch {chap.chapter_number}: {chap.chapter_title}
                    </h3>

                    <p style={{ fontSize: '0.8125rem', color: 'var(--text-secondary)', margin: 0, lineHeight: 1.45, maxHeight: '58px', overflow: 'hidden' }}>
                      {chap.summary_notes}
                    </p>
                  </div>

                  <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', borderTop: '1px solid #F3F4F6', paddingTop: 12 }}>
                    <span style={{ fontSize: '0.75rem', color: '#6B7280', fontWeight: 600 }}>
                      ❓ {chap.question_count} Questions
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
                        style={{ fontSize: '0.75rem', padding: '5px 12px', height: 'auto' }}
                        onClick={() => handleOpenChapter(chap.id, 'questions')}
                      >
                        Explore Lesson →
                      </button>
                    </div>
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
