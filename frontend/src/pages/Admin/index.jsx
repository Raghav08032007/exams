import { useState, useEffect, useCallback, useMemo } from 'react'
import { useNavigate, Link } from 'react-router-dom'
import { useAuthStore, useToastStore } from '../../store'
import { 
  fetchAdminStats, 
  uploadPaper, 
  fetchExams, 
  fetchCategories,
  createCategory,
  fetchVerificationQueue,
  verifyPaper,
  fetchVerificationStats
} from '../../api/client'
import { useSEO } from '../../hooks/useSEO'

export default function AdminDashboard() {
  const { user } = useAuthStore()
  const { addToast } = useToastStore()
  const navigate = useNavigate()

  useSEO({ title: 'Admin Verification Queue & Dashboard — ExamVault' })

  const [activeTab, setActiveTab] = useState('queue') // 'queue', 'verified', 'rejected', 'upload'
  const [searchQuery, setSearchQuery] = useState('')
  const [vStats, setVStats] = useState([])
  const [queue, setQueue] = useState([])
  const [queueLoading, setQueueLoading] = useState(false)
  const [exams, setExams] = useState([])
  const [categories, setCategories] = useState([])
  const [loading, setLoading] = useState(true)

  // Rejection modal state
  const [rejectingPaper, setRejectingPaper] = useState(null)
  const [rejectionNote, setRejectionNote] = useState('')
  const [actionLoading, setActionLoading] = useState(false)

  // Manual Upload Form state
  const [examSlug, setExamSlug] = useState('')
  const [formData, setFormData] = useState({
    exam_category_id: '',
    title: '',
    year: new Date().getFullYear(),
    session: '',
    language: 'English',
    subjects: '',
  })
  const [pdfFile, setPdfFile] = useState(null)
  const [coverImageFile, setCoverImageFile] = useState(null)
  const [answerKeyFile, setAnswerKeyFile] = useState(null)
  const [uploading, setUploading] = useState(false)

  // New Category inline creation state
  const [showNewCatModal, setShowNewCatModal] = useState(false)
  const [newCatName, setNewCatName] = useState('')
  const [creatingCat, setCreatingCat] = useState(false)

  const handleCreateCategory = async (e) => {
    e.preventDefault()
    if (!examSlug || !newCatName.trim()) {
      addToast('Please select an Exam and enter a Category Name', 'error')
      return
    }
    setCreatingCat(true)
    try {
      const cat = await createCategory(examSlug, newCatName.trim())
      addToast(`Category '${cat.name}' created!`, 'success')
      setCategories(prev => [...prev, cat])
      setFormData(prev => ({ ...prev, exam_category_id: cat.id }))
      setNewCatName('')
      setShowNewCatModal(false)
    } catch (err) {
      addToast(err.response?.data?.error || 'Failed to create category', 'error')
    } finally {
      setCreatingCat(false)
    }
  }

  const loadDashboardData = useCallback(() => {
    if (!user || (user.role !== 'admin' && user.role !== 'verifier')) {
      setLoading(false)
      return
    }
    setLoading(true)
    Promise.all([fetchVerificationStats(), fetchExams()])
      .then(([vStatsData, examsData]) => {
        setVStats(Array.isArray(vStatsData) ? vStatsData : [])
        setExams(Array.isArray(examsData) ? examsData : [])
      })
      .catch((err) => {
        addToast('Failed to load admin verification stats', 'error')
      })
      .finally(() => setLoading(false))
  }, [user, addToast])

  useEffect(() => {
    loadDashboardData()
  }, [loadDashboardData])

  // Fetch queue items when tab changes
  const loadQueue = useCallback((status) => {
    setQueueLoading(true)
    fetchVerificationQueue(status)
      .then(res => setQueue(Array.isArray(res?.queue) ? res.queue : []))
      .catch((err) => {
        const st = err.response?.status
        if (st === 401 || st === 403 || st === 422) {
          navigate('/login')
        } else {
          addToast(`Failed to load ${status} queue`, 'error')
        }
      })
      .finally(() => setQueueLoading(false))
  }, [addToast, navigate])

  useEffect(() => {
    if (activeTab === 'queue') loadQueue('unverified')
    else if (activeTab === 'verified') loadQueue('verified')
    else if (activeTab === 'rejected') loadQueue('rejected')
  }, [activeTab, loadQueue])

  // Fetch categories when exam is selected in upload form
  useEffect(() => {
    if (!examSlug) {
      setCategories([])
      setFormData(prev => ({ ...prev, exam_category_id: '' }))
      return
    }
    fetchCategories(examSlug)
      .then(res => setCategories(Array.isArray(res) ? res : []))
      .catch(() => addToast('Failed to load categories', 'error'))
  }, [examSlug, addToast])

  const handleVerifyAction = async (paperId, action, note = '') => {
    setActionLoading(true)
    try {
      const res = await verifyPaper(paperId, action, note)
      addToast(res.message, action === 'approve' ? 'success' : 'info')
      setRejectingPaper(null)
      setRejectionNote('')
      loadQueue(activeTab === 'queue' ? 'unverified' : activeTab)
      loadDashboardData()
    } catch (err) {
      addToast(err.response?.data?.error || 'Verification update failed', 'error')
    } finally {
      setActionLoading(false)
    }
  }

  const handleUpload = async (e) => {
    e.preventDefault()
    if (!formData.exam_category_id || !formData.title || !formData.year) {
      addToast('Please fill out required fields (Exam, Category, Title, Year)', 'error')
      return
    }

    setUploading(true)
    const payload = new FormData()
    if (pdfFile) payload.append('file', pdfFile)
    payload.append('title', formData.title)
    payload.append('exam_category_id', formData.exam_category_id)
    payload.append('year', formData.year)
    if (formData.session) payload.append('session', formData.session)
    payload.append('language', formData.language)
    if (formData.subjects) payload.append('subjects', formData.subjects)
    if (coverImageFile) payload.append('cover_image', coverImageFile)
    if (answerKeyFile) payload.append('answer_key', answerKeyFile)

    try {
      await uploadPaper(payload)
      addToast('Paper uploaded and published successfully!', 'success')
      setFormData({
        exam_category_id: formData.exam_category_id,
        title: '',
        year: new Date().getFullYear(),
        session: '',
        language: 'English',
        subjects: '',
      })
      setPdfFile(null)
      setCoverImageFile(null)
      setAnswerKeyFile(null)
      if (document.getElementById('pdf-file-input')) document.getElementById('pdf-file-input').value = ''
      if (document.getElementById('cover-img-input')) document.getElementById('cover-img-input').value = ''
      if (document.getElementById('ak-file-input')) document.getElementById('ak-file-input').value = ''
      loadDashboardData()
      setActiveTab('verified')
    } catch (err) {
      addToast(err.response?.data?.error || 'Upload failed', 'error')
    } finally {
      setUploading(false)
    }
  }

  // Move useMemo to top of component body to adhere to React Rules of Hooks
  const filteredQueue = useMemo(() => {
    if (!Array.isArray(queue)) return []
    if (!searchQuery.trim()) return queue
    const q = searchQuery.toLowerCase().trim()
    return queue.filter(paper => {
      if (!paper) return false
      const titleMatch = paper.title ? String(paper.title).toLowerCase().includes(q) : false
      const examMatch  = paper.exam?.name ? String(paper.exam.name).toLowerCase().includes(q) : false
      const catMatch   = paper.category?.name ? String(paper.category.name).toLowerCase().includes(q) : false
      const yearMatch  = paper.year ? String(paper.year).includes(q) : false
      const langMatch  = paper.language ? String(paper.language).toLowerCase().includes(q) : false
      const subMatch   = Array.isArray(paper.subjects)
        ? paper.subjects.some(s => String(s).toLowerCase().includes(q))
        : paper.subjects ? String(paper.subjects).toLowerCase().includes(q) : false
      return titleMatch || examMatch || catMatch || yearMatch || langMatch || subMatch
    })
  }, [queue, searchQuery])

  if (!user || (user.role !== 'admin' && user.role !== 'verifier')) {
    return (
      <div className="page-content container" style={{ padding: '60px 20px', textAlign: 'center' }}>
        <div className="card" style={{ maxWidth: '500px', margin: '0 auto', padding: '40px 24px' }}>
          <div style={{ fontSize: '48px', marginBottom: '16px' }}>🔐</div>
          <h2 style={{ marginBottom: '12px', fontFamily: "'Fraunces', Georgia, serif" }}>Admin Access Required</h2>
          <p style={{ color: 'var(--text-secondary)', marginBottom: '24px', lineHeight: 1.6 }}>
            You need to be signed in with administrator or verifier credentials to access the Verification Queue & Dashboard.
          </p>
          <div style={{ display: 'flex', gap: '12px', justifyContent: 'center' }}>
            <Link to="/login" className="btn btn-primary">Sign In as Admin</Link>
            <Link to="/" className="btn btn-ghost">Return to Home</Link>
          </div>
        </div>
      </div>
    )
  }

  if (loading) {
    return (
      <div className="page-content container" style={{ padding: '60px 20px', textAlign: 'center' }}>
        <div className="skeleton" style={{ width: '100%', height: '240px', borderRadius: '16px', marginBottom: '24px' }} />
        <p style={{ color: 'var(--text-muted)' }}>Loading verification dashboard…</p>
      </div>
    )
  }

  const safeStats = Array.isArray(vStats) ? vStats : []
  const unverifiedTotal = safeStats.reduce((sum, s) => sum + (s.unverified || 0), 0)
  const verifiedTotal   = safeStats.reduce((sum, s) => sum + (s.verified || 0), 0)
  const rejectedTotal   = safeStats.reduce((sum, s) => sum + (s.rejected || 0), 0)

  return (
    <div className="page-content">
      <div className="container">
        
        <div className="page-header" style={{ marginBottom: 'var(--space-6)' }}>
          <div className="page-header-eyebrow">Administration & Quality Control</div>
          <h1>Verification Queue & Dashboard</h1>
          <p>Strict provenance tracking and verification queue. Only verified papers reach end users.</p>
        </div>

        {/* Progress Dashboard Cards */}
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(220px, 1fr))', gap: 'var(--space-4)', marginBottom: 'var(--space-8)' }}>
          {vStats.map(s => (
            <div key={s.exam_slug} className="card" style={{ padding: 'var(--space-4)', borderLeft: `4px solid ${s.accent_color_hex}` }}>
              <div style={{ fontSize: '1.05rem', fontWeight: 600, color: s.accent_color_hex, marginBottom: 8 }}>
                {s.exam_name}
              </div>
              <div style={{ display: 'flex', flexDirection: 'column', gap: 4, fontSize: '0.875rem' }}>
                <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                  <span>Verified (Public):</span>
                  <span className="mono" style={{ fontWeight: 700, color: '#10B981' }}>{s.verified}</span>
                </div>
                <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                  <span>Unverified (Queue):</span>
                  <span className="mono" style={{ fontWeight: 700, color: '#F59E0B' }}>{s.unverified}</span>
                </div>
                <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                  <span>Rejected:</span>
                  <span className="mono" style={{ fontWeight: 700, color: '#EF4444' }}>{s.rejected}</span>
                </div>
              </div>
            </div>
          ))}
        </div>

        {/* Tab Navigation */}
        <div style={{ display: 'flex', gap: 'var(--space-3)', borderBottom: '1px solid var(--border)', marginBottom: 'var(--space-6)', flexWrap: 'wrap' }}>
          <button 
            className={`btn ${activeTab === 'queue' ? 'btn-primary' : 'btn-ghost'}`}
            onClick={() => setActiveTab('queue')}
          >
            ⏳ Unverified Queue ({unverifiedTotal})
          </button>
          <button 
            className={`btn ${activeTab === 'verified' ? 'btn-primary' : 'btn-ghost'}`}
            onClick={() => setActiveTab('verified')}
          >
            ✓ Verified Papers ({verifiedTotal})
          </button>
          <button 
            className={`btn ${activeTab === 'rejected' ? 'btn-primary' : 'btn-ghost'}`}
            onClick={() => setActiveTab('rejected')}
          >
            ✗ Rejected Papers ({rejectedTotal})
          </button>
          <button 
            className={`btn ${activeTab === 'upload' ? 'btn-primary' : 'btn-ghost'}`}
            onClick={() => setActiveTab('upload')}
          >
            + Upload Paper
          </button>
        </div>

        {/* Search Bar & Button on Dashboard */}
        {activeTab !== 'upload' && (
          <div style={{ marginBottom: 'var(--space-6)' }}>
            <form
              onSubmit={(e) => e.preventDefault()}
              style={{
                display: 'flex',
                gap: 'var(--space-3)',
                maxWidth: '640px',
                alignItems: 'center',
              }}
            >
              <div style={{ flex: 1, position: 'relative' }}>
                <input
                  type="text"
                  className="form-input"
                  placeholder="Search papers by title, exam, category, or year…"
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  style={{ width: '100%', paddingRight: searchQuery ? '36px' : '14px' }}
                />
                {searchQuery && (
                  <button
                    type="button"
                    onClick={() => setSearchQuery('')}
                    style={{
                      position: 'absolute',
                      right: '12px',
                      top: '50%',
                      transform: 'translateY(-50%)',
                      background: 'none',
                      border: 'none',
                      cursor: 'pointer',
                      fontSize: '14px',
                      color: 'var(--text-muted)',
                    }}
                  >
                    ✕
                  </button>
                )}
              </div>

              <button
                type="submit"
                className="btn btn-primary"
                onClick={(e) => e.preventDefault()}
              >
                🔍 Search
              </button>
            </form>
            {searchQuery && (
              <div style={{ fontSize: '0.8125rem', color: 'var(--text-muted)', marginTop: '6px' }}>
                Showing {filteredQueue.length} matching paper{filteredQueue.length === 1 ? '' : 's'} for "{searchQuery}"
              </div>
            )}
          </div>
        )}

        {/* Tab Content: Queue / Verified / Rejected */}
        {activeTab !== 'upload' && (
          <div>
            {queueLoading ? (
              <div style={{ padding: '40px 0', textAlign: 'center', color: 'var(--text-muted)' }}>Loading paper list...</div>
            ) : filteredQueue.length === 0 ? (
              <div className="card" style={{ padding: '40px 20px', textAlign: 'center' }}>
                <h3>{searchQuery ? `No matching ${activeTab} papers` : `No ${activeTab} papers found`}</h3>
                <p style={{ color: 'var(--text-muted)' }}>
                  {searchQuery ? `Try clearing your search query "${searchQuery}"` : 'All papers in this status category are processed.'}
                </p>
              </div>
            ) : (
              <div style={{ display: 'flex', flexDirection: 'column', gap: 'var(--space-6)' }}>
                {filteredQueue.map(paper => (
                  <div key={paper.id} className="card" style={{ padding: 'var(--space-6)', background: 'var(--color-bg-raised)' }}>
                    
                    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', flexWrap: 'wrap', gap: 12, marginBottom: 12 }}>
                      <div>
                        <div style={{ display: 'flex', gap: 8, alignItems: 'center', flexWrap: 'wrap', marginBottom: 6 }}>
                          <span className="mono" style={{ fontWeight: 700, color: 'var(--accent-color)' }}>
                            {paper.exam?.name || 'EXAM'} ({paper.year})
                          </span>
                          <span className="badge badge-language">{paper.category?.name}</span>
                          
                          {/* Source Type Badge */}
                          {paper.source_type === 'official' ? (
                            <span style={{ background: '#10B981', color: '#FFF', padding: '2px 8px', borderRadius: 4, fontSize: '0.75rem', fontWeight: 700 }}>
                              OFFICIAL SOURCE
                            </span>
                          ) : (
                            <span style={{ background: '#F59E0B', color: '#FFF', padding: '2px 8px', borderRadius: 4, fontSize: '0.75rem', fontWeight: 700 }}>
                              AGGREGATOR SOURCE (REQUIRES REVIEW)
                            </span>
                          )}

                          <span style={{ fontSize: '0.8125rem', color: 'var(--text-muted)' }}>
                            Status: <strong>{paper.verification_status}</strong>
                          </span>
                        </div>

                        <h3 style={{ fontSize: '1.25rem', marginBottom: 6 }}>{paper.title}</h3>
                        
                        <div style={{ fontSize: '0.875rem', color: 'var(--text-secondary)' }}>
                          Uploaded by: <strong>{paper.uploaded_by ? `User #${paper.uploaded_by}` : 'Unknown'}</strong>
                        </div>
                      </div>

                      {/* Action Buttons */}
                      <div style={{ display: 'flex', gap: 8 }}>
                        {paper.verification_status !== 'verified' && (
                          <button 
                            className="btn btn-primary"
                            style={{ background: '#10B981', borderColor: '#10B981' }}
                            onClick={() => handleVerifyAction(paper.id, 'approve')}
                            disabled={actionLoading}
                          >
                            ✓ Approve & Publish
                          </button>
                        )}
                        {paper.verification_status !== 'rejected' && (
                          <button 
                            className="btn btn-ghost"
                            style={{ color: '#EF4444', borderColor: '#EF4444' }}
                            onClick={() => setRejectingPaper(paper)}
                            disabled={actionLoading}
                          >
                            ✗ Reject
                          </button>
                        )}
                      </div>
                    </div>

                    {/* Rejection Note display */}
                    {paper.rejection_note && (
                      <div style={{ background: 'rgba(239, 68, 68, 0.1)', border: '1px solid rgba(239, 68, 68, 0.3)', padding: '8px 12px', borderRadius: 6, marginBottom: 12, fontSize: '0.875rem', color: '#EF4444' }}>
                        Rejection Note: {paper.rejection_note}
                      </div>
                    )}

                    {/* PDF Link */}
                    <div style={{ background: 'var(--color-bg-raised)', padding: 12, borderRadius: 8, marginTop: 12, display: 'flex', alignItems: 'center', gap: 12 }}>
                      <span style={{ fontSize: '0.8125rem', fontWeight: 600, color: 'var(--text-secondary)' }}>PDF:</span>
                      {paper.pdf_url ? (
                        <a href={paper.pdf_url} target="_blank" rel="noopener noreferrer" style={{ color: 'var(--color-upsc)', fontSize: '0.875rem' }}>
                          📄 Open PDF →
                        </a>
                      ) : (
                        <span style={{ color: 'var(--text-muted)', fontSize: '0.875rem' }}>No PDF uploaded</span>
                      )}
                      {paper.session && (
                        <span className="badge badge-language" style={{ marginLeft: 'auto' }}>{paper.session}</span>
                      )}
                    </div>

                  </div>
                ))}
              </div>
            )}
          </div>
        )}

        {/* Tab Content: Manual Upload */}
        {activeTab === 'upload' && (
          <div className="card" style={{ maxWidth: 650, padding: 'var(--space-6)', background: 'var(--color-bg-raised)' }}>
            <h2 style={{ fontSize: '1.25rem', marginBottom: 'var(--space-5)' }}>Upload Question Paper</h2>
            <form onSubmit={handleUpload} style={{ display: 'flex', flexDirection: 'column', gap: 'var(--space-4)' }}>
              
              <div className="form-group">
                <label className="form-label">Exam</label>
                <select className="form-input" value={examSlug} onChange={e => setExamSlug(e.target.value)} required>
                  <option value="">-- Select Exam --</option>
                  {exams.map(ex => <option key={ex.id} value={ex.slug}>{ex.name}</option>)}
                </select>
              </div>

              <div className="form-group">
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                  <label className="form-label">Category</label>
                  {examSlug && (
                    <button
                      type="button"
                      className="btn btn-ghost btn-sm"
                      style={{ padding: '2px 8px', fontSize: '0.75rem', color: 'var(--color-upsc)' }}
                      onClick={() => setShowNewCatModal(!showNewCatModal)}
                    >
                      + Add New Category
                    </button>
                  )}
                </div>
                
                <select 
                  className="form-input" 
                  value={formData.exam_category_id} 
                  onChange={e => setFormData({ ...formData, exam_category_id: e.target.value })}
                  required
                  disabled={!examSlug}
                >
                  <option value="">
                    {!examSlug 
                      ? '-- Select Exam First --' 
                      : categories.length === 0 
                        ? '-- No Categories Found (Click + Add New) --' 
                        : '-- Select Category --'}
                  </option>
                  {categories.map(c => <option key={c.id} value={c.id}>{c.name}</option>)}
                </select>
                
                {/* Inline New Category Creator */}
                {showNewCatModal && (
                  <div style={{ background: 'var(--color-bg-card)', border: '1px solid var(--color-border)', borderRadius: 'var(--radius-md)', padding: 12, marginTop: 8 }}>
                    <div style={{ fontSize: '0.8125rem', fontWeight: 600, marginBottom: 6 }}>
                      Create New Category for {examSlug.toUpperCase()}
                    </div>
                    <div style={{ display: 'flex', gap: 8 }}>
                      <input
                        type="text"
                        className="form-input"
                        placeholder="e.g. Group 3 or Paper 2"
                        value={newCatName}
                        onChange={e => setNewCatName(e.target.value)}
                        autoFocus
                      />
                      <button
                        type="button"
                        className="btn btn-primary btn-sm"
                        onClick={handleCreateCategory}
                        disabled={creatingCat || !newCatName.trim()}
                      >
                        {creatingCat ? 'Saving...' : 'Add'}
                      </button>
                      <button
                        type="button"
                        className="btn btn-ghost btn-sm"
                        onClick={() => setShowNewCatModal(false)}
                      >
                        Cancel
                      </button>
                    </div>
                  </div>
                )}
              </div>

              <div className="form-group">
                <label className="form-label">Paper Title</label>
                <input 
                  type="text" 
                  className="form-input" 
                  placeholder="e.g. Group IV General Studies"
                  value={formData.title}
                  onChange={e => setFormData({ ...formData, title: e.target.value })}
                  required 
                />
              </div>

              <div style={{ display: 'flex', gap: 'var(--space-4)', flexWrap: 'wrap' }}>
                <div className="form-group" style={{ flex: 1, minWidth: 120 }}>
                  <label className="form-label">Year</label>
                  <input 
                    type="number" 
                    className="form-input" 
                    value={formData.year}
                    onChange={e => setFormData({ ...formData, year: parseInt(e.target.value) })}
                    required 
                  />
                </div>
                <div className="form-group" style={{ flex: 2, minWidth: 200 }}>
                  <label className="form-label">Session <span style={{ color: 'var(--text-muted)', fontWeight: 400 }}>(optional, for JEE)</span></label>
                  <input 
                    type="text" 
                    className="form-input" 
                    placeholder="e.g. January Session 1"
                    value={formData.session}
                    onChange={e => setFormData({ ...formData, session: e.target.value })}
                  />
                </div>
                <div className="form-group" style={{ flex: 1, minWidth: 120 }}>
                  <label className="form-label">Language</label>
                  <input 
                    type="text" 
                    className="form-input" 
                    value={formData.language}
                    onChange={e => setFormData({ ...formData, language: e.target.value })}
                  />
                </div>
              </div>

              <div className="form-group">
                <label className="form-label">Subjects (comma-separated)</label>
                <input 
                  type="text" 
                  className="form-input" 
                  placeholder="Physics, Chemistry, Math"
                  value={formData.subjects}
                  onChange={e => setFormData({ ...formData, subjects: e.target.value })}
                />
              </div>

              <div className="form-group">
                <label className="form-label">
                  Question Paper PDF <span style={{ color: 'var(--text-muted)', fontWeight: 400 }}>(optional)</span>
                </label>
                <input 
                  id="pdf-file-input"
                  type="file" 
                  accept="application/pdf"
                  className="form-input" 
                  onChange={e => setPdfFile(e.target.files[0] || null)}
                />
              </div>

              <div className="form-group">
                <label className="form-label">
                  Cover Image <span style={{ color: 'var(--text-muted)', fontWeight: 400 }}>(optional photo / cover page)</span>
                </label>
                <input 
                  id="cover-img-input"
                  type="file" 
                  accept="image/png, image/jpeg, image/webp"
                  className="form-input" 
                  onChange={e => setCoverImageFile(e.target.files[0] || null)}
                />
              </div>

              <div className="form-group">
                <label className="form-label">Answer Key PDF (optional)</label>
                <input 
                  id="ak-file-input"
                  type="file" 
                  accept="application/pdf"
                  className="form-input" 
                  onChange={e => setAnswerKeyFile(e.target.files[0])}
                />
              </div>

              <button type="submit" className="btn btn-primary" disabled={uploading}>
                {uploading ? 'Uploading...' : 'Upload Paper'}
              </button>
            </form>
          </div>
        )}

        {/* Rejection Modal */}
        {rejectingPaper && (
          <div style={{ position: 'fixed', inset: 0, background: 'rgba(0,0,0,0.6)', display: 'flex', alignItems: 'center', justifyContent: 'center', zIndex: 9999 }}>
            <div className="card" style={{ width: 450, padding: 24, background: 'var(--color-bg-raised)' }}>
              <h3 style={{ marginBottom: 12 }}>Reject Paper: {rejectingPaper.title}</h3>
              <p style={{ fontSize: '0.875rem', color: 'var(--text-secondary)', marginBottom: 16 }}>
                Please provide an optional note explaining why this paper is rejected (e.g. wrong year, missing pages, corrupted PDF).
              </p>
              
              <textarea 
                className="form-input"
                style={{ width: '100%', height: 100, marginBottom: 20 }}
                placeholder="Reason for rejection..."
                value={rejectionNote}
                onChange={e => setRejectionNote(e.target.value)}
              />

              <div style={{ display: 'flex', justifyContent: 'flex-end', gap: 12 }}>
                <button className="btn btn-ghost" onClick={() => setRejectingPaper(null)}>Cancel</button>
                <button 
                  className="btn btn-primary" 
                  style={{ background: '#EF4444', borderColor: '#EF4444' }}
                  onClick={() => handleVerifyAction(rejectingPaper.id, 'reject', rejectionNote)}
                  disabled={actionLoading}
                >
                  Confirm Rejection
                </button>
              </div>
            </div>
          </div>
        )}

      </div>
    </div>
  )
}
