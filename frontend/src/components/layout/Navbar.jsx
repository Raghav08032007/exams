import { useState, useEffect, useRef } from 'react'
import { Link, NavLink, useNavigate } from 'react-router-dom'
import { useAuthStore, useToastStore } from '../../store'
import { useOnlineStatus } from '../../hooks/useOnlineStatus'
import { fetchNotifications, markNotificationRead } from '../../api/client'

const EXAM_GROUPS = [
  {
    heading: '🏫 School Education (K-12)',
    items: [
      { slug: 'class-10', label: 'CBSE Class 10 (Secondary)', desc: 'Math, Science, Social, English, Tamil' },
      { slug: 'class-12', label: 'CBSE Class 12 (Sr. Secondary)', desc: 'Maths, Physics, Chemistry, Biology, Commerce' },
      { slug: 'state-boards', label: 'State Boards Archive', desc: 'Tamil Nadu SSLC/HSC, UP, Bihar, MH, RJ' },
    ]
  },
  {
    heading: '🎯 Competitive Entrances',
    items: [
      { slug: 'jee', label: 'JEE (Main & Advanced)', desc: 'Engineering Entrance Papers & Solutions' },
      { slug: 'neet', label: 'NEET UG', desc: 'Medical Entrance Physics, Chemistry, Biology' },
    ]
  },
  {
    heading: '🏛️ Civil Services & Defence',
    items: [
      { slug: 'upsc', label: 'UPSC Civil Services', desc: 'Prelims, Mains, IFS, NDA, CDS, CAPF' },
      { slug: 'tnpsc', label: 'TNPSC Group Exams', desc: 'Group 1, 2, 4 & VAO Question Papers' },
    ]
  }
]

function NotificationBell() {
  const { user } = useAuthStore()
  const { addToast } = useToastStore()
  const navigate = useNavigate()

  const [isOpen, setIsOpen] = useState(false)
  const [notifications, setNotifications] = useState([])
  const [unreadCount, setUnreadCount] = useState(0)
  const dropdownRef = useRef(null)

  const loadNotifications = () => {
    fetchNotifications()
      .then(data => {
        setNotifications(data.notifications || [])
        setUnreadCount(data.unread_count || 0)
      })
      .catch(() => {})
  }

  // Poll for new paper notifications every 20 seconds
  useEffect(() => {
    loadNotifications()
    const interval = setInterval(loadNotifications, 20000)
    return () => clearInterval(interval)
  }, [user])

  // Close dropdown on outside click
  useEffect(() => {
    const handleClickOutside = (e) => {
      if (dropdownRef.current && !dropdownRef.current.contains(e.target)) {
        setIsOpen(false)
      }
    }
    document.addEventListener('mousedown', handleClickOutside)
    return () => document.removeEventListener('mousedown', handleClickOutside)
  }, [])

  const handleNotificationClick = async (notif) => {
    if (!user) {
      addToast('Please sign in to view paper details.', 'info')
      navigate('/login')
      return
    }

    if (!notif.is_read) {
      try {
        await markNotificationRead(notif.id)
        setUnreadCount(prev => Math.max(0, prev - 1))
        setNotifications(prev => prev.map(n => n.id === notif.id ? { ...n, is_read: true } : n))
      } catch (err) {}
    }

    setIsOpen(false)
    if (notif.paper_id) {
      navigate(`/paper/${notif.paper_id}`)
    } else if (notif.exam_slug) {
      navigate(`/exam/${notif.exam_slug}`)
    }
  }

  return (
    <div ref={dropdownRef} style={{ position: 'relative' }}>
      <button
        className="btn btn-ghost btn-sm"
        onClick={() => {
          setIsOpen(!isOpen)
          if (!isOpen) loadNotifications()
        }}
        aria-label="Notifications"
        style={{ position: 'relative', padding: '6px 12px', fontSize: '1.1rem' }}
      >
        🔔
        {unreadCount > 0 && (
          <span
            style={{
              position: 'absolute',
              top: '-2px',
              right: '-2px',
              backgroundColor: '#EF4444',
              color: '#FFFFFF',
              borderRadius: '9999px',
              padding: '2px 6px',
              fontSize: '0.65rem',
              fontWeight: 700,
              lineHeight: 1,
              boxShadow: '0 2px 4px rgba(0,0,0,0.2)',
            }}
          >
            {unreadCount}
          </span>
        )}
      </button>

      {isOpen && (
        <div
          style={{
            position: 'absolute',
            right: 0,
            top: 'calc(100% + 8px)',
            width: '340px',
            maxWidth: '90vw',
            backgroundColor: 'var(--color-bg-raised)',
            border: '1px solid var(--color-border)',
            borderRadius: '16px',
            boxShadow: 'var(--shadow-xl)',
            zIndex: 1000,
            overflow: 'hidden',
          }}
        >
          <div
            style={{
              padding: '12px 16px',
              borderBottom: '1px solid var(--color-border)',
              display: 'flex',
              justifyContent: 'space-between',
              alignItems: 'center',
              backgroundColor: 'var(--color-bg)',
            }}
          >
            <span style={{ fontWeight: 700, fontSize: '0.875rem' }}>🔔 Notifications</span>
            {unreadCount > 0 && (
              <span className="badge" style={{ backgroundColor: '#EF4444', color: '#FFF', fontSize: '0.7rem' }}>
                {unreadCount} new
              </span>
            )}
          </div>

          <div style={{ maxHeight: '360px', overflowY: 'auto' }}>
            {notifications.length === 0 ? (
              <div style={{ padding: '24px 16px', textAlign: 'center', color: 'var(--text-muted)', fontSize: '0.8125rem' }}>
                No notifications yet. New published papers will appear here!
              </div>
            ) : (
              notifications.map((n) => (
                <div
                  key={n.id}
                  onClick={() => handleNotificationClick(n)}
                  style={{
                    padding: '12px 16px',
                    borderBottom: '1px solid var(--color-border)',
                    backgroundColor: n.is_read ? 'transparent' : 'rgba(16, 185, 129, 0.06)',
                    cursor: 'pointer',
                    transition: 'background-color 0.15s ease',
                  }}
                  onMouseEnter={(e) => (e.currentTarget.style.backgroundColor = 'var(--color-bg)')}
                  onMouseLeave={(e) => (e.currentTarget.style.backgroundColor = n.is_read ? 'transparent' : 'rgba(16, 185, 129, 0.06)')}
                >
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 4 }}>
                    <span style={{ fontSize: '0.8125rem', fontWeight: 700, color: 'var(--text-primary)' }}>
                      {n.title}
                    </span>
                    {!n.is_read && (
                      <span style={{ width: 8, height: 8, borderRadius: '50%', backgroundColor: '#10B981' }} />
                    )}
                  </div>
                  <p style={{ fontSize: '0.75rem', color: 'var(--text-secondary)', margin: 0, lineHeight: 1.4 }}>
                    {n.message}
                  </p>
                </div>
              ))
            )}
          </div>
        </div>
      )}
    </div>
  )
}

