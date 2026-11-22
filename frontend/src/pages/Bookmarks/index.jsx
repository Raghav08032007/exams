/**
 * Student Study Hub & Analytics Dashboard
 * Tabs: Saved Papers | Practice Test History & Analytics | Revision Notes | Exam Readiness & Syllabus
 * Route: /bookmarks (auth-gated)
 */
import { useEffect, useState } from 'react'
import { Link, Navigate } from 'react-router-dom'
import {
  fetchBookmarks,
  removeBookmark,
  fetchUserPracticeSummary,
  fetchUserAllNotes,
  fetchUserSyllabusProgress,
  updateUserSyllabusProgress
} from '../../api/client'
import { AnswerKeyBadge, LanguageBadge } from '../../components/ui/Badges'
import { PageSkeleton } from '../../components/ui/Skeleton'
import { useAuthStore, useToastStore } from '../../store'
import { useSEO } from '../../hooks/useSEO'

const SYLLABUS_MAP = {
  'class-10': [
    {
      subject: 'Mathematics',
      units: [
        { name: 'Number Systems', marks: 6, topics: ['Real Numbers', 'Fundamental Theorem of Arithmetic', 'Revisiting Irrational Numbers'] },
        { name: 'Algebra', marks: 20, topics: ['Polynomials', 'Pair of Linear Equations in Two Variables', 'Quadratic Equations', 'Arithmetic Progressions'] },
        { name: 'Coordinate Geometry', marks: 6, topics: ['Distance Formula', 'Section Formula'] },
        { name: 'Geometry', marks: 15, topics: ['Triangles (Similarity Criteria & Theorems)', 'Circles (Tangents to a Circle)'] },
        { name: 'Trigonometry', marks: 12, topics: ['Introduction to Trigonometry', 'Trigonometric Identities', 'Heights and Distances'] },
        { name: 'Mensuration', marks: 10, topics: ['Areas Related to Circles', 'Surface Areas and Volumes'] },
        { name: 'Statistics & Probability', marks: 11, topics: ['Mean, Median, Mode of Grouped Data', 'Probability (Classical Definition)'] },
      ]
    },
    {
      subject: 'Science',
      units: [
        { name: 'Chemical Substances - Nature & Behaviour', marks: 25, topics: ['Chemical Reactions & Equations', 'Acids, Bases and Salts', 'Metals and Non-metals', 'Carbon and its Compounds'] },
        { name: 'World of Living', marks: 25, topics: ['Life Processes (Nutrition, Respiration, Transport, Excretion)', 'Control and Coordination', 'How do Organisms Reproduce?', 'Heredity and Evolution'] },
        { name: 'Natural Phenomena', marks: 12, topics: ['Reflection and Refraction of Light', 'Human Eye and Colourful World'] },
        { name: 'Effects of Current', marks: 13, topics: ['Electricity (Ohm’s Law, Resistance)', 'Magnetic Effects of Electric Current'] },
        { name: 'Natural Resources', marks: 5, topics: ['Our Environment (Ecosystem, Ozone Depletion, Waste Management)'] },
      ]
    }
  ],
  'class-12': [
    {
      subject: 'Physics',
      units: [
        { name: 'Electrostatics & Current Electricity', marks: 16, topics: ['Electric Charges and Fields', 'Electrostatic Potential & Capacitance', 'Current Electricity & Kirchhoff’s Laws'] },
        { name: 'Magnetic Effects of Current & Magnetism', marks: 17, topics: ['Moving Charges and Magnetism', 'Magnetism and Matter', 'Electromagnetic Induction', 'Alternating Currents'] },
        { name: 'Electromagnetic Waves & Optics', marks: 18, topics: ['Electromagnetic Waves', 'Ray Optics and Optical Instruments', 'Wave Optics & Interference'] },
        { name: 'Dual Nature of Radiation & Atoms/Nuclei', marks: 12, topics: ['Photoelectric Effect', 'Atoms (Bohr Model)', 'Nuclei (Mass Defect & Binding Energy)'] },
        { name: 'Electronic Devices', marks: 7, topics: ['Semiconductor Electronics (p-n Junction Diode, Rectifiers)'] },
      ]
    },
    {
      subject: 'Chemistry',
      units: [
        { name: 'Physical Chemistry', marks: 23, topics: ['Solutions', 'Electrochemistry', 'Chemical Kinetics'] },
        { name: 'Inorganic Chemistry', marks: 14, topics: ['d- and f-Block Elements', 'Coordination Compounds'] },
        { name: 'Organic Chemistry', marks: 33, topics: ['Haloalkanes and Haloarenes', 'Alcohols, Phenols and Ethers', 'Aldehydes, Ketones and Carboxylic Acids', 'Amines', 'Biomolecules'] },
      ]
    }
  ],
  'jee': [
    {
      subject: 'Mathematics',
      units: [
        { name: 'Calculus & Coordinate Geometry', marks: 40, topics: ['Straight Lines & Circles', 'Conic Sections', 'Limits, Continuity & Derivatives', 'Definite Integrals & Area Under Curves', 'Differential Equations'] },
        { name: 'Algebra & Vectors', marks: 40, topics: ['Complex Numbers & Quadratic Equations', 'Matrices & Determinants', 'Permutations & Combinations', 'Vector Algebra & 3D Geometry'] },
      ]
    },
    {
      subject: 'Physics',
      units: [
        { name: 'Mechanics & Electromagnetism', marks: 50, topics: ['Kinematics & Newton’s Laws', 'Work, Energy & Power', 'Rotational Motion', 'Gravitation', 'Electrostatics & Current Electricity', 'Electromagnetic Induction'] },
        { name: 'Modern Physics & Optics', marks: 30, topics: ['Wave & Ray Optics', 'Dual Nature of Matter', 'Atoms & Nuclei', 'Semiconductors'] },
      ]
    }
  ],
  'neet': [
    {
      subject: 'Biology',
      units: [
        { name: 'Genetics, Evolution & Biotechnology', marks: 180, topics: ['Principles of Inheritance & Variation', 'Molecular Basis of Inheritance', 'Evolution', 'Biotechnology: Principles & Applications'] },
        { name: 'Human & Plant Physiology', marks: 180, topics: ['Photosynthesis & Respiration in Plants', 'Plant Growth & Development', 'Breathing, Circulation & Excretion in Humans', 'Neural Control & Chemical Coordination'] },
        { name: 'Ecology & Human Health', marks: 100, topics: ['Human Health and Disease', 'Organisms and Populations', 'Ecosystem & Biodiversity Conservation'] },
      ]
    }
  ]
}

