/**
 * CommandPalette — Universal Spotlight Quick Search (Ctrl + K / Cmd + K).
 * Provides lightning-fast keyboard search across papers, exams, textbooks, and subjects.
 */
import { useEffect, useState, useRef } from 'react'
import { useNavigate } from 'react-router-dom'
import { fetchPapers, fetchTextbooks } from '../../api/client'

const QUICK_LINKS = [
  { type: 'Exam', title: 'Class 10 Board Archive', subtitle: 'CBSE & State Board SSLC Papers', url: '/exam/class-10', icon: '📘' },
  { type: 'Exam', title: 'Class 12 Higher Secondary', subtitle: 'CBSE, ISC & State Board HSC Papers', url: '/exam/class-12', icon: '🎓' },
  { type: 'Exam', title: 'JEE Main & Advanced', subtitle: 'National Engineering Entrance Papers', url: '/exam/jee', icon: '⚗️' },
  { type: 'Exam', title: 'NEET UG Medical Entrance', subtitle: 'Undergraduate Medical Entrance Papers', url: '/exam/neet', icon: '🩺' },
  { type: 'Exam', title: 'UPSC Civil Services', subtitle: 'Prelims & Mains GS Papers', url: '/exam/upsc', icon: '🏛️' },
  { type: 'Exam', title: 'TNPSC State Services', subtitle: 'Group 1, 2, 4 & VAO Examinations', url: '/exam/tnpsc', icon: '📋' },
  { type: 'Library', title: 'Curriculum Textbooks (Class 1–12)', subtitle: 'NCERT & State Board Prescribed Books', url: '/textbooks', icon: '📚' },
  { type: 'Provenance', title: 'Open Source Repositories & Provenance', subtitle: 'GitHub repos, licenses & statutory portals', url: '/sources', icon: '🐙' },
  { type: 'Hub', title: 'My Study Hub & Practice Analytics', subtitle: 'Saved papers, mock test logs & notes', url: '/bookmarks', icon: '🎯' },
]

