/**
 * Paper detail page — PDF viewer + Answer Key + Split-view comparison + bookmarking.
 * Route: /paper/:id
 */
import { useEffect, useState, useCallback, useRef } from 'react'
import { useParams, useSearchParams, Link, useNavigate } from 'react-router-dom'
import {
  fetchPaper,
  downloadPaper,
  addBookmark,
  removeBookmark,
  fetchBookmarks,
  fetchPaperNote,
  savePaperNote,
  fetchPracticeHistory,
  recordPracticeAttempt,
  getStudyPackUrl,
  getProxyPdfUrl,
  askGeminiDoubt
} from '../../api/client'
import { AnswerKeyBadge, LanguageBadge, PaperTypeBadge } from '../../components/ui/Badges'
import { useAuthStore, useToastStore } from '../../store'
import { useOfflineStorage } from '../../hooks/useOfflineStorage'
import { useSEO } from '../../hooks/useSEO'

// react-pdf for canvas rendering option
import { Document, Page, pdfjs } from 'react-pdf'
import 'react-pdf/dist/Page/TextLayer.css'
import 'react-pdf/dist/Page/AnnotationLayer.css'

// Set worker to local public copy
if (typeof window !== 'undefined') {
  pdfjs.GlobalWorkerOptions.workerSrc = '/pdf.worker.min.mjs'
}