export default function BookmarksPage() {
  const { user } = useAuthStore()
  const { addToast } = useToastStore()

  const [activeTab, setActiveTab] = useState('bookmarks') // 'bookmarks' | 'practice' | 'notes' | 'readiness'
  const [bookmarks, setBookmarks] = useState([])
  const [practiceAttempts, setPracticeAttempts] = useState([])
  const [userNotes, setUserNotes] = useState([])
  const [loading, setLoading] = useState(true)
  const [removing, setRemoving] = useState(null)

  // Syllabus tracker state
  const [selectedExamSyllabus, setSelectedExamSyllabus] = useState('class-10')
  const [selectedSubjectIndex, setSelectedSubjectIndex] = useState(0)
  const [completedTopics, setCompletedTopics] = useState(new Set())
  const [syllabusLoading, setSyllabusLoading] = useState(false)

  useSEO({
    title: 'My Study Hub & Practice Analytics — ExamVault',
    description: 'Track your saved papers, timed mock test performance, self-evaluation scores, and personal revision notes.'
  })

  useEffect(() => {
    if (!user) return
    setLoading(true)
    Promise.all([
      fetchBookmarks().catch(() => []),
      fetchUserPracticeSummary().catch(() => []),
      fetchUserAllNotes().catch(() => [])
    ])
      .then(([bms, prs, nts]) => {
        setBookmarks(bms || [])
        setPracticeAttempts(prs || [])
        setUserNotes(nts || [])
      })
      .finally(() => setLoading(false))
  }, [user])

  // Fetch completed syllabus topics whenever exam changes
  useEffect(() => {
    if (!user) return
    setSyllabusLoading(true)
    fetchUserSyllabusProgress({ exam: selectedExamSyllabus })
      .then((res) => {
        setCompletedTopics(new Set(res.completed_topics || []))
      })
      .catch(() => {})
      .finally(() => setSyllabusLoading(false))
  }, [user, selectedExamSyllabus])

  const handleToggleTopic = async (topicName, subjectName) => {
    const isNowCompleted = !completedTopics.has(topicName)
    const nextSet = new Set(completedTopics)
    if (isNowCompleted) nextSet.add(topicName)
    else nextSet.delete(topicName)
    setCompletedTopics(nextSet)

    try {
      await updateUserSyllabusProgress({
        exam_slug: selectedExamSyllabus,
        subject_name: subjectName,
        topic_name: topicName,
        is_completed: isNowCompleted
      })
    } catch {
      addToast('Could not update topic progress', 'error')
    }
  }

  const handleRemove = async (paperId) => {
    setRemoving(paperId)
    try {
      await removeBookmark(paperId)
      setBookmarks((prev) => prev.filter((b) => b.paper_id !== paperId))
      addToast('Bookmark removed')
    } catch {
      addToast('Could not remove bookmark', 'error')
    } finally {
      setRemoving(null)
    }
  }

  // Redirect unauthenticated users
  if (!user) return <Navigate to="/login" state={{ from: { pathname: '/bookmarks' } }} replace />

  // Practice Analytics Calculations
  const totalPracticeSeconds = practiceAttempts.reduce((acc, a) => acc + (a.duration_seconds || 0), 0)
  const totalHours = (totalPracticeSeconds / 3600).toFixed(1)
  const scoredAttempts = practiceAttempts.filter(a => a.self_score !== null && a.max_score)
  const averagePercentage = scoredAttempts.length > 0
    ? Math.round(scoredAttempts.reduce((acc, a) => acc + (Number(a.self_score) / Number(a.max_score)) * 100, 0) / scoredAttempts.length)
    : null

  // Current selected syllabus
  const examSubjects = SYLLABUS_MAP[selectedExamSyllabus] || []
  const currentSubjectObj = examSubjects[selectedSubjectIndex] || examSubjects[0] || null
  const allTopicsInCurrentSubject = currentSubjectObj
    ? currentSubjectObj.units.flatMap(u => u.topics)
    : []
  const completedInSubject = allTopicsInCurrentSubject.filter(t => completedTopics.has(t)).length
  const subjectReadinessPct = allTopicsInCurrentSubject.length > 0
    ? Math.round((completedInSubject / allTopicsInCurrentSubject.length) * 100)
    : 0

  return (
    <div className="page-content">
      <div className="container" style={{ maxWidth: 1040 }}>
        
        {/* Header */}
        <div className="page-header" style={{ marginBottom: 'var(--space-6)' }}>
          <div className="page-header-eyebrow">Personal Learning Hub</div>
          <h1>My Study Hub & Analytics</h1>
          <p>Manage your saved papers, track timed mock exam scores, and monitor exam readiness across syllabus units.</p>
        </div>

        {/* Analytics Summary Banner */}
        <div style={{
          display: 'grid',
          gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))',
          gap: 16,
          backgroundColor: 'var(--surface)',
          padding: '20px 24px',
          borderRadius: '16px',
          border: '1px solid var(--color-border)',
          marginBottom: 'var(--space-6)',
          boxShadow: 'var(--shadow-sm)'
        }}>
          <div>
            <div className="mono" style={{ fontSize: '1.75rem', fontWeight: 700, color: '#2563EB' }}>
              {bookmarks.length}
            </div>
            <div style={{ fontSize: '0.8125rem', color: 'var(--text-muted)', textTransform: 'uppercase', letterSpacing: '0.05em' }}>
              Saved Question Papers
            </div>
          </div>
          <div>
            <div className="mono" style={{ fontSize: '1.75rem', fontWeight: 700, color: '#10B981' }}>
              {practiceAttempts.length}
            </div>
            <div style={{ fontSize: '0.8125rem', color: 'var(--text-muted)', textTransform: 'uppercase', letterSpacing: '0.05em' }}>
              Mock Tests Completed
            </div>
          </div>
          <div>
            <div className="mono" style={{ fontSize: '1.75rem', fontWeight: 700, color: '#F59E0B' }}>
              {totalHours}h
            </div>
            <div style={{ fontSize: '0.8125rem', color: 'var(--text-muted)', textTransform: 'uppercase', letterSpacing: '0.05em' }}>
              Time Spent Practicing
            </div>
          </div>
          <div>
            <div className="mono" style={{ fontSize: '1.75rem', fontWeight: 700, color: '#8B5CF6' }}>
              {averagePercentage !== null ? `${averagePercentage}%` : 'N/A'}
            </div>
            <div style={{ fontSize: '0.8125rem', color: 'var(--text-muted)', textTransform: 'uppercase', letterSpacing: '0.05em' }}>
              Average Evaluation Score
            </div>
          </div>
        </div>

        {/* Navigation Tabs */}
        <div style={{
          display: 'flex',
          gap: 10,
          borderBottom: '1px solid var(--color-border)',
          paddingBottom: '12px',
          marginBottom: 'var(--space-6)',
          flexWrap: 'wrap'
        }}>
          <button
            className={`btn ${activeTab === 'bookmarks' ? 'btn-primary' : 'btn-ghost'}`}
            style={{ fontWeight: 600, fontSize: '0.875rem' }}
            onClick={() => setActiveTab('bookmarks')}
          >
            ★ Saved Papers ({bookmarks.length})
          </button>
          <button
            className={`btn ${activeTab === 'practice' ? 'btn-primary' : 'btn-ghost'}`}
            style={{
              fontWeight: 600,
              fontSize: '0.875rem',
              backgroundColor: activeTab === 'practice' ? '#10B981' : 'transparent',
              borderColor: activeTab === 'practice' ? '#10B981' : 'var(--color-border)',
              color: activeTab === 'practice' ? '#fff' : 'var(--text-secondary)'
            }}
            onClick={() => setActiveTab('practice')}
          >
            🎯 Practice History & Scores ({practiceAttempts.length})
          </button>
          <button
            className={`btn ${activeTab === 'notes' ? 'btn-primary' : 'btn-ghost'}`}
            style={{
              fontWeight: 600,
              fontSize: '0.875rem',
              backgroundColor: activeTab === 'notes' ? '#F59E0B' : 'transparent',
              borderColor: activeTab === 'notes' ? '#F59E0B' : 'var(--color-border)',
              color: activeTab === 'notes' ? '#fff' : 'var(--text-secondary)'
            }}
            onClick={() => setActiveTab('notes')}
          >
            📝 Revision Notes ({userNotes.length})
          </button>
          <button
            className={`btn ${activeTab === 'readiness' ? 'btn-primary' : 'btn-ghost'}`}
            style={{
              fontWeight: 600,
              fontSize: '0.875rem',
              backgroundColor: activeTab === 'readiness' ? '#6366F1' : 'transparent',
              borderColor: activeTab === 'readiness' ? '#6366F1' : 'var(--color-border)',
              color: activeTab === 'readiness' ? '#fff' : 'var(--text-secondary)'
            }}
            onClick={() => setActiveTab('readiness')}
          >
            📊 Exam Readiness & Syllabus
          </button>
        </div>

        {loading && <PageSkeleton count={4} />}

        {/* ── TAB 1: BOOKMARKS LIST ── */}
        {!loading && activeTab === 'bookmarks' && (
          bookmarks.length === 0 ? (
            <div className="empty-state">
              <div className="empty-state-icon">☆</div>
              <h3>No bookmarks yet</h3>
              <p>Open any question paper and click "Bookmark" to pin it to your study list.</p>
              <Link to="/" className="btn btn-primary">Browse Papers</Link>
            </div>
          ) : (
            <div className="papers-list">
              {bookmarks.map((bookmark) => {
                const paper = bookmark.paper
                if (!paper) return null
                const slug = paper.exam?.slug || ''
                const accentColor = paper.exam?.accent_color_hex || '#8FB9A8'

                return (
                  <div key={bookmark.id} style={{ display: 'flex', alignItems: 'stretch', gap: 0 }}>
                    <Link
                      to={`/paper/${paper.id}`}
                      className="paper-item"
                      data-exam={slug}
                      style={{ flex: 1, borderRadius: 'var(--radius-lg) 0 0 var(--radius-lg)' }}
                    >
                      <div className="paper-item-year mono" style={{ color: accentColor }}>
                        {paper.year}
                      </div>
                      <div className="paper-item-content">
                        <div className="paper-item-title">{paper.title}</div>
                        <div className="paper-item-meta">
                          {paper.exam && (
                            <span className="badge" style={{ background: `${accentColor}26`, color: accentColor }}>
                              {paper.exam.name}
                            </span>
                          )}
                          <LanguageBadge language={paper.language} />
                          {paper.has_answer_key && <AnswerKeyBadge />}
                        </div>
                      </div>
                      <span className="btn btn-ghost btn-sm">View →</span>
                    </Link>
                    <button
                      onClick={() => handleRemove(paper.id)}
                      disabled={removing === paper.id}
                      title="Remove bookmark"
                      style={{
                        background: 'var(--color-bg-card)',
                        border: '1px solid rgba(255,255,255,0.06)',
                        borderLeft: 'none',
                        borderRadius: '0 var(--radius-lg) var(--radius-lg) 0',
                        padding: '0 var(--space-4)',
                        cursor: 'pointer',
                        color: 'var(--text-muted)',
                        fontSize: '1.125rem',
                        transition: 'all var(--transition-fast)',
                      }}
                      onMouseEnter={e => e.currentTarget.style.color = '#E05858'}
                      onMouseLeave={e => e.currentTarget.style.color = 'var(--text-muted)'}
                    >
                      {removing === paper.id ? '…' : '✕'}
                    </button>
                  </div>
                )
              })}
            </div>
          )
        )}

        {/* ── TAB 2: PRACTICE HISTORY & ANALYTICS ── */}
        {!loading && activeTab === 'practice' && (
          practiceAttempts.length === 0 ? (
            <div className="empty-state">
              <div className="empty-state-icon">⏱️</div>
              <h3>No practice attempts yet</h3>
              <p>Launch the "Practice Mode & Timer" on any paper card to complete a timed mock test and self-evaluate.</p>
              <Link to="/" className="btn btn-primary">Find a Paper to Practice</Link>
            </div>
          ) : (
            <div style={{ display: 'flex', flexDirection: 'column', gap: 14 }}>
              {practiceAttempts.map((att) => {
                const pct = att.self_score !== null && att.max_score
                  ? Math.round((Number(att.self_score) / Number(att.max_score)) * 100)
                  : null
                const mins = Math.floor(att.duration_seconds / 60)

                return (
                  <div
                    key={att.id}
                    style={{
                      backgroundColor: 'var(--surface)',
                      borderRadius: '12px',
                      border: '1px solid var(--color-border)',
                      padding: '18px 22px',
                      display: 'flex',
                      justifyContent: 'space-between',
                      alignItems: 'center',
                      flexWrap: 'wrap',
                      gap: 14,
                      boxShadow: 'var(--shadow-sm)'
                    }}
                  >
                    <div style={{ flex: 1, minWidth: 260 }}>
                      <div style={{ display: 'flex', alignItems: 'center', gap: 8, marginBottom: 4 }}>
                        <span style={{ fontSize: '0.75rem', fontWeight: 700, color: '#2563EB', backgroundColor: '#eff6ff', padding: '2px 8px', borderRadius: '4px' }}>
                          {att.exam_name} · {att.year}
                        </span>
                        <span style={{ fontSize: '0.72rem', color: 'var(--text-muted)' }}>
                          {new Date(att.completed_at).toLocaleDateString()} at {new Date(att.completed_at).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                        </span>
                      </div>
                      <div style={{ fontWeight: 700, fontSize: '0.95rem', color: 'var(--text-primary)', marginBottom: 6 }}>
                        {att.paper_title}
                      </div>
                      {att.notes && (
                        <p style={{ margin: 0, fontSize: '0.78125rem', color: 'var(--text-secondary)', fontStyle: 'italic' }}>
                          "{att.notes.length > 100 ? `${att.notes.slice(0, 100)}…` : att.notes}"
                        </p>
                      )}
                    </div>

                    <div style={{ display: 'flex', alignItems: 'center', gap: 16 }}>
                      <div style={{ textAlign: 'right' }}>
                        <div style={{ fontSize: '1.1rem', fontWeight: 700, color: pct >= 75 ? '#10B981' : pct >= 50 ? '#F59E0B' : '#EF4444' }}>
                          {att.self_score !== null ? `${att.self_score} / ${att.max_score}` : 'Timed Drill'}
                          {pct !== null && <span style={{ fontSize: '0.8rem', marginLeft: 4 }}>({pct}%)</span>}
                        </div>
                        <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>
                          ⏱️ Time taken: {mins} mins
                        </div>
                      </div>

                      <Link
                        to={`/paper/${att.paper_id}`}
                        className="btn btn-ghost btn-sm"
                        style={{ fontWeight: 600 }}
                      >
                        Open Paper →
                      </Link>
                    </div>
                  </div>
                )
              })}
            </div>
          )
        )}

        {/* ── TAB 3: REVISION NOTES ── */}
        {!loading && activeTab === 'notes' && (
          userNotes.length === 0 ? (
            <div className="empty-state">
              <div className="empty-state-icon">📝</div>
              <h3>No revision notes saved yet</h3>
              <p>Click "Add Notes" on any question paper to write down formulas, tricky questions, or reminders.</p>
              <Link to="/" className="btn btn-primary">Browse Papers</Link>
            </div>
          ) : (
            <div style={{ display: 'flex', flexDirection: 'column', gap: 14 }}>
              {userNotes.map((note) => (
                <div
                  key={note.id}
                  style={{
                    backgroundColor: '#fffbeb',
                    borderRadius: '12px',
                    border: '1px solid #fde68a',
                    padding: '18px 22px',
                    display: 'flex',
                    flexDirection: 'column',
                    gap: 10
                  }}
                >
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: 8 }}>
                    <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
                      <span style={{ fontSize: '0.75rem', fontWeight: 700, color: '#b45309', backgroundColor: '#fef3c7', padding: '2px 8px', borderRadius: '4px' }}>
                        {note.exam_name} · {note.year}
                      </span>
                      <span style={{ fontWeight: 700, fontSize: '0.9375rem', color: '#92400e' }}>
                        {note.paper_title}
                      </span>
                    </div>
                    <Link
                      to={`/paper/${note.paper_id}`}
                      style={{ fontSize: '0.78125rem', color: '#b45309', fontWeight: 600, textDecoration: 'none' }}
                    >
                      Open Paper & Edit Note →
                    </Link>
                  </div>
                  <div style={{
                    fontSize: '0.875rem',
                    color: '#78350f',
                    lineHeight: 1.6,
                    whiteSpace: 'pre-wrap',
                    backgroundColor: '#ffffff',
                    padding: '12px 14px',
                    borderRadius: '8px',
                    border: '1px solid #fef08a'
                  }}>
                    {note.note_text}
                  </div>
                  <div style={{ fontSize: '0.72rem', color: '#b45309', textAlign: 'right' }}>
                    Updated: {new Date(note.updated_at).toLocaleDateString()} {new Date(note.updated_at).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                  </div>
                </div>
              ))}
            </div>
          )
        )}

        {/* ── TAB 4: EXAM READINESS & SYLLABUS TRACKER ── */}
        {!loading && activeTab === 'readiness' && (
          <div style={{ display: 'flex', flexDirection: 'column', gap: 20 }}>
            {/* Exam and Subject Filter Bar */}
            <div style={{
              display: 'flex',
              justifyContent: 'space-between',
              alignItems: 'center',
              flexWrap: 'wrap',
              gap: 12,
              backgroundColor: 'var(--surface)',
              padding: '16px 20px',
              borderRadius: '12px',
              border: '1px solid var(--color-border)'
            }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: 10, flexWrap: 'wrap' }}>
                <span style={{ fontWeight: 600, fontSize: '0.875rem', color: 'var(--text-muted)' }}>Target Exam:</span>
                {[
                  { slug: 'class-10', label: '📘 Class 10 Board' },
                  { slug: 'class-12', label: '🎓 Class 12 Board' },
                  { slug: 'jee',      label: '⚗️ JEE Main' },
                  { slug: 'neet',     label: '🩺 NEET UG' },
                ].map(ex => (
                  <button
                    key={ex.slug}
                    className={`btn btn-sm ${selectedExamSyllabus === ex.slug ? 'btn-primary' : 'btn-ghost'}`}
                    style={{ fontSize: '0.8125rem' }}
                    onClick={() => {
                      setSelectedExamSyllabus(ex.slug)
                      setSelectedSubjectIndex(0)
                    }}
                  >
                    {ex.label}
                  </button>
                ))}
              </div>

              {/* Subject selector */}
              {examSubjects.length > 1 && (
                <div style={{ display: 'flex', alignItems: 'center', gap: 6 }}>
                  <span style={{ fontSize: '0.8125rem', color: 'var(--text-muted)' }}>Subject:</span>
                  {examSubjects.map((s, idx) => (
                    <button
                      key={s.subject}
                      className={`btn btn-xs ${selectedSubjectIndex === idx ? 'btn-primary' : 'btn-ghost'}`}
                      style={{
                        padding: '4px 10px',
                        fontSize: '0.75rem',
                        backgroundColor: selectedSubjectIndex === idx ? '#6366F1' : 'transparent',
                        borderColor: '#6366F1',
                        color: selectedSubjectIndex === idx ? '#fff' : '#6366F1'
                      }}
                      onClick={() => setSelectedSubjectIndex(idx)}
                    >
                      {s.subject}
                    </button>
                  ))}
                </div>
              )}
            </div>

            {/* Readiness Progress Bar Card */}
            {currentSubjectObj && (
              <div style={{
                backgroundColor: 'var(--surface)',
                padding: '24px',
                borderRadius: '16px',
                border: '1px solid var(--color-border)',
                boxShadow: 'var(--shadow-sm)'
              }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 12 }}>
                  <div>
                    <span style={{ fontSize: '0.75rem', fontWeight: 700, color: '#6366F1', textTransform: 'uppercase', letterSpacing: '0.05em' }}>
                      Syllabus Mastery Index
                    </span>
                    <h3 style={{ margin: 0, fontSize: '1.2rem', color: 'var(--text-primary)' }}>
                      {currentSubjectObj.subject} — {completedInSubject} of {allTopicsInCurrentSubject.length} Topics Mastered
                    </h3>
                  </div>
                  <div style={{ fontSize: '1.5rem', fontWeight: 700, color: subjectReadinessPct >= 75 ? '#10B981' : '#6366F1' }}>
                    {subjectReadinessPct}%
                  </div>
                </div>

                {/* Progress bar container */}
                <div style={{
                  width: '100%',
                  height: '10px',
                  backgroundColor: '#e2e8f0',
                  borderRadius: '10px',
                  overflow: 'hidden',
                  marginBottom: 16
                }}>
                  <div style={{
                    width: `${subjectReadinessPct}%`,
                    height: '100%',
                    backgroundColor: subjectReadinessPct >= 75 ? '#10B981' : '#6366F1',
                    borderRadius: '10px',
                    transition: 'width 0.4s ease'
                  }} />
                </div>

                <div style={{ display: 'flex', gap: 12, fontSize: '0.78125rem', color: 'var(--text-muted)' }}>
                  <span>✓ Check off topics as you revise them.</span>
                  <span>· Click "🔍 Papers" to find previous questions testing that concept.</span>
                </div>
              </div>
            )}

            {/* Units & Topics Checklist */}
            {currentSubjectObj && (
              <div style={{ display: 'flex', flexDirection: 'column', gap: 16 }}>
                {currentSubjectObj.units.map((unit, uIdx) => {
                  const unitCompleted = unit.topics.filter(t => completedTopics.has(t)).length
                  const unitPct = Math.round((unitCompleted / unit.topics.length) * 100)

                  return (
                    <div
                      key={uIdx}
                      style={{
                        backgroundColor: 'var(--surface)',
                        borderRadius: '14px',
                        border: '1px solid var(--color-border)',
                        padding: '20px 24px',
                        boxShadow: 'var(--shadow-sm)'
                      }}
                    >
                      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 14 }}>
                        <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
                          <span style={{ fontSize: '1.1rem' }}>📖</span>
                          <span style={{ fontWeight: 700, fontSize: '1rem', color: 'var(--text-primary)' }}>
                            {unit.name}
                          </span>
                        </div>
                        <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
                          <span style={{
                            fontSize: '0.72rem',
                            fontWeight: 700,
                            padding: '2px 8px',
                            borderRadius: '4px',
                            backgroundColor: '#eff6ff',
                            color: '#2563EB',
                            border: '1px solid #bfdbfe'
                          }}>
                            {unit.marks} Marks Weightage
                          </span>
                          <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>
                            {unitCompleted}/{unit.topics.length} Done ({unitPct}%)
                          </span>
                        </div>
                      </div>

                      <div style={{ display: 'flex', flexDirection: 'column', gap: 10 }}>
                        {unit.topics.map((topic, tIdx) => {
                          const isDone = completedTopics.has(topic)
                          return (
                            <div
                              key={tIdx}
                              style={{
                                display: 'flex',
                                alignItems: 'center',
                                justifyContent: 'space-between',
                                padding: '10px 14px',
                                borderRadius: '8px',
                                backgroundColor: isDone ? 'rgba(16, 185, 129, 0.06)' : 'rgba(0,0,0,0.015)',
                                border: `1px solid ${isDone ? 'rgba(16, 185, 129, 0.3)' : 'var(--color-border)'}`,
                                transition: 'all 0.15s ease'
                              }}
                            >
                              <label style={{ display: 'flex', alignItems: 'center', gap: 12, cursor: 'pointer', flex: 1, margin: 0 }}>
                                <input
                                  type="checkbox"
                                  checked={isDone}
                                  onChange={() => handleToggleTopic(topic, currentSubjectObj.subject)}
                                  style={{ width: '18px', height: '18px', accentColor: '#10B981', cursor: 'pointer' }}
                                />
                                <span style={{
                                  fontSize: '0.875rem',
                                  fontWeight: isDone ? 600 : 500,
                                  color: isDone ? '#065f46' : 'var(--text-primary)',
                                  textDecoration: isDone ? 'line-through' : 'none'
                                }}>
                                  {topic}
                                </span>
                              </label>

                              <Link
                                to={`/search?subject=${encodeURIComponent(currentSubjectObj.subject)}&q=${encodeURIComponent(topic)}`}
                                className="btn btn-ghost btn-sm"
                                style={{ fontSize: '0.72rem', padding: '3px 8px', height: 'auto', textDecoration: 'none' }}
                                title={`Find past papers testing ${topic}`}
                              >
                                🔍 Past Papers →
                              </Link>
                            </div>
                          )
                        })}
                      </div>
                    </div>
                  )
                })}
              </div>
            )}
          </div>
        )}

      </div>
    </div>
  )
}