export default function Navbar() {
  const { user, logout } = useAuthStore()
  const { addToast } = useToastStore()
  const navigate = useNavigate()
  const isOnline = useOnlineStatus()
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false)
  const [examsDropdownOpen, setExamsDropdownOpen] = useState(false)
  const dropdownRef = useRef(null)

  const handleLogout = () => {
    logout()
    setMobileMenuOpen(false)
    addToast('Signed out successfully', 'info')
    navigate('/login')
  }

  const closeMenu = () => {
    setMobileMenuOpen(false)
    setExamsDropdownOpen(false)
  }

  // Close exams dropdown on outside click
  useEffect(() => {
    const handleClickOutside = (e) => {
      if (dropdownRef.current && !dropdownRef.current.contains(e.target)) {
        setExamsDropdownOpen(false)
      }
    }
    document.addEventListener('mousedown', handleClickOutside)
    return () => document.removeEventListener('mousedown', handleClickOutside)
  }, [])

  const handleProtectedClick = (e, path) => {
    closeMenu()
    if (!user) {
      e.preventDefault()
      addToast('Please sign in or register to access question papers.', 'info')
      navigate('/login')
    } else if (path) {
      navigate(path)
    }
  }

  return (
    <header className="navbar">
      <div className="navbar-container">
        
        {/* Brand */}
        <Link to="/" className="navbar-brand" onClick={closeMenu}>
          <span>Exam</span>
          <span className="brand-vault">Vault</span>
          {!isOnline && (
            <span className="badge" style={{ backgroundColor: '#D4A84B', color: '#FAF7F2', fontSize: '0.65rem', marginLeft: '6px' }}>
              Offline
            </span>
          )}
        </Link>

        {/* Mobile menu toggle */}
        <button
          className="navbar-mobile-toggle"
          onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
          aria-label={mobileMenuOpen ? 'Close menu' : 'Open menu'}
          aria-expanded={mobileMenuOpen}
        >
          {mobileMenuOpen ? '✕' : '☰'}
        </button>

        {/* Clean, Grouped Navigation Bar */}
        <div className={`navbar-content ${mobileMenuOpen ? 'is-open' : ''}`}>
          <ul className="navbar-links">
            
            {/* 1. Categorized Exams Dropdown */}
            <li ref={dropdownRef} style={{ position: 'relative' }}>
              <button
                className="navbar-link"
                onClick={() => setExamsDropdownOpen(!examsDropdownOpen)}
                style={{
                  background: 'none',
                  border: 'none',
                  cursor: 'pointer',
                  display: 'flex',
                  alignItems: 'center',
                  gap: 4,
                  fontSize: '0.875rem',
                  fontWeight: 600,
                  color: examsDropdownOpen ? 'var(--color-primary)' : 'inherit'
                }}
              >
                <span>📝 All Exams & Boards</span>
                <span style={{ fontSize: '0.7rem', transition: 'transform 0.15s ease', transform: examsDropdownOpen ? 'rotate(180deg)' : 'none' }}>▼</span>
              </button>

              {examsDropdownOpen && (
                <div style={{
                  position: 'absolute',
                  top: 'calc(100% + 10px)',
                  left: 0,
                  width: '380px',
                  maxWidth: '92vw',
                  backgroundColor: '#ffffff',
                  border: '1px solid var(--color-border)',
                  borderRadius: '16px',
                  boxShadow: '0 12px 36px rgba(0,0,0,0.12)',
                  padding: '16px',
                  zIndex: 1100,
                  display: 'flex',
                  flexDirection: 'column',
                  gap: 16
                }}>
                  {EXAM_GROUPS.map((group) => (
                    <div key={group.heading}>
                      <div style={{
                        fontSize: '0.72rem',
                        fontWeight: 700,
                        color: 'var(--text-muted)',
                        textTransform: 'uppercase',
                        letterSpacing: '0.04em',
                        marginBottom: 6,
                        paddingLeft: 6
                      }}>
                        {group.heading}
                      </div>
                      <div style={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
                        {group.items.map((item) => (
                          <Link
                            key={item.slug}
                            to={`/exam/${item.slug}`}
                            onClick={(e) => handleProtectedClick(e, `/exam/${item.slug}`)}
                            style={{
                              padding: '8px 10px',
                              borderRadius: '8px',
                              textDecoration: 'none',
                              color: 'var(--text-primary)',
                              display: 'flex',
                              flexDirection: 'column',
                              transition: 'background-color 0.15s ease'
                            }}
                            onMouseEnter={(e) => (e.currentTarget.style.backgroundColor = '#F3F4F6')}
                            onMouseLeave={(e) => (e.currentTarget.style.backgroundColor = 'transparent')}
                          >
                            <span style={{ fontWeight: 600, fontSize: '0.875rem' }}>{item.label}</span>
                            <span style={{ fontSize: '0.72rem', color: 'var(--text-secondary)' }}>{item.desc}</span>
                          </Link>
                        ))}
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </li>

            {/* 2. Lessons & Chapters Hub */}
            <li>
              <NavLink
                to="/lessons"
                className={({ isActive }) => `navbar-link ${isActive ? 'active' : ''}`}
                onClick={closeMenu}
              >
                📑 Curriculum Lessons
              </NavLink>
            </li>

            {/* 3. Textbooks */}
            <li>
              <NavLink
                to="/textbooks"
                className={({ isActive }) => `navbar-link ${isActive ? 'active' : ''}`}
                onClick={closeMenu}
              >
                📚 Textbooks
              </NavLink>
            </li>

            {/* 4. Open Repositories & Sources */}
            <li>
              <NavLink
                to="/repositories"
                className={({ isActive }) => `navbar-link ${isActive ? 'active' : ''}`}
                onClick={closeMenu}
              >
                🐙 Repositories
              </NavLink>
            </li>

            {/* 5. Search Hub */}
            <li>
              <NavLink
                to="/search"
                className={({ isActive }) => `navbar-link ${isActive ? 'active' : ''}`}
                onClick={(e) => handleProtectedClick(e, '/search')}
              >
                🔍 Search
              </NavLink>
            </li>

          </ul>

          {/* User actions */}
          <div className="navbar-actions">
            {user && user.role === 'user' && <NotificationBell />}
            {user ? (
              <>
                <NavLink
                  to="/bookmarks"
                  className={({ isActive }) => `btn btn-ghost btn-sm ${isActive ? 'active' : ''}`}
                  onClick={closeMenu}
                  title="Your saved bookmarks"
                >
                  ⭐ Bookmarks
                </NavLink>

                {user.role === 'admin' && (
                  <NavLink
                    to="/admin"
                    className="btn btn-ghost btn-sm"
                    onClick={closeMenu}
                    style={{ borderColor: 'var(--color-primary)', color: 'var(--color-primary)' }}
                  >
                    🛡️ Admin
                  </NavLink>
                )}

                <button
                  className="btn btn-ghost btn-sm"
                  onClick={handleLogout}
                  style={{ color: '#EF4444' }}
                >
                  Sign Out
                </button>
              </>
            ) : (
              <div style={{ display: 'flex', gap: 8, alignItems: 'center' }}>
                <Link to="/login" className="btn btn-ghost btn-sm" onClick={closeMenu}>
                  Sign In
                </Link>
                <Link to="/register" className="btn btn-primary btn-sm" onClick={closeMenu}>
                  Register Free
                </Link>
              </div>
            )}
          </div>
        </div>

      </div>
    </header>
  )
}