function formatFileSize(bytes) {
  if (!bytes) return null
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(0)} KB`
  return `${(bytes / 1024 / 1024).toFixed(1)} MB`
}

function getExamBlueprint(paper) {
  const slug = (paper?.exam?.slug || '').toLowerCase()
  if (slug === 'class-10') {
    return {
      title: 'CBSE Class 10 Board Exam Pattern & Section Blueprint',
      totalMarks: '80 Theory (+ 20 Internal Assessment)',
      duration: '3 Hours',
      negativeMarking: 'No Negative Marking',
      sections: [
        { name: 'Section A', desc: '20 MCQs & Assertion-Reason (1 Mark each)', marks: '20 Marks' },
        { name: 'Section B', desc: '5 Very Short Answer Questions (2 Marks each)', marks: '10 Marks' },
        { name: 'Section C', desc: '6 Short Answer Questions (3 Marks each)', marks: '18 Marks' },
        { name: 'Section D', desc: '4 Long Answer Questions (5 Marks each)', marks: '20 Marks' },
        { name: 'Section E', desc: '3 Case-Based Integrated Units (4 Marks each)', marks: '12 Marks' },
      ]
    }
  }
  if (slug === 'class-12') {
    return {
      title: 'CBSE Class 12 Board Exam Pattern & Section Blueprint',
      totalMarks: '70 / 80 Theory (+ Practical)',
      duration: '3 Hours',
      negativeMarking: 'No Negative Marking',
      sections: [
        { name: 'Section A', desc: '16 to 18 Objective MCQs (1 Mark each)', marks: '16–18 Marks' },
        { name: 'Section B', desc: '5 Very Short Answer Questions (2 Marks each)', marks: '10 Marks' },
        { name: 'Section C', desc: '7 Short Answer Questions (3 Marks each)', marks: '21 Marks' },
        { name: 'Section D', desc: '2 Case-Study Real World Scenarios (4 Marks each)', marks: '8 Marks' },
        { name: 'Section E', desc: '3 Long Answer Structured Problems (5 Marks each)', marks: '15 Marks' },
      ]
    }
  }
  if (slug === 'jee') {
    return {
      title: 'JEE Main Examination Pattern & Scoring Scheme',
      totalMarks: '300 Marks',
      duration: '3 Hours (180 Minutes)',
      negativeMarking: '+4 for Correct, -1 for Incorrect (MCQs & Numericals)',
      sections: [
        { name: 'Physics', desc: '20 Single-Choice MCQs + 10 Numerical Value Qs (Attempt 5)', marks: '100 Marks' },
        { name: 'Chemistry', desc: '20 Single-Choice MCQs + 10 Numerical Value Qs (Attempt 5)', marks: '100 Marks' },
        { name: 'Mathematics', desc: '20 Single-Choice MCQs + 10 Numerical Value Qs (Attempt 5)', marks: '100 Marks' },
      ]
    }
  }
  if (slug === 'neet') {
    return {
      title: 'NEET UG National Medical Entrance Examination Pattern',
      totalMarks: '720 Marks',
      duration: '3 Hours 20 Minutes (200 Minutes)',
      negativeMarking: '+4 for Correct, -1 for Incorrect Answer',
      sections: [
        { name: 'Physics', desc: 'Section A (35 Qs mandatory) + Section B (15 Qs, attempt 10)', marks: '180 Marks' },
        { name: 'Chemistry', desc: 'Section A (35 Qs mandatory) + Section B (15 Qs, attempt 10)', marks: '180 Marks' },
        { name: 'Botany', desc: 'Section A (35 Qs mandatory) + Section B (15 Qs, attempt 10)', marks: '180 Marks' },
        { name: 'Zoology', desc: 'Section A (35 Qs mandatory) + Section B (15 Qs, attempt 10)', marks: '180 Marks' },
      ]
    }
  }
  if (slug === 'upsc') {
    return {
      title: 'UPSC Civil Services Preliminary Examination Blueprint',
      totalMarks: '200 Marks per Paper',
      duration: '2 Hours per Session',
      negativeMarking: '-0.33 (1/3rd penalty for each wrong answer)',
      sections: [
        { name: 'GS Paper 1', desc: '100 Questions covering History, Polity, Economy, Geography, Environment & Current Affairs', marks: '200 Marks' },
        { name: 'CSAT Paper 2', desc: '80 Questions covering Reading Comprehension, Logical Reasoning, Aptitude (33% Qualifying)', marks: '200 Marks' },
      ]
    }
  }
  if (slug === 'tnpsc') {
    return {
      title: 'TNPSC Examination Pattern & Marking Scheme',
      totalMarks: '300 Marks',
      duration: '3 Hours (180 Minutes)',
      negativeMarking: 'No Negative Marking',
      sections: [
        { name: 'Part A', desc: 'General Tamil / General English (100 Questions)', marks: '150 Marks' },
        { name: 'Part B', desc: 'General Studies (75 Questions) + Aptitude & Mental Ability (25 Questions)', marks: '150 Marks' },
      ]
    }
  }
  return null
}

export default function PaperDetailPage() {
  const { id } = useParams()
  const [searchParams] = useSearchParams()
  const initialTab = searchParams.get('tab') === 'key' ? 'key' : 'paper'
  const navigate = useNavigate()
  const { user } = useAuthStore()
  const { addToast } = useToastStore()

  useEffect(() => {
    if (!user) {
      addToast('Please sign in or register to view question papers.', 'info')
      navigate('/login', { replace: true })
    }
  }, [user, navigate, addToast])

  const [paper, setPaper] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)
  const [pdfUrl, setPdfUrl] = useState(null)
  const [pdfLoading, setPdfLoading] = useState(false)
  const [activeDoc, setActiveDoc] = useState(initialTab) // 'paper' | 'key' | 'textbook' | 'split'
  const [selectedTextbookIndex, setSelectedTextbookIndex] = useState(0)
  const [splitSecondary, setSplitSecondary] = useState('key') // 'key' | 'textbook'
  const [viewerMode, setViewerMode] = useState('embed') // 'embed' (native iframe) | 'canvas' (react-pdf)
  const [useProxy, setUseProxy] = useState(true)
  const [isFullscreen, setIsFullscreen] = useState(false)
  const [numPages, setNumPages] = useState(null)
  const [currentPage, setCurrentPage] = useState(1)
  const [isBookmarked, setIsBookmarked] = useState(false)
  const [bookmarkLoading, setBookmarkLoading] = useState(false)
  const viewerContainerRef = useRef(null)

  // ── Revision Notes State ────────────────────────────────────────────────
  const [noteText, setNoteText] = useState('')
  const [notesOpen, setNotesOpen] = useState(false)
  const [savingNote, setSavingNote] = useState(false)
  const [lastSavedNoteTime, setLastSavedNoteTime] = useState(null)

  // ── Exam Simulator & Practice Mode State ────────────────────────────────
  const [practiceModalOpen, setPracticeModalOpen] = useState(false)
  const [timerDuration, setTimerDuration] = useState(180 * 60)
  const [timerSeconds, setTimerSeconds] = useState(180 * 60)
  const [timerRunning, setTimerRunning] = useState(false)
  const [practiceFinished, setPracticeFinished] = useState(false)
  const [scratchText, setScratchText] = useState('')
  const [selfScore, setSelfScore] = useState('')
  const [maxScore, setMaxScore] = useState(100)
  const [practiceNotes, setPracticeNotes] = useState('')
  const [practiceHistory, setPracticeHistory] = useState([])
  const [recordingAttempt, setRecordingAttempt] = useState(false)
  const [blueprintOpen, setBlueprintOpen] = useState(false)

  // ── Gemini AI Doubt Assistant State ─────────────────────────────────────
  const [aiModalOpen, setAiModalOpen] = useState(false)
  const [aiQuestionText, setAiQuestionText] = useState('')
  const [aiUserQuery, setAiUserQuery] = useState('')
  const [aiMode, setAiMode] = useState('step_by_step')
  const [aiLoading, setAiLoading] = useState(false)
  const [aiSolution, setAiSolution] = useState(null)
  const [aiModelUsed, setAiModelUsed] = useState('')
  
  const { isCached, isDownloading, saveForOffline, removeFromOffline } = useOfflineStorage(paper)

  useEffect(() => {
    if (!user || !id) return
    fetchPaperNote(id)
      .then((res) => {
        setNoteText(res.note || '')
        setLastSavedNoteTime(res.updated_at)
      })
      .catch(() => {})
    fetchPracticeHistory(id)
      .then(setPracticeHistory)
      .catch(() => {})
  }, [user, id])

  // Timer interval for Practice Mode
  useEffect(() => {
    let interval = null
    if (timerRunning && timerSeconds > 0 && !practiceFinished) {
      interval = setInterval(() => {
        setTimerSeconds(s => Math.max(0, s - 1))
      }, 1000)
    } else if (timerSeconds === 0 && timerRunning) {
      setTimerRunning(false)
      setPracticeFinished(true)
      addToast('Time is up! Review with official answer key.', 'info')
    }
    return () => clearInterval(interval)
  }, [timerRunning, timerSeconds, practiceFinished, addToast])

  const handleSaveNote = async () => {
    if (!user) return
    setSavingNote(true)
    try {
      await savePaperNote(id, noteText)
      setLastSavedNoteTime(new Date().toISOString())
      addToast('Revision note saved successfully!')
    } catch {
      addToast('Failed to save revision note', 'error')
    } finally {
      setSavingNote(false)
    }
  }

  const handleStartPractice = (minutes = 180) => {
    setTimerDuration(minutes * 60)
    setTimerSeconds(minutes * 60)
    setTimerRunning(true)
    setPracticeFinished(false)
    setScratchText('')
    setSelfScore('')
    setPracticeNotes('')
    setPracticeModalOpen(true)
  }

  const handleFinishPractice = () => {
    setTimerRunning(false)
    setPracticeFinished(true)
  }

  const handleRecordAttempt = async () => {
    if (!selfScore) {
      addToast('Please enter your self-evaluated score', 'error')
      return
    }
    setRecordingAttempt(true)
    try {
      const durationSeconds = timerDuration - timerSeconds
      await recordPracticeAttempt(id, {
        duration_seconds: durationSeconds,
        self_score: Number(selfScore),
        max_score: Number(maxScore) || 100,
        notes: practiceNotes || scratchText
      })
      addToast('Mock exam attempt saved to your profile!')
      const updated = await fetchPracticeHistory(id)
      setPracticeHistory(updated)
      setPracticeModalOpen(false)
    } catch {
      addToast('Could not save practice attempt', 'error')
    } finally {
      setRecordingAttempt(false)
    }
  }

  const handleAskGemini = async (overridePrompt = null) => {
    const queryToSend = overridePrompt || aiUserQuery
    if (!aiQuestionText && !queryToSend) {
      addToast('Please type a question or select a prompt', 'error')
      return
    }
    setAiLoading(true)
    try {
      const res = await askGeminiDoubt({
        paper_id: id,
        question_text: aiQuestionText,
        user_query: queryToSend,
        mode: aiMode
      })
      setAiSolution(res.solution)
      setAiModelUsed(res.model_used)
      addToast('Gemini AI explanation generated!')
    } catch {
      addToast('Gemini AI request failed. Please try again.', 'error')
    } finally {
      setAiLoading(false)
    }
  }

  const handleAppendAiToNotes = () => {
    if (!aiSolution) return
    const newText = noteText ? `${noteText}\n\n--- 🤖 Gemini AI Solution ---\n${aiSolution}` : `--- 🤖 Gemini AI Solution ---\n${aiSolution}`
    setNoteText(newText)
    setNotesOpen(true)
    addToast('Solution appended to your revision notes! Click Save Note to persist.')
  }

  const formatTimer = (totalSec) => {
    const hrs = Math.floor(totalSec / 3600)
    const mins = Math.floor((totalSec % 3600) / 60)
    const secs = totalSec % 60
    return `${hrs > 0 ? `${hrs.toString().padStart(2, '0')}:` : ''}${mins.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`
  }

  useEffect(() => {
    setLoading(true)
    fetchPaper(id)
      .then((p) => {
        setPaper(p)
        if (p.pdf_url) {
          setPdfUrl(p.pdf_url)
        }
        if (initialTab === 'key' && p.has_answer_key && p.answer_key_pdf_url) {
          setActiveDoc('key')
        }
      })
      .catch(() => setError('Paper not found'))
      .finally(() => setLoading(false))
  }, [id, initialTab])

  useSEO({
    title: paper ? `${paper.title} (${paper.year}) ${activeDoc === 'key' ? '— Answer Key' : ''} — ExamVault` : 'Paper Detail — ExamVault',
    description: paper ? `Download and view ${paper.title} from ${paper.year} along with official answer key and marking scheme.` : '',
    schema: paper ? {
      '@context': 'https://schema.org',
      '@type': 'LearningResource',
      name: paper.title,
      datePublished: `${paper.year}-01-01`,
      educationalLevel: paper.exam?.name,
      inLanguage: paper.language,
      url: `https://examvault.in/paper/${paper.id}`,
    } : null
  })

  useEffect(() => {
    if (!user || !paper) return
    fetchBookmarks()
      .then((bms) => {
        setIsBookmarked(bms.some((b) => b.paper_id === paper.id))
      })
      .catch(() => {})
  }, [user, paper])

  const handleLoadPDF = useCallback(async () => {
    if (!paper) return
    setPdfLoading(true)
    try {
      const data = await downloadPaper(paper.id)
      setPdfUrl(data.pdf_url)
    } catch {
      addToast('Could not load PDF', 'error')
    } finally {
      setPdfLoading(false)
    }
  }, [paper, addToast])

  const scrollToViewer = (docType = 'paper') => {
    setActiveDoc(docType)
    if (viewerContainerRef.current) {
      viewerContainerRef.current.scrollIntoView({ behavior: 'smooth' })
    }
  }

  const handleBookmark = async () => {
    if (!user) {
      addToast('Sign in to bookmark papers', 'error')
      return
    }
    setBookmarkLoading(true)
    try {
      if (isBookmarked) {
        await removeBookmark(paper.id)
        setIsBookmarked(false)
        addToast('Bookmark removed')
      } else {
        await addBookmark(paper.id)
        setIsBookmarked(true)
        addToast('Paper bookmarked!')
      }
    } catch {
      addToast('Could not update bookmark', 'error')
    } finally {
      setBookmarkLoading(false)
    }
  }

  const toggleFullscreen = () => {
    if (!viewerContainerRef.current) return
    if (!document.fullscreenElement) {
      viewerContainerRef.current.requestFullscreen().catch(() => {})
      setIsFullscreen(true)
    } else {
      document.exitFullscreen().catch(() => {})
      setIsFullscreen(false)
    }
  }

  useEffect(() => {
    const handleFsChange = () => setIsFullscreen(!!document.fullscreenElement)
    document.addEventListener('fullscreenchange', handleFsChange)
    return () => document.removeEventListener('fullscreenchange', handleFsChange)
  }, [])

  const slug = paper?.exam?.slug || ''
  const accentColor = paper?.exam?.accent_color_hex || '#8FB9A8'
  const isSample = paper?.paper_type === 'sample'
  const hasKey = Boolean(paper?.has_answer_key && paper?.answer_key_pdf_url)
  const textbooks = paper?.textbooks || []
  const hasTextbooks = textbooks.length > 0
  const activeTextbook = textbooks[selectedTextbookIndex] || textbooks[0] || null
  const blueprint = getExamBlueprint(paper)

  let rawViewUrl = pdfUrl
  if (activeDoc === 'key') {
    rawViewUrl = paper?.answer_key_pdf_url || pdfUrl
  } else if (activeDoc === 'textbook' && activeTextbook) {
    rawViewUrl = activeTextbook.pdf_url
  }

  const resolveDocUrl = (url) => {
    if (!url) return ''
    if (useProxy || url.startsWith('http://') || url.startsWith('https://')) {
      return getProxyPdfUrl(url)
    }
    return url
  }

  const currentViewUrl = resolveDocUrl(rawViewUrl)
  const leftPaneUrl = resolveDocUrl(pdfUrl)
  const rightPaneRawUrl = splitSecondary === 'textbook' && activeTextbook ? activeTextbook.pdf_url : paper?.answer_key_pdf_url
  const rightPaneUrl = resolveDocUrl(rightPaneRawUrl)

  if (loading) {
    return (
      <div className="page-content container">
        <div className="skeleton" style={{ width: '60%', height: 36, marginBottom: 12 }} />
        <div className="skeleton" style={{ width: '40%', height: 20, marginBottom: 32 }} />
        <div className="skeleton" style={{ width: '100%', height: 400, borderRadius: 12 }} />
      </div>
    )
  }

  if (error || !paper) {
    return (
      <div className="page-content container">
        <div className="empty-state">
          <div className="empty-state-icon">📭</div>
          <h3>Paper not found</h3>
          <Link to="/" className="btn btn-ghost">← Back to Home</Link>
        </div>
      </div>
    )
  }

  return (
    <div className="page-content" data-exam={slug}>
      <div className="container" style={{ maxWidth: 1000 }}>

        {/* Breadcrumb */}
        <div style={{ display: 'flex', gap: 8, alignItems: 'center', marginBottom: 'var(--space-5)', fontSize: '0.8125rem', color: 'var(--text-muted)', flexWrap: 'wrap' }}>
          <Link to="/" style={{ color: 'var(--text-muted)', textDecoration: 'none' }}>Home</Link>
          <span>›</span>
          {paper.exam && (
            <>
              <Link to={`/exam/${paper.exam.slug}`} style={{ color: 'var(--text-muted)', textDecoration: 'none' }}>{paper.exam.name}</Link>
              <span>›</span>
            </>
          )}
          {paper.exam && paper.category && (
            <>
              <Link to={`/exam/${paper.exam.slug}/${paper.category.slug}`} style={{ color: 'var(--text-muted)', textDecoration: 'none' }}>{paper.category.name}</Link>
              <span>›</span>
            </>
          )}
          <span className="mono" style={{ color: 'var(--text-secondary)' }}>
            {paper.year}{paper.session ? ` — ${paper.session}` : ''}
          </span>
        </div>

        {/* Paper Header Card */}
        <div style={{
          backgroundColor: 'var(--surface)',
          padding: '24px 28px',
          borderRadius: '16px',
          border: '1px solid var(--color-border)',
          marginBottom: 'var(--space-6)',
          boxShadow: 'var(--shadow-sm)'
        }}>
          {/* Classification & Answer Key Badges */}
          <div style={{ display: 'flex', gap: 10, alignItems: 'center', flexWrap: 'wrap', marginBottom: 14 }}>
            <PaperTypeBadge paperType={paper.paper_type} />
            <AnswerKeyBadge hasKey={hasKey} />
            {paper.verification_status === 'verified' ? (
              <span style={{
                display: 'inline-flex',
                alignItems: 'center',
                gap: 4,
                fontSize: '0.72rem',
                fontWeight: 600,
                color: '#10B981',
                backgroundColor: 'rgba(16, 185, 129, 0.1)',
                padding: '2px 7px',
                borderRadius: '6px',
                border: '1px solid rgba(16, 185, 129, 0.25)'
              }}>
                <span>🛡️</span>
                <span>Verified Official Document</span>
              </span>
            ) : (
              <span style={{
                display: 'inline-flex',
                alignItems: 'center',
                gap: 4,
                fontSize: '0.72rem',
                fontWeight: 600,
                color: '#D97706',
                backgroundColor: 'rgba(245, 158, 11, 0.1)',
                padding: '2px 7px',
                borderRadius: '6px',
                border: '1px solid rgba(245, 158, 11, 0.25)'
              }}>
                <span>⚠️</span>
                <span>Provisional / Community Archive</span>
              </span>
            )}
            <span className="mono" style={{ fontSize: '0.875rem', fontWeight: 700, color: accentColor, marginLeft: 'auto' }}>
              {paper.year}{paper.session ? ` (${paper.session})` : ''}
            </span>
          </div>

          {paper.verification_status === 'unverified' && (
            <div style={{
              backgroundColor: 'rgba(245, 158, 11, 0.08)',
              border: '1px solid rgba(245, 158, 11, 0.25)',
              borderRadius: 10,
              padding: '10px 14px',
              marginBottom: 16,
              fontSize: '0.8125rem',
              color: '#B45309',
              display: 'flex',
              alignItems: 'center',
              gap: 10
            }}>
              <span style={{ fontSize: '1.1rem' }}>⚠️</span>
              <div>
                <strong>Provisional / Community Archive:</strong> This document is sourced from candidate recollections or provisional exam shifts. It is provided for study reference while awaiting final statutory board publication.
              </div>
            </div>
          )}

          <h1 style={{ fontSize: 'clamp(1.4rem, 2.5vw, 1.85rem)', lineHeight: 1.35, marginBottom: 'var(--space-3)', color: 'var(--text-primary)' }}>
            {paper.title}
          </h1>

          <p style={{ fontSize: '0.875rem', color: 'var(--text-secondary)', marginBottom: 16, lineHeight: 1.5 }}>
            {isSample
              ? 'Official Sample Question Paper (SQP) issued by the examination board to familiarize students with the exact question paper pattern, section structure, and marking scheme.'
              : 'Genuine Previous Year Public/Board/Competitive Examination Paper administered to candidates in this academic examination cycle.'}
            {hasKey ? ' Official Answer Key / Marking Scheme is attached with this question paper.' : ''}
          </p>

          {/* Metadata Badges */}
          <div style={{ display: 'flex', gap: 'var(--space-3)', flexWrap: 'wrap', alignItems: 'center', marginBottom: 20 }}>
            <LanguageBadge language={paper.language} />
            {formatFileSize(paper.file_size) && (
              <span style={{ fontSize: '0.8125rem', color: 'var(--text-muted)', background: 'rgba(0,0,0,0.04)', padding: '2px 8px', borderRadius: '4px' }}>
                📦 {formatFileSize(paper.file_size)}
              </span>
            )}
            <span className="mono" style={{ fontSize: '0.8125rem', color: 'var(--text-muted)' }}>
              ↓ {paper.download_count?.toLocaleString() || 0} downloads
            </span>
          </div>

          {/* Subjects (Subject-wise navigation) */}
          {paper.subjects?.length > 0 && (
            <div style={{ display: 'flex', gap: 8, flexWrap: 'wrap', marginBottom: 20, alignItems: 'center' }}>
              <span style={{ fontSize: '0.8125rem', color: 'var(--text-muted)', fontWeight: 600 }}>Subjects:</span>
              {paper.subjects.map((s) => (
                <Link
                  key={s.id}
                  to={`/search?subject=${encodeURIComponent(s.name)}`}
                  className="badge"
                  style={{
                    textDecoration: 'none',
                    backgroundColor: `${accentColor}18`,
                    color: accentColor,
                    border: `1px solid ${accentColor}33`,
                    padding: '4px 10px',
                    borderRadius: '8px',
                    fontSize: '0.8125rem',
                    fontWeight: 600,
                    cursor: 'pointer'
                  }}
                  title={`View all ${s.name} previous year question papers`}
                >
                  🏷️ {s.name}
                </Link>
              ))}
            </div>
          )}

          {/* ── Official Exam Blueprint & Section Pattern ── */}
          {blueprint && (
            <div style={{
              marginTop: 14,
              marginBottom: 20,
              padding: '14px 18px',
              backgroundColor: 'rgba(99, 102, 241, 0.04)',
              border: '1px solid rgba(99, 102, 241, 0.22)',
              borderRadius: '12px'
            }}>
              <div
                style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', cursor: 'pointer', flexWrap: 'wrap', gap: 8 }}
                onClick={() => setBlueprintOpen(!blueprintOpen)}
              >
                <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
                  <span style={{ fontSize: '1.15rem' }}>📋</span>
                  <div>
                    <span style={{ fontWeight: 700, fontSize: '0.875rem', color: '#4338ca' }}>
                      {blueprint.title}
                    </span>
                    <div style={{ fontSize: '0.72rem', color: 'var(--text-muted)' }}>
                      Click to {blueprintOpen ? 'collapse' : 'view'} section breakdown & marking scheme
                    </div>
                  </div>
                </div>
                <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
                  <span style={{ fontSize: '0.75rem', fontWeight: 600, color: '#4f46e5', backgroundColor: '#e0e7ff', padding: '2px 8px', borderRadius: '4px' }}>
                    {blueprint.duration} · {blueprint.negativeMarking}
                  </span>
                  <span style={{ fontSize: '0.8125rem', color: '#4f46e5' }}>
                    {blueprintOpen ? '▲' : '▼'}
                  </span>
                </div>
              </div>

              {blueprintOpen && (
                <div style={{ marginTop: 12, borderTop: '1px solid rgba(99, 102, 241, 0.15)', paddingTop: 12 }}>
                  <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: 10 }}>
                    {blueprint.sections.map((sec, idx) => (
                      <div
                        key={idx}
                        style={{
                          backgroundColor: '#ffffff',
                          padding: '10px 14px',
                          borderRadius: '8px',
                          border: '1px solid var(--color-border)',
                          display: 'flex',
                          flexDirection: 'column',
                          gap: 2
                        }}
                      >
                        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                          <span style={{ fontWeight: 700, fontSize: '0.8125rem', color: 'var(--text-primary)' }}>{sec.name}</span>
                          <span style={{ fontSize: '0.75rem', fontWeight: 600, color: '#4f46e5' }}>{sec.marks}</span>
                        </div>
                        <div style={{ fontSize: '0.75rem', color: 'var(--text-secondary)' }}>{sec.desc}</div>
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </div>
          )}

          {/* Prescribed Curriculum Textbooks Co-Located Card Section */}
          {hasTextbooks && (
            <div style={{
              marginTop: 18,
              marginBottom: 20,
              padding: '16px 20px',
              backgroundColor: 'rgba(59, 130, 246, 0.04)',
              border: '1px solid rgba(59, 130, 246, 0.22)',
              borderRadius: '12px',
            }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 12, flexWrap: 'wrap', gap: 8 }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
                  <span style={{ fontSize: '1.25rem' }}>📚</span>
                  <div>
                    <div style={{ fontSize: '0.7rem', textTransform: 'uppercase', letterSpacing: '0.06em', color: '#2563EB', fontWeight: 700 }}>
                      Official Prescribed Curriculum Textbooks
                    </div>
                    <div style={{ fontSize: '0.875rem', fontWeight: 600, color: 'var(--text-primary)' }}>
                      Board-Prescribed Study Material & Syllabus Textbooks
                    </div>
                  </div>
                </div>
                <Link
                  to="/textbooks"
                  style={{ fontSize: '0.75rem', color: '#2563EB', textDecoration: 'none', fontWeight: 600 }}
                >
                  View Full Textbook Library →
                </Link>
              </div>

              <div style={{ display: 'flex', flexDirection: 'column', gap: 10 }}>
                {textbooks.map((tb, idx) => (
                  <div
                    key={tb.id}
                    style={{
                      display: 'flex',
                      alignItems: 'center',
                      justifyContent: 'space-between',
                      padding: '10px 14px',
                      backgroundColor: selectedTextbookIndex === idx && activeDoc === 'textbook' ? 'rgba(59, 130, 246, 0.12)' : '#ffffff',
                      border: `1px solid ${selectedTextbookIndex === idx && activeDoc === 'textbook' ? '#3B82F6' : 'var(--color-border)'}`,
                      borderRadius: '8px',
                      flexWrap: 'wrap',
                      gap: 10
                    }}
                  >
                    <div style={{ display: 'flex', alignItems: 'center', gap: 10, minWidth: 200, flex: 1 }}>
                      <span style={{
                        fontSize: '0.7rem',
                        fontWeight: 700,
                        padding: '2px 8px',
                        borderRadius: '4px',
                        backgroundColor: tb.board === 'NCERT' ? '#EEF2FF' : '#ECFDF5',
                        color: tb.board === 'NCERT' ? '#4F46E5' : '#059669',
                        border: '1px solid var(--color-border)'
                      }}>
                        {tb.board} · {tb.standard_level}
                      </span>
                      <span style={{ fontWeight: 600, fontSize: '0.875rem', color: 'var(--text-primary)' }}>
                        {tb.title}
                      </span>
                    </div>

                    <div style={{ display: 'flex', gap: 8, alignItems: 'center' }}>
                      <button
                        className="btn btn-primary btn-sm"
                        style={{ fontSize: '0.75rem', padding: '5px 12px', height: 'auto', backgroundColor: '#3B82F6', borderColor: '#3B82F6' }}
                        onClick={() => {
                          setSelectedTextbookIndex(idx)
                          scrollToViewer('textbook')
                        }}
                      >
                        📖 Read in Viewer
                      </button>
                      <button
                        className="btn btn-ghost btn-sm"
                        style={{ fontSize: '0.75rem', padding: '5px 10px', height: 'auto', color: '#6366F1', borderColor: 'rgba(99, 102, 241, 0.4)' }}
                        onClick={() => {
                          setSelectedTextbookIndex(idx)
                          setSplitSecondary('textbook')
                          scrollToViewer('split')
                        }}
                        title="Compare Question Paper and Textbook side-by-side"
                      >
                        ◫ Split View
                      </button>
                      {tb.pdf_url && (
                        <a
                          href={tb.pdf_url}
                          target="_blank"
                          rel="noopener noreferrer"
                          download
                          className="btn btn-ghost btn-sm"
                          style={{ fontSize: '0.75rem', padding: '5px 10px', height: 'auto' }}
                          title="Download PDF"
                        >
                          📥 PDF
                        </a>
                      )}
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* ── Document Segregation Access Bar ── */}
          <div style={{
            display: 'flex',
            gap: 10,
            flexWrap: 'wrap',
            alignItems: 'center',
            padding: '14px 16px',
            background: 'rgba(0,0,0,0.02)',
            borderRadius: '12px',
            border: '1px solid var(--color-border)',
            marginBottom: 20
          }}>
            <button
              className={`btn ${activeDoc === 'paper' ? 'btn-primary' : 'btn-ghost'}`}
              onClick={() => scrollToViewer('paper')}
              style={{ fontWeight: 600, padding: '8px 16px', fontSize: '0.875rem' }}
            >
              📑 View Question Paper
            </button>

            {hasKey && (
              <button
                className={`btn ${activeDoc === 'key' ? 'btn-primary' : 'btn-ghost'}`}
                onClick={() => scrollToViewer('key')}
                style={{
                  fontWeight: 600,
                  padding: '8px 16px',
                  fontSize: '0.875rem',
                  backgroundColor: activeDoc === 'key' ? '#10B981' : 'transparent',
                  borderColor: '#10B981',
                  color: activeDoc === 'key' ? '#fff' : '#10B981'
                }}
              >
                🔑 View Answer Key
              </button>
            )}

            {hasTextbooks && (
              <button
                className={`btn ${activeDoc === 'textbook' ? 'btn-primary' : 'btn-ghost'}`}
                onClick={() => scrollToViewer('textbook')}
                style={{
                  fontWeight: 600,
                  padding: '8px 16px',
                  fontSize: '0.875rem',
                  backgroundColor: activeDoc === 'textbook' ? '#3B82F6' : 'transparent',
                  borderColor: '#3B82F6',
                  color: activeDoc === 'textbook' ? '#fff' : '#3B82F6'
                }}
              >
                📚 View Textbook
              </button>
            )}

            {(hasKey || hasTextbooks) && (
              <button
                className={`btn ${activeDoc === 'split' ? 'btn-primary' : 'btn-ghost'}`}
                onClick={() => scrollToViewer('split')}
                style={{
                  fontWeight: 600,
                  padding: '8px 16px',
                  fontSize: '0.875rem',
                  backgroundColor: activeDoc === 'split' ? '#6366F1' : 'transparent',
                  borderColor: '#6366F1',
                  color: activeDoc === 'split' ? '#fff' : '#6366F1'
                }}
                title="View Question Paper and reference material side-by-side"
              >
                ◫ Side-by-Side View
              </button>
            )}

            {!hasKey && !hasTextbooks && (
              <span style={{ fontSize: '0.8125rem', color: 'var(--text-muted)', fontStyle: 'italic', padding: '6px 10px' }}>
                ℹ️ Descriptive exam paper (official scoring based on full evaluation criteria)
              </span>
            )}
          </div>

          {/* Secondary Action & Download Buttons */}
          <div style={{ display: 'flex', gap: 'var(--space-3)', flexWrap: 'wrap', alignItems: 'center' }}>
            {pdfUrl && (
              <a
                href={pdfUrl}
                target="_blank"
                rel="noopener noreferrer"
                className="btn btn-ghost btn-sm"
                download
              >
                📥 Download Question Paper
              </a>
            )}

            {hasKey && (
              <a
                href={paper.answer_key_pdf_url}
                target="_blank"
                rel="noopener noreferrer"
                className="btn btn-ghost btn-sm"
                style={{ color: '#10B981', borderColor: 'rgba(16, 185, 129, 0.4)' }}
                download
              >
                📥 Download Answer Key
              </a>
            )}

            <a
              href={getStudyPackUrl(paper.id)}
              className="btn btn-ghost btn-sm"
              style={{
                color: '#2563EB',
                borderColor: 'rgba(37, 99, 235, 0.4)',
                backgroundColor: 'rgba(37, 99, 235, 0.05)',
                fontWeight: 600
              }}
              download
              title="Download Question Paper, Official Answer Key, and Prescribed Textbook combined in a single ZIP"
            >
              📦 Download Full Study Pack (.zip)
            </a>

            <button
              className="btn btn-primary btn-sm"
              style={{
                backgroundColor: '#F59E0B',
                borderColor: '#F59E0B',
                fontWeight: 600,
                color: '#fff'
              }}
              onClick={() => handleStartPractice(180)}
              title="Launch distraction-free exam simulator with countdown timer and self-scoring"
            >
              ⏱️ Practice Mode & Timer
            </button>

            <button
              className="btn btn-ghost btn-sm"
              style={{
                color: '#D97706',
                borderColor: 'rgba(217, 119, 6, 0.4)',
                fontWeight: 600
              }}
              onClick={() => setNotesOpen(!notesOpen)}
            >
              {notesOpen ? 'Hide Notes' : noteText ? '📝 View My Notes' : '📝 Add Notes'}
            </button>

            <button
              className="btn btn-primary btn-sm"
              style={{
                backgroundColor: '#7C3AED',
                borderColor: '#7C3AED',
                fontWeight: 600,
                color: '#fff',
                display: 'inline-flex',
                alignItems: 'center',
                gap: 6
              }}
              onClick={() => setAiModalOpen(!aiModalOpen)}
              title="Ask Gemini AI for step-by-step solutions, hints, or marking scheme analysis"
            >
              <span>✨ Ask Gemini AI</span>
            </button>

            <button
              className="btn btn-ghost btn-sm"
              onClick={handleBookmark}
              disabled={bookmarkLoading}
              style={{ color: isBookmarked ? '#FFD166' : undefined }}
            >
              {isBookmarked ? '★ Bookmarked' : '☆ Bookmark'}
            </button>

            {isCached ? (
              <button
                className="btn btn-ghost btn-sm"
                onClick={removeFromOffline}
                style={{ color: '#4ECBA9' }}
              >
                ✓ Offline Available (Remove)
              </button>
            ) : (
              <button
                className="btn btn-ghost btn-sm"
                onClick={saveForOffline}
                disabled={isDownloading || !paper?.pdf_url}
              >
                {isDownloading ? '⏳ Saving...' : '⬇ Save Offline'}
              </button>
            )}
          </div>

          {/* Gemini AI Doubt Solver & Solution Explainer Drawer */}
          {aiModalOpen && (
            <div style={{
              marginTop: 18,
              padding: '20px 24px',
              backgroundColor: '#f5f3ff',
              border: '1px solid #ddd6fe',
              borderRadius: '14px',
              boxShadow: '0 4px 14px rgba(124, 58, 237, 0.08)'
            }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 14, flexWrap: 'wrap', gap: 10 }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
                  <span style={{ fontSize: '1.35rem' }}>✨</span>
                  <div>
                    <span style={{ fontWeight: 700, fontSize: '0.95rem', color: '#5b21b6' }}>
                      Gemini AI Doubt Solver & Academic Tutor
                    </span>
                    <div style={{ fontSize: '0.72rem', color: '#6d28d9' }}>
                      Powered by Google Gemini 3.5 Flash · Aligned with official syllabus & marking scheme
                    </div>
                  </div>
                </div>
                <div style={{ display: 'flex', gap: 6, alignItems: 'center' }}>
                  {aiSolution && (
                    <button
                      className="btn btn-ghost btn-sm"
                      style={{ fontSize: '0.75rem', color: '#6d28d9', borderColor: '#c4b5fd', backgroundColor: '#ede9fe' }}
                      onClick={handleAppendAiToNotes}
                      title="Append this solution to your personal revision notes"
                    >
                      📝 Save to Notes
                    </button>
                  )}
                  <button
                    className="btn btn-ghost btn-sm"
                    style={{ fontSize: '0.75rem', color: '#6d28d9' }}
                    onClick={() => setAiModalOpen(false)}
                  >
                    ✕ Close
                  </button>
                </div>
              </div>

              {/* Mode Selector Tabs */}
              <div style={{ display: 'flex', gap: 8, marginBottom: 14, flexWrap: 'wrap' }}>
                {[
                  { id: 'step_by_step', label: '📝 Step-by-Step Solution', desc: 'Full pedagogical solution with formulas' },
                  { id: 'hint', label: '💡 Socratic Hint (No Spoilers)', desc: 'Guiding hint to solve it yourself' },
                  { id: 'marking_scheme', label: '🎯 Marking Scheme Breakdown', desc: 'Point allocation breakdown' },
                  { id: 'textbook_ref', label: '📖 NCERT Textbook Links', desc: 'Relevant chapters & theory' },
                ].map((m) => (
                  <button
                    key={m.id}
                    type="button"
                    onClick={() => setAiMode(m.id)}
                    style={{
                      padding: '5px 12px',
                      borderRadius: '8px',
                      fontSize: '0.78rem',
                      fontWeight: 600,
                      border: '1px solid',
                      borderColor: aiMode === m.id ? '#7c3aed' : '#c4b5fd',
                      backgroundColor: aiMode === m.id ? '#7c3aed' : '#ffffff',
                      color: aiMode === m.id ? '#ffffff' : '#6d28d9',
                      cursor: 'pointer',
                      transition: 'all 0.15s ease'
                    }}
                    title={m.desc}
                  >
                    {m.label}
                  </button>
                ))}
              </div>

              {/* Question Text / Doubt Input */}
              <div style={{ marginBottom: 12 }}>
                <textarea
                  value={aiQuestionText}
                  onChange={(e) => setAiQuestionText(e.target.value)}
                  placeholder="Paste or type the question here (e.g. 'Question 4: State Ohm\'s law and derive the expression for equivalent resistance of two resistors in parallel...')"
                  rows={3}
                  style={{
                    width: '100%',
                    padding: '10px 14px',
                    borderRadius: '10px',
                    border: '1px solid #c4b5fd',
                    fontFamily: 'inherit',
                    fontSize: '0.875rem',
                    resize: 'vertical',
                    backgroundColor: '#ffffff'
                  }}
                />
              </div>

              {/* Quick Prompt Suggestions */}
              <div style={{ display: 'flex', gap: 6, flexWrap: 'wrap', marginBottom: 14, alignItems: 'center' }}>
                <span style={{ fontSize: '0.72rem', color: '#6d28d9', fontWeight: 600 }}>Quick Questions:</span>
                {[
                  'Explain step-by-step with formulas',
                  'What are common mistakes students make here?',
                  'How would the examiner mark each step?',
                  'Which chapter in NCERT explains this?'
                ].map((p) => (
                  <button
                    key={p}
                    type="button"
                    onClick={() => {
                      setAiUserQuery(p)
                      handleAskGemini(p)
                    }}
                    style={{
                      fontSize: '0.72rem',
                      padding: '3px 9px',
                      borderRadius: '14px',
                      backgroundColor: '#ede9fe',
                      color: '#5b21b6',
                      border: '1px solid #ddd6fe',
                      cursor: 'pointer'
                    }}
                  >
                    {p}
                  </button>
                ))}
              </div>

              {/* Action Button */}
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                <div style={{ fontSize: '0.75rem', color: '#6d28d9' }}>
                  {aiModelUsed ? `Generated with ${aiModelUsed}` : 'Ready to analyze'}
                </div>
                <button
                  className="btn btn-primary btn-sm"
                  style={{
                    backgroundColor: '#7c3aed',
                    borderColor: '#7c3aed',
                    fontWeight: 600,
                    padding: '7px 20px',
                    fontSize: '0.85rem'
                  }}
                  onClick={() => handleAskGemini()}
                  disabled={aiLoading}
                >
                  {aiLoading ? '⏳ Generating AI Explanation...' : '✨ Generate Solution'}
                </button>
              </div>

              {/* Solution Output Box */}
              {aiSolution && (
                <div style={{
                  marginTop: 16,
                  padding: '16px 20px',
                  backgroundColor: '#ffffff',
                  border: '1px solid #c4b5fd',
                  borderRadius: '10px',
                  boxShadow: '0 2px 6px rgba(0,0,0,0.04)'
                }}>
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 12, borderBottom: '1px solid #f3e8ff', paddingBottom: 8 }}>
                    <span style={{ fontWeight: 700, fontSize: '0.85rem', color: '#5b21b6' }}>
                      🎓 AI Solution & Academic Analysis:
                    </span>
                    <button
                      className="btn btn-ghost btn-sm"
                      style={{ fontSize: '0.72rem', padding: '2px 8px' }}
                      onClick={() => {
                        navigator.clipboard.writeText(aiSolution)
                        addToast('Solution copied to clipboard!')
                      }}
                    >
                      📋 Copy
                    </button>
                  </div>
                  <div style={{
                    fontSize: '0.875rem',
                    lineHeight: 1.65,
                    color: '#1f2937',
                    whiteSpace: 'pre-wrap',
                    fontFamily: 'inherit'
                  }}>
                    {aiSolution}
                  </div>
                </div>
              )}
            </div>
          )}

          {/* Student Revision Notes Drawer */}
          {notesOpen && (
            <div style={{
              marginTop: 18,
              padding: '16px 20px',
              backgroundColor: '#fffbeb',
              border: '1px solid #fde68a',
              borderRadius: '12px'
            }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 8 }}>
                <span style={{ fontWeight: 700, fontSize: '0.875rem', color: '#92400e' }}>
                  📝 My Private Revision Notes
                </span>
                {lastSavedNoteTime && (
                  <span style={{ fontSize: '0.72rem', color: '#b45309' }}>
                    Last saved: {new Date(lastSavedNoteTime).toLocaleDateString()} {new Date(lastSavedNoteTime).toLocaleTimeString()}
                  </span>
                )}
              </div>
              <textarea
                value={noteText}
                onChange={(e) => setNoteText(e.target.value)}
                placeholder="Jot down formulas, tricky questions, notes from the marking scheme, or concepts to revise..."
                rows={4}
                style={{
                  width: '100%',
                  padding: '10px 12px',
                  borderRadius: '8px',
                  border: '1px solid #fcd34d',
                  fontFamily: 'inherit',
                  fontSize: '0.875rem',
                  resize: 'vertical',
                  marginBottom: 8
                }}
              />
              <div style={{ display: 'flex', justifyContent: 'flex-end', gap: 8 }}>
                <button
                  className="btn btn-ghost btn-sm"
                  onClick={() => setNotesOpen(false)}
                >
                  Close
                </button>
                <button
                  className="btn btn-primary btn-sm"
                  style={{ backgroundColor: '#d97706', borderColor: '#d97706' }}
                  onClick={handleSaveNote}
                  disabled={savingNote}
                >
                  {savingNote ? 'Saving...' : '💾 Save Note'}
                </button>
              </div>
            </div>
          )}

          {/* Previous Practice Attempts History */}
          {practiceHistory.length > 0 && (
            <div style={{
              marginTop: 18,
              padding: '12px 18px',
              backgroundColor: '#f0fdf4',
              border: '1px solid #bbf7d0',
              borderRadius: '10px',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'space-between',
              flexWrap: 'wrap',
              gap: 10
            }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
                <span>🎯</span>
                <span style={{ fontSize: '0.8125rem', fontWeight: 600, color: '#166534' }}>
                  Practice History: {practiceHistory.length} attempt{practiceHistory.length > 1 ? 's' : ''} completed.
                </span>
                <span style={{ fontSize: '0.75rem', color: '#15803d' }}>
                  Latest score: <strong>{practiceHistory[0].self_score} / {practiceHistory[0].max_score}</strong> ({Math.floor(practiceHistory[0].duration_seconds / 60)} mins)
                </span>
              </div>
              <button
                className="btn btn-ghost btn-sm"
                style={{ fontSize: '0.75rem', color: '#166534' }}
                onClick={() => handleStartPractice(180)}
              >
                Re-take Mock Test →
              </button>
            </div>
          )}

          {/* Official Verification Source Banner */}
          {paper.source_url && (
            <div style={{
              marginTop: 20,
              padding: '12px 16px',
              background: 'rgba(0, 0, 0, 0.015)',
              border: '1px solid var(--color-border)',
              borderRadius: '10px',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'space-between',
              flexWrap: 'wrap',
              gap: 12,
            }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
                <span style={{ fontSize: '1.25rem' }}>🏛️</span>
                <div>
                  <div style={{ fontSize: '0.7rem', textTransform: 'uppercase', letterSpacing: '0.05em', color: 'var(--text-muted)' }}>
                    Official Document Source
                  </div>
                  <div style={{ fontSize: '0.8125rem', fontWeight: 600, color: 'var(--text-primary)' }}>
                    {paper.source_name || 'Official Examination Portal'}
                  </div>
                </div>
              </div>
              <a
                href={paper.source_url}
                target="_blank"
                rel="noopener noreferrer"
                className="btn btn-ghost btn-sm"
                style={{ fontSize: '0.75rem' }}
              >
                ↗ View Source Repository
              </a>
            </div>
          )}
        </div>

        {/* ── PDF IN-PLATFORM VIEWER WITH ANSWER KEY INTEGRATION ── */}
        <div
          ref={viewerContainerRef}
          style={{
            backgroundColor: '#ffffff',
            borderRadius: '16px',
            border: '1px solid var(--color-border)',
            overflow: 'hidden',
            boxShadow: 'var(--shadow-md)',
            marginBottom: 'var(--space-8)',
          }}
        >
          {/* Viewer Control & Switcher Bar */}
          <div style={{
            display: 'flex',
            justifyContent: 'space-between',
            alignItems: 'center',
            padding: '12px 18px',
            backgroundColor: '#f8fafc',
            borderBottom: '1px solid #e2e8f0',
            flexWrap: 'wrap',
            gap: 10,
          }}>
            {/* Document Tabs */}
            <div style={{ display: 'flex', alignItems: 'center', gap: 8, flexWrap: 'wrap' }}>
              <button
                type="button"
                className={`btn ${activeDoc === 'paper' ? 'btn-primary' : 'btn-ghost'} btn-sm`}
                style={{ fontSize: '0.8125rem', padding: '5px 14px', height: 'auto' }}
                onClick={() => setActiveDoc('paper')}
              >
                📑 Question Paper
              </button>

              {hasKey && (
                <button
                  type="button"
                  className={`btn ${activeDoc === 'key' ? 'btn-primary' : 'btn-ghost'} btn-sm`}
                  style={{
                    fontSize: '0.8125rem',
                    padding: '5px 14px',
                    height: 'auto',
                    backgroundColor: activeDoc === 'key' ? '#10B981' : 'transparent',
                    borderColor: '#10B981',
                    color: activeDoc === 'key' ? '#fff' : '#10B981',
                    fontWeight: 600
                  }}
                  onClick={() => setActiveDoc('key')}
                >
                  🔑 Official Answer Key
                </button>
              )}

              {hasTextbooks && (
                <button
                  type="button"
                  className={`btn ${activeDoc === 'textbook' ? 'btn-primary' : 'btn-ghost'} btn-sm`}
                  style={{
                    fontSize: '0.8125rem',
                    padding: '5px 14px',
                    height: 'auto',
                    backgroundColor: activeDoc === 'textbook' ? '#3B82F6' : 'transparent',
                    borderColor: '#3B82F6',
                    color: activeDoc === 'textbook' ? '#fff' : '#3B82F6',
                    fontWeight: 600
                  }}
                  onClick={() => setActiveDoc('textbook')}
                >
                  📚 Curriculum Textbook
                </button>
              )}

              {(hasKey || hasTextbooks) && (
                <button
                  type="button"
                  className={`btn ${activeDoc === 'split' ? 'btn-primary' : 'btn-ghost'} btn-sm`}
                  style={{
                    fontSize: '0.8125rem',
                    padding: '5px 14px',
                    height: 'auto',
                    backgroundColor: activeDoc === 'split' ? '#6366F1' : 'transparent',
                    borderColor: '#6366F1',
                    color: activeDoc === 'split' ? '#fff' : '#6366F1',
                    fontWeight: 600
                  }}
                  onClick={() => {
                    setActiveDoc('split')
                    if (!hasKey && hasTextbooks) {
                      setSplitSecondary('textbook')
                    }
                  }}
                  title="Compare Question Paper and Answer Key/Textbook side-by-side"
                >
                  ◫ Side-by-Side View
                </button>
              )}
            </div>

            {/* View Controls */}
            <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
              <button
                type="button"
                className="btn btn-ghost btn-sm"
                style={{
                  fontSize: '0.75rem',
                  padding: '4px 10px',
                  height: 'auto',
                  border: '1px solid',
                  borderColor: useProxy ? '#10B981' : '#cbd5e1',
                  backgroundColor: useProxy ? 'rgba(16, 185, 129, 0.12)' : 'transparent',
                  color: useProxy ? '#059669' : 'inherit',
                  fontWeight: useProxy ? 700 : 500
                }}
                onClick={() => {
                  const nextProxy = !useProxy
                  setUseProxy(nextProxy)
                  addToast(nextProxy ? 'Proxy stream activated (bypasses browser iframe restrictions)' : 'Direct stream activated', 'info')
                }}
                title="Toggle Backend Proxy stream to bypass X-Frame-Options or ISP/Gov portal iframe embedding blocks"
              >
                {useProxy ? '🛡️ Proxy Active' : '🛡️ Proxy Stream'}
              </button>

              {activeDoc !== 'split' && (
                <button
                  type="button"
                  className="btn btn-ghost btn-sm"
                  style={{ fontSize: '0.75rem', padding: '4px 10px', height: 'auto', border: '1px solid #cbd5e1' }}
                  onClick={() => setViewerMode(m => m === 'embed' ? 'canvas' : 'embed')}
                  title="Switch between high-performance native PDF view and canvas view"
                >
                  {viewerMode === 'embed' ? '🔄 Canvas View' : '🔄 Native View'}
                </button>
              )}

              <button
                type="button"
                className="btn btn-ghost btn-sm"
                style={{ fontSize: '0.75rem', padding: '4px 10px', height: 'auto', border: '1px solid #cbd5e1' }}
                onClick={toggleFullscreen}
                title="Fullscreen mode"
              >
                {isFullscreen ? '✕ Exit Fullscreen' : '⛶ Fullscreen'}
              </button>

              <a
                href={currentViewUrl}
                target="_blank"
                rel="noopener noreferrer"
                className="btn btn-primary btn-sm"
                style={{ fontSize: '0.75rem', padding: '4px 12px', height: 'auto' }}
              >
                ↗ Popout
              </a>
            </div>
          </div>

          {/* Textbook Selector Sub-bar when viewing Textbook */}
          {activeDoc === 'textbook' && textbooks.length > 1 && (
            <div style={{
              display: 'flex',
              alignItems: 'center',
              gap: 8,
              padding: '8px 18px',
              backgroundColor: '#eff6ff',
              borderBottom: '1px solid #dbeafe',
              overflowX: 'auto'
            }}>
              <span style={{ fontSize: '0.75rem', fontWeight: 600, color: '#1e40af', whiteSpace: 'nowrap' }}>
                Select Book:
              </span>
              {textbooks.map((tb, idx) => (
                <button
                  key={tb.id}
                  type="button"
                  onClick={() => setSelectedTextbookIndex(idx)}
                  style={{
                    padding: '3px 10px',
                    borderRadius: '20px',
                    fontSize: '0.75rem',
                    fontWeight: 600,
                    border: '1px solid',
                    borderColor: selectedTextbookIndex === idx ? '#2563eb' : '#93c5fd',
                    backgroundColor: selectedTextbookIndex === idx ? '#2563eb' : '#ffffff',
                    color: selectedTextbookIndex === idx ? '#ffffff' : '#1e40af',
                    cursor: 'pointer',
                    whiteSpace: 'nowrap'
                  }}
                >
                  {tb.board} · {tb.title}
                </button>
              ))}
            </div>
          )}

          {/* ── Official Exam Blueprint & Section Pattern ── */}
          {blueprint && (
            <div style={{
              marginTop: 14,
              marginBottom: 20,
              padding: '14px 18px',
              backgroundColor: 'rgba(99, 102, 241, 0.04)',
              border: '1px solid rgba(99, 102, 241, 0.22)',
              borderRadius: '12px'
            }}>
              <div
                style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', cursor: 'pointer', flexWrap: 'wrap', gap: 8 }}
                onClick={() => setBlueprintOpen(!blueprintOpen)}
              >
                <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
                  <span style={{ fontSize: '1.15rem' }}>📋</span>
                  <div>
                    <span style={{ fontWeight: 700, fontSize: '0.875rem', color: '#4338ca' }}>
                      {blueprint.title}
                    </span>
                    <div style={{ fontSize: '0.72rem', color: 'var(--text-muted)' }}>
                      Click to {blueprintOpen ? 'collapse' : 'view'} section breakdown & marking scheme
                    </div>
                  </div>
                </div>
                <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
                  <span style={{ fontSize: '0.75rem', fontWeight: 600, color: '#4f46e5', backgroundColor: '#e0e7ff', padding: '2px 8px', borderRadius: '4px' }}>
                    {blueprint.duration} · {blueprint.negativeMarking}
                  </span>
                  <span style={{ fontSize: '0.8125rem', color: '#4f46e5' }}>
                    {blueprintOpen ? '▲' : '▼'}
                  </span>
                </div>
              </div>

              {blueprintOpen && (
                <div style={{ marginTop: 12, borderTop: '1px solid rgba(99, 102, 241, 0.15)', paddingTop: 12 }}>
                  <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: 10 }}>
                    {blueprint.sections.map((sec, idx) => (
                      <div
                        key={idx}
                        style={{
                          backgroundColor: '#ffffff',
                          padding: '10px 14px',
                          borderRadius: '8px',
                          border: '1px solid var(--color-border)',
                          display: 'flex',
                          flexDirection: 'column',
                          gap: 2
                        }}
                      >
                        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                          <span style={{ fontWeight: 700, fontSize: '0.8125rem', color: 'var(--text-primary)' }}>{sec.name}</span>
                          <span style={{ fontSize: '0.75rem', fontWeight: 600, color: '#4f46e5' }}>{sec.marks}</span>
                        </div>
                        <div style={{ fontSize: '0.75rem', color: 'var(--text-secondary)' }}>{sec.desc}</div>
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </div>
          )}

          {/* ── VIEWER CONTENT ── */}
          {activeDoc === 'split' && (hasKey || hasTextbooks) ? (
            /* ◫ SIDE-BY-SIDE SPLIT VIEW */
            <div style={{
              display: 'grid',
              gridTemplateColumns: '1fr 1fr',
              gap: '2px',
              backgroundColor: '#cbd5e1',
              width: '100%',
              height: isFullscreen ? 'calc(100vh - 60px)' : '850px'
            }}>
              {/* Left Pane: Question Paper */}
              <div style={{ height: '100%', display: 'flex', flexDirection: 'column', backgroundColor: '#525659' }}>
                <div style={{
                  padding: '8px 14px',
                  backgroundColor: '#1e293b',
                  color: '#f8fafc',
                  fontSize: '0.78125rem',
                  fontWeight: 600,
                  display: 'flex',
                  justifyContent: 'space-between',
                  alignItems: 'center'
                }}>
                  <span>📑 Question Paper</span>
                  <a href={pdfUrl} target="_blank" rel="noopener noreferrer" style={{ color: '#93c5fd', textDecoration: 'none', fontSize: '0.75rem' }}>
                    ↗ Full Tab
                  </a>
                </div>
                <iframe
                  src={`${leftPaneUrl}#toolbar=1&navpanes=0`}
                  title="Question Paper"
                  width="100%"
                  height="100%"
                  style={{ border: 'none', flex: 1, display: 'block', backgroundColor: '#525659' }}
                />
              </div>

              {/* Right Pane: Official Answer Key OR Prescribed Textbook */}
              <div style={{ height: '100%', display: 'flex', flexDirection: 'column', backgroundColor: '#525659' }}>
                <div style={{
                  padding: '6px 14px',
                  backgroundColor: splitSecondary === 'textbook' ? '#1e3a8a' : '#064e3b',
                  color: '#ecfdf5',
                  fontSize: '0.78125rem',
                  fontWeight: 600,
                  display: 'flex',
                  justifyContent: 'space-between',
                  alignItems: 'center',
                  flexWrap: 'wrap',
                  gap: 8
                }}>
                  <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
                    {hasKey && hasTextbooks ? (
                      <div style={{ display: 'flex', gap: 4, background: 'rgba(0,0,0,0.25)', padding: '2px', borderRadius: '6px' }}>
                        <button
                          type="button"
                          onClick={() => setSplitSecondary('key')}
                          style={{
                            padding: '2px 8px',
                            fontSize: '0.7rem',
                            fontWeight: 600,
                            borderRadius: '4px',
                            border: 'none',
                            backgroundColor: splitSecondary === 'key' ? '#10B981' : 'transparent',
                            color: splitSecondary === 'key' ? '#ffffff' : '#94a3b8',
                            cursor: 'pointer'
                          }}
                        >
                          🔑 Answer Key
                        </button>
                        <button
                          type="button"
                          onClick={() => setSplitSecondary('textbook')}
                          style={{
                            padding: '2px 8px',
                            fontSize: '0.7rem',
                            fontWeight: 600,
                            borderRadius: '4px',
                            border: 'none',
                            backgroundColor: splitSecondary === 'textbook' ? '#3B82F6' : 'transparent',
                            color: splitSecondary === 'textbook' ? '#ffffff' : '#94a3b8',
                            cursor: 'pointer'
                          }}
                        >
                          📚 Textbook
                        </button>
                      </div>
                    ) : (
                      <span>{splitSecondary === 'textbook' || !hasKey ? '📚 Prescribed Textbook' : '🔑 Official Answer Key / Solutions'}</span>
                    )}

                    {splitSecondary === 'textbook' && textbooks.length > 1 && (
                      <select
                        value={selectedTextbookIndex}
                        onChange={(e) => setSelectedTextbookIndex(Number(e.target.value))}
                        style={{
                          fontSize: '0.7rem',
                          padding: '2px 6px',
                          borderRadius: '4px',
                          backgroundColor: '#1e293b',
                          color: '#fff',
                          border: '1px solid #475569'
                        }}
                      >
                        {textbooks.map((tb, i) => (
                          <option key={tb.id} value={i}>
                            {tb.board}: {tb.title.length > 25 ? `${tb.title.slice(0, 25)}…` : tb.title}
                          </option>
                        ))}
                      </select>
                    )}
                  </div>

                  <a
                    href={splitSecondary === 'textbook' && activeTextbook ? activeTextbook.pdf_url : paper.answer_key_pdf_url}
                    target="_blank"
                    rel="noopener noreferrer"
                    style={{ color: splitSecondary === 'textbook' ? '#93c5fd' : '#6ee7b7', textDecoration: 'none', fontSize: '0.75rem' }}
                  >
                    ↗ Full Tab
                  </a>
                </div>
                <iframe
                  src={`${rightPaneUrl}#toolbar=1&navpanes=0`}
                  title={splitSecondary === 'textbook' ? 'Curriculum Textbook' : 'Official Answer Key'}
                  width="100%"
                  height="100%"
                  style={{ border: 'none', flex: 1, display: 'block', backgroundColor: '#525659' }}
                />
              </div>
            </div>
          ) : (
            /* SINGLE DOCUMENT VIEW (Question Paper, Answer Key, OR Curriculum Textbook) */
            currentViewUrl ? (
              viewerMode === 'embed' ? (
                /* Native Browser PDF Engine */
                <div style={{ width: '100%', height: isFullscreen ? 'calc(100vh - 60px)' : '850px', background: '#525659' }}>
                  <iframe
                    src={`${currentViewUrl}#toolbar=1&navpanes=1&scrollbar=1`}
                    title={activeDoc === 'key' ? 'Official Answer Key' : activeDoc === 'textbook' ? (activeTextbook?.title || 'Curriculum Textbook') : paper.title}
                    width="100%"
                    height="100%"
                    style={{ border: 'none', display: 'block', backgroundColor: '#525659' }}
                  />
                </div>
              ) : (
                /* Canvas react-pdf mode */
                <div style={{ padding: '20px', background: '#f1f5f9', minHeight: '600px', display: 'flex', flexDirection: 'column', alignItems: 'center' }}>
                  <div style={{ display: 'flex', alignItems: 'center', gap: 12, marginBottom: 16 }}>
                    <button
                      className="btn btn-ghost btn-sm"
                      onClick={() => setCurrentPage(p => Math.max(1, p - 1))}
                      disabled={currentPage <= 1}
                    >
                      ← Previous Page
                    </button>
                    <span style={{ fontSize: '0.875rem', fontWeight: 600, color: '#334155' }}>
                      Page {currentPage} of {numPages || '…'}
                    </span>
                    <button
                      className="btn btn-ghost btn-sm"
                      onClick={() => setCurrentPage(p => Math.min(numPages || p, p + 1))}
                      disabled={currentPage >= (numPages || 1)}
                    >
                      Next Page →
                    </button>
                  </div>

                  <div style={{ boxShadow: '0 4px 12px rgba(0,0,0,0.15)', borderRadius: '8px', overflow: 'hidden', background: '#fff' }}>
                    <Document
                      file={currentViewUrl}
                      onLoadSuccess={({ numPages }) => setNumPages(numPages)}
                      onLoadError={(err) => {
                        console.error('Canvas load error, falling back to embedded viewer', err)
                        setViewerMode('embed')
                      }}
                      loading={
                        <div style={{ padding: 40, textAlign: 'center', color: '#64748b' }}>
                          Loading document pages...
                        </div>
                      }
                    >
                      <Page
                        pageNumber={currentPage}
                        width={Math.min(window.innerWidth - 60, 800)}
                        renderTextLayer={true}
                        renderAnnotationLayer={true}
                      />
                    </Document>
                  </div>
                </div>
              )
            ) : (
              <div style={{ padding: '60px 20px', textAlign: 'center', background: '#f8fafc' }}>
                <div style={{ fontSize: '3rem', marginBottom: 12 }}>📄</div>
                <h3 style={{ marginBottom: 8, color: '#1e293b' }}>PDF Document Ready</h3>
                <p style={{ color: '#64748b', marginBottom: 20 }}>
                  Click below to view the full question paper.
                </p>
                <button
                  className="btn btn-primary"
                  onClick={handleLoadPDF}
                  disabled={pdfLoading}
                >
                  {pdfLoading ? '⏳ Loading PDF...' : '📖 View Question Paper'}
                </button>
              </div>
            )
          )}
        </div>

      {/* ── INTERACTIVE EXAM PRACTICE & SELF-SCORING SIMULATOR MODAL ── */}
      {practiceModalOpen && (
        <div style={{
          position: 'fixed',
          top: 0,
          left: 0,
          right: 0,
          bottom: 0,
          backgroundColor: 'rgba(15, 23, 42, 0.85)',
          backdropFilter: 'blur(8px)',
          zIndex: 9999,
          display: 'flex',
          flexDirection: 'column',
          padding: '16px',
        }}>
          {/* Top Control Bar */}
          <div style={{
            backgroundColor: '#1e293b',
            borderRadius: '12px 12px 0 0',
            padding: '14px 24px',
            display: 'flex',
            justifyContent: 'space-between',
            alignItems: 'center',
            color: '#f8fafc',
            flexWrap: 'wrap',
            gap: 12,
            borderBottom: '1px solid #334155'
          }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: 12 }}>
              <span style={{ fontSize: '1.25rem' }}>⏱️</span>
              <div>
                <span style={{ fontWeight: 700, fontSize: '0.9375rem', color: '#f8fafc' }}>
                  Exam Practice Simulator — {paper.title}
                </span>
                <div style={{ fontSize: '0.75rem', color: '#94a3b8' }}>
                  Authentic Timed Examination Environment & Self-Evaluation
                </div>
              </div>
            </div>

            {/* Timer Display & Controls */}
            <div style={{ display: 'flex', alignItems: 'center', gap: 12 }}>
              <div style={{
                fontSize: '1.25rem',
                fontWeight: 700,
                fontFamily: 'monospace',
                backgroundColor: timerSeconds < 300 ? '#7f1d1d' : '#0f172a',
                color: timerSeconds < 300 ? '#fca5a5' : '#38bdf8',
                padding: '6px 14px',
                borderRadius: '8px',
                border: '1px solid #334155'
              }}>
                {formatTimer(timerSeconds)}
              </div>

              {!practiceFinished ? (
                <>
                  <button
                    className="btn btn-ghost btn-sm"
                    style={{ color: '#f8fafc', border: '1px solid #475569' }}
                    onClick={() => setTimerRunning(!timerRunning)}
                  >
                    {timerRunning ? '⏸ Pause' : '▶ Resume'}
                  </button>
                  <button
                    className="btn btn-primary btn-sm"
                    style={{ backgroundColor: '#10B981', borderColor: '#10B981', fontWeight: 600 }}
                    onClick={handleFinishPractice}
                  >
                    🏁 Finish & Reveal Key
                  </button>
                </>
              ) : (
                <span style={{ fontSize: '0.8125rem', color: '#34d399', fontWeight: 600 }}>
                  ✓ Exam Submitted — Evaluate Below
                </span>
              )}

              <button
                className="btn btn-ghost btn-sm"
                style={{ color: '#94a3b8' }}
                onClick={() => setPracticeModalOpen(false)}
              >
                ✕ Close
              </button>
            </div>
          </div>

          {/* Dual Split Testing Workspace */}
          <div style={{
            flex: 1,
            display: 'grid',
            gridTemplateColumns: '1.2fr 1fr',
            gap: '2px',
            backgroundColor: '#334155',
            overflow: 'hidden',
            borderRadius: '0 0 12px 12px'
          }}>
            {/* Left Pane: Question Paper */}
            <div style={{ height: '100%', display: 'flex', flexDirection: 'column', backgroundColor: '#525659' }}>
              <div style={{
                padding: '8px 16px',
                backgroundColor: '#0f172a',
                color: '#94a3b8',
                fontSize: '0.78125rem',
                fontWeight: 600
              }}>
                📑 Genuine Question Paper (Solve on paper or rough scratchpad)
              </div>
              <iframe
                src={`${pdfUrl}#toolbar=0&navpanes=0`}
                title="Exam Simulator Question Paper"
                width="100%"
                height="100%"
                style={{ border: 'none', flex: 1, display: 'block', backgroundColor: '#525659' }}
              />
            </div>

            {/* Right Pane: Scratchpad (during exam) OR Answer Key & Score Recording (post-exam) */}
            <div style={{ height: '100%', display: 'flex', flexDirection: 'column', backgroundColor: '#ffffff', overflowY: 'auto' }}>
              {!practiceFinished ? (
                /* IN-PROGRESS EXAM SCRATCHPAD */
                <div style={{ padding: '24px', display: 'flex', flexDirection: 'column', height: '100%' }}>
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 12 }}>
                    <span style={{ fontWeight: 700, fontSize: '0.9375rem', color: '#1e293b' }}>
                      ✍️ Rough Answer Sheet & Checklist
                    </span>
                    <span style={{ fontSize: '0.75rem', color: '#64748b' }}>
                      Track your question numbers & rough calculations
                    </span>
                  </div>
                  <textarea
                    value={scratchText}
                    onChange={(e) => setScratchText(e.target.value)}
                    placeholder="Q1: (A)&#10;Q2: 42.5 J&#10;Q3: Photosynthesis light reaction formula...&#10;Q4: Skipped (review later)"
                    style={{
                      flex: 1,
                      width: '100%',
                      padding: '14px',
                      borderRadius: '8px',
                      border: '1px solid #cbd5e1',
                      fontFamily: 'monospace',
                      fontSize: '0.875rem',
                      lineHeight: 1.6,
                      resize: 'none',
                      marginBottom: 16,
                      backgroundColor: '#f8fafc'
                    }}
                  />
                  <div style={{
                    padding: '14px 18px',
                    backgroundColor: '#eff6ff',
                    borderRadius: '8px',
                    border: '1px solid #bfdbfe',
                    marginBottom: 16
                  }}>
                    <div style={{ fontWeight: 600, fontSize: '0.8125rem', color: '#1e40af', marginBottom: 4 }}>
                      💡 Real Exam Strategy
                    </div>
                    <p style={{ margin: 0, fontSize: '0.75rem', color: '#1e3a8a', lineHeight: 1.45 }}>
                      Attempt every section with realistic discipline. When ready to evaluate, click <strong>"Finish & Reveal Key"</strong> at the top right to verify your responses against the board marking scheme.
                    </p>
                  </div>
                  <button
                    className="btn btn-primary"
                    style={{ backgroundColor: '#10B981', borderColor: '#10B981', width: '100%', fontWeight: 700 }}
                    onClick={handleFinishPractice}
                  >
                    🏁 Finish Exam & Review Scoring Scheme →
                  </button>
                </div>
              ) : (
                /* POST-EXAM EVALUATION & SCORING */
                <div style={{ display: 'flex', flexDirection: 'column', height: '100%' }}>
                  <div style={{
                    padding: '16px 20px',
                    backgroundColor: '#064e3b',
                    color: '#ecfdf5',
                    display: 'flex',
                    justifyContent: 'space-between',
                    alignItems: 'center'
                  }}>
                    <div>
                      <div style={{ fontWeight: 700, fontSize: '0.9375rem' }}>
                        🔑 Official Scoring Scheme & Self-Evaluation
                      </div>
                      <div style={{ fontSize: '0.75rem', color: '#a7f3d0' }}>
                        Time taken: {Math.floor((timerDuration - timerSeconds) / 60)} minutes
                      </div>
                    </div>
                  </div>

                  {/* Top Score Input Form */}
                  <div style={{
                    padding: '16px 20px',
                    backgroundColor: '#f0fdf4',
                    borderBottom: '1px solid #bbf7d0',
                    display: 'flex',
                    flexDirection: 'column',
                    gap: 10
                  }}>
                    <div style={{ display: 'flex', gap: 12, alignItems: 'center', flexWrap: 'wrap' }}>
                      <div style={{ display: 'flex', alignItems: 'center', gap: 6 }}>
                        <span style={{ fontSize: '0.8125rem', fontWeight: 600, color: '#166534' }}>Your Score:</span>
                        <input
                          type="number"
                          value={selfScore}
                          onChange={(e) => setSelfScore(e.target.value)}
                          placeholder="e.g. 84"
                          style={{
                            width: '90px',
                            padding: '6px 10px',
                            borderRadius: '6px',
                            border: '1px solid #86efac',
                            fontWeight: 700,
                            fontSize: '0.875rem'
                          }}
                        />
                      </div>
                      <div style={{ display: 'flex', alignItems: 'center', gap: 6 }}>
                        <span style={{ fontSize: '0.8125rem', fontWeight: 600, color: '#166534' }}>Out of:</span>
                        <input
                          type="number"
                          value={maxScore}
                          onChange={(e) => setMaxScore(e.target.value)}
                          placeholder="100"
                          style={{
                            width: '80px',
                            padding: '6px 10px',
                            borderRadius: '6px',
                            border: '1px solid #86efac',
                            fontWeight: 700,
                            fontSize: '0.875rem'
                          }}
                        />
                      </div>
                      <button
                        className="btn btn-primary btn-sm"
                        style={{ backgroundColor: '#16a34a', borderColor: '#16a34a', fontWeight: 600 }}
                        onClick={handleRecordAttempt}
                        disabled={recordingAttempt}
                      >
                        {recordingAttempt ? 'Saving...' : '💾 Record Score in Profile'}
                      </button>
                    </div>
                  </div>

                  {/* Answer Key Document Viewer */}
                  {hasKey ? (
                    <iframe
                      src={`${paper.answer_key_pdf_url}#toolbar=1&navpanes=0`}
                      title="Practice Official Answer Key"
                      width="100%"
                      height="100%"
                      style={{ border: 'none', flex: 1, display: 'block', backgroundColor: '#525659' }}
                    />
                  ) : (
                    <div style={{ padding: '30px', textAlign: 'center', color: '#64748b' }}>
                      <div style={{ fontSize: '2rem', marginBottom: 8 }}>📑</div>
                      <p>Official Answer Key is descriptive or institutional. Use your rough notes to record your score.</p>
                    </div>
                  )}
                </div>
              )}
            </div>
          </div>
        </div>
      )}

      </div>
    </div>
  )
}