export default function CommandPalette() {
  const [isOpen, setIsOpen] = useState(false)
  const [query, setQuery] = useState('')
  const [papers, setPapers] = useState([])
  const [textbooks, setTextbooks] = useState([])
  const [selectedIndex, setSelectedIndex] = useState(0)
  const navigate = useNavigate()
  const inputRef = useRef(null)

  // Listen for Ctrl+K or Cmd+K
  useEffect(() => {
    const handleKeyDown = (e) => {
      if ((e.ctrlKey || e.metaKey) && e.key.toLowerCase() === 'k') {
        e.preventDefault()
        setIsOpen((open) => !open)
      } else if (e.key === 'Escape' && isOpen) {
        setIsOpen(false)
      }
    }
    window.addEventListener('keydown', handleKeyDown)
    return () => window.removeEventListener('keydown', handleKeyDown)
  }, [isOpen])

  // Focus input when opened
  useEffect(() => {
    if (isOpen) {
      setTimeout(() => inputRef.current?.focus(), 50)
      setQuery('')
      setSelectedIndex(0)
    }
  }, [isOpen])

  // Live search when query changes
  useEffect(() => {
    if (!query.trim() || query.length < 2) {
      setPapers([])
      setTextbooks([])
      return
    }
    const timer = setTimeout(() => {
      fetchPapers({ search: query, per_page: 5 })
        .then((res) => setPapers(res.papers || []))
        .catch(() => setPapers([]))

      fetchTextbooks({ search: query, per_page: 4 })
        .then((res) => setTextbooks(res.textbooks || []))
        .catch(() => setTextbooks([]))
    }, 250)

    return () => clearTimeout(timer)
  }, [query])

  const filteredQuickLinks = QUICK_LINKS.filter((item) =>
    item.title.toLowerCase().includes(query.toLowerCase()) ||
    item.subtitle.toLowerCase().includes(query.toLowerCase())
  )

  const allItems = [
    ...filteredQuickLinks.map(q => ({ ...q, category: 'Navigation & Exams' })),
    ...papers.map(p => ({
      type: 'Paper',
      title: p.title,
      subtitle: `${p.exam?.name || 'Exam'} · ${p.year}${p.has_answer_key ? ' · ✓ Answer Key' : ''}`,
      url: `/paper/${p.id}`,
      icon: '📑',
      category: 'Question Papers'
    })),
    ...textbooks.map(tb => ({
      type: 'Textbook',
      title: tb.title,
      subtitle: `${tb.board} · ${tb.standard_level}`,
      url: `/textbooks?search=${encodeURIComponent(tb.title)}`,
      icon: '📚',
      category: 'Textbooks'
    }))
  ]

  const handleSelect = (item) => {
    setIsOpen(false)
    navigate(item.url)
  }

  const handleKeyNavigation = (e) => {
    if (e.key === 'ArrowDown') {
      e.preventDefault()
      setSelectedIndex((idx) => (idx + 1) % Math.max(1, allItems.length))
    } else if (e.key === 'ArrowUp') {
      e.preventDefault()
      setSelectedIndex((idx) => (idx - 1 + allItems.length) % Math.max(1, allItems.length))
    } else if (e.key === 'Enter' && allItems[selectedIndex]) {
      e.preventDefault()
      handleSelect(allItems[selectedIndex])
    }
  }

  if (!isOpen) return null

  return (
    <div
      style={{
        position: 'fixed',
        top: 0,
        left: 0,
        right: 0,
        bottom: 0,
        backgroundColor: 'rgba(15, 23, 42, 0.65)',
        backdropFilter: 'blur(6px)',
        zIndex: 10000,
        display: 'flex',
        alignItems: 'flex-start',
        justifyContent: 'center',
        paddingTop: '12vh',
        paddingLeft: '16px',
        paddingRight: '16px',
      }}
      onClick={() => setIsOpen(false)}
    >
      <div
        style={{
          width: '100%',
          maxWidth: '640px',
          backgroundColor: '#ffffff',
          borderRadius: '16px',
          boxShadow: '0 20px 45px rgba(0,0,0,0.25)',
          border: '1px solid #cbd5e1',
          overflow: 'hidden',
          display: 'flex',
          flexDirection: 'column',
          maxHeight: '75vh'
        }}
        onClick={(e) => e.stopPropagation()}
      >
        {/* Search Input Bar */}
        <div style={{
          display: 'flex',
          alignItems: 'center',
          gap: 12,
          padding: '16px 20px',
          borderBottom: '1px solid #e2e8f0',
          backgroundColor: '#f8fafc'
        }}>
          <span style={{ fontSize: '1.25rem', color: '#64748b' }}>🔍</span>
          <input
            ref={inputRef}
            type="text"
            value={query}
            onChange={(e) => {
              setQuery(e.target.value)
              setSelectedIndex(0)
            }}
            onKeyDown={handleKeyNavigation}
            placeholder="Type an exam, subject, textbook, or standard (e.g. Maths, Class 10, JEE, UPSC)..."
            style={{
              flex: 1,
              border: 'none',
              outline: 'none',
              fontSize: '1rem',
              backgroundColor: 'transparent',
              color: '#0f172a',
              fontFamily: 'inherit'
            }}
          />
          <kbd style={{
            fontSize: '0.7rem',
            backgroundColor: '#e2e8f0',
            color: '#475569',
            padding: '3px 7px',
            borderRadius: '6px',
            border: '1px solid #cbd5e1',
            fontWeight: 600
          }}>
            ESC
          </kbd>
        </div>

        {/* Results List */}
        <div style={{ overflowY: 'auto', padding: '10px 0' }}>
          {allItems.length === 0 ? (
            <div style={{ padding: '36px 20px', textAlign: 'center', color: '#64748b' }}>
              <div style={{ fontSize: '2rem', marginBottom: 6 }}>🔍</div>
              <div style={{ fontWeight: 600, fontSize: '0.9375rem' }}>No results found for "{query}"</div>
              <div style={{ fontSize: '0.8125rem', marginTop: 4 }}>
                Try searching for Mathematics, Physics, Class 10, or UPSC
              </div>
            </div>
          ) : (
            allItems.map((item, idx) => {
              const isSelected = idx === selectedIndex
              return (
                <div
                  key={`${item.type}-${item.title}-${idx}`}
                  style={{
                    display: 'flex',
                    alignItems: 'center',
                    gap: 14,
                    padding: '12px 20px',
                    backgroundColor: isSelected ? 'rgba(59, 130, 246, 0.08)' : 'transparent',
                    borderLeft: `3px solid ${isSelected ? '#2563EB' : 'transparent'}`,
                    cursor: 'pointer',
                    transition: 'background-color 0.1s ease'
                  }}
                  onMouseEnter={() => setSelectedIndex(idx)}
                  onClick={() => handleSelect(item)}
                >
                  <span style={{ fontSize: '1.35rem' }}>{item.icon}</span>
                  <div style={{ flex: 1, minWidth: 0 }}>
                    <div style={{
                      fontWeight: 600,
                      fontSize: '0.875rem',
                      color: isSelected ? '#1d4ed8' : '#0f172a',
                      whiteSpace: 'nowrap',
                      overflow: 'hidden',
                      textOverflow: 'ellipsis'
                    }}>
                      {item.title}
                    </div>
                    <div style={{
                      fontSize: '0.75rem',
                      color: '#64748b',
                      whiteSpace: 'nowrap',
                      overflow: 'hidden',
                      textOverflow: 'ellipsis'
                    }}>
                      {item.subtitle}
                    </div>
                  </div>
                  <span style={{
                    fontSize: '0.6875rem',
                    fontWeight: 600,
                    color: '#64748b',
                    backgroundColor: '#f1f5f9',
                    padding: '2px 8px',
                    borderRadius: '4px',
                    border: '1px solid #e2e8f0'
                  }}>
                    {item.type}
                  </span>
                </div>
              )
            })
          )}
        </div>

        {/* Footer info bar */}
        <div style={{
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center',
          padding: '10px 18px',
          backgroundColor: '#f8fafc',
          borderTop: '1px solid #e2e8f0',
          fontSize: '0.72rem',
          color: '#64748b'
        }}>
          <div style={{ display: 'flex', gap: 12 }}>
            <span><kbd>↑</kbd> <kbd>↓</kbd> Navigate</span>
            <span><kbd>↵</kbd> Select</span>
          </div>
          <span>Quick Spotlight Palette</span>
        </div>
      </div>
    </div>
  )
}
