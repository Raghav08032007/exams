/**
 * Axios API client — all requests go through this instance.
 * Base URL reads from VITE_API_URL env var, falls back to /api proxy.
 */
import axios from 'axios'

const BASE_URL = import.meta.env.VITE_API_URL || '/api'

const api = axios.create({
  baseURL: BASE_URL,
  timeout: 15000,
  headers: { 'Content-Type': 'application/json' },
})

// Attach JWT token from localStorage on every request
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('examvault_token')
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

// Handle 401 & 422 auth errors globally — clear token and redirect to login
api.interceptors.response.use(
  (response) => response,
  (error) => {
    const status = error.response?.status
    if (status === 401 || status === 422) {
      localStorage.removeItem('examvault_token')
      localStorage.removeItem('examvault_user')
      if (window.location.pathname.startsWith('/admin')) {
        window.location.href = '/login'
      }
    }
    return Promise.reject(error)
  }
)

// ── Exams ──────────────────────────────────────────────────────────────────
export const fetchExams = () =>
  api.get('/exams/').then(r => r.data.exams)

export const fetchExam = (slug) =>
  api.get(`/exams/${slug}`).then(r => r.data.exam)

export const fetchCategories = (slug) =>
  api.get(`/exams/${slug}/categories`).then(r => r.data.categories)

export const createCategory = (examSlug, name) =>
  api.post('/admin/categories', { exam_slug: examSlug, name }).then(r => r.data.category)

/**
 * Fetch distinct {year, session} pairs for a given exam category.
 * Used by the Category page to render year+session cards.
 * Returns: [{ year: 2024, session: null }, { year: 2024, session: "January Session 1" }, ...]
 */
export const fetchYearSessions = (slug, categorySlug) =>
  api.get(`/exams/${slug}/categories/${categorySlug}/year-sessions`)
    .then(r => r.data.year_sessions)

/**
 * Legacy: fetch distinct years for an exam (used by Search page).
 */
export const fetchYears = (slug, category = '') =>
  api.get(`/exams/${slug}/years`, { params: category ? { category } : {} })
    .then(r => r.data.years)

// ── Papers ─────────────────────────────────────────────────────────────────
export const fetchPapers = (params = {}) =>
  api.get('/papers/', { params }).then(r => r.data)

export const fetchSubjects = (params = {}) =>
  api.get('/papers/subjects', { params }).then(r => r.data.subjects)

export const fetchPaper = (id) =>
  api.get(`/papers/${id}`).then(r => r.data.paper)

export const downloadPaper = (id) =>
  api.get(`/papers/${id}/download`).then(r => r.data)

// ── Textbooks ──────────────────────────────────────────────────────────────
export const fetchTextbooks = (params = {}) =>
  api.get('/textbooks/', { params }).then(r => r.data)

export const fetchTextbookStandards = () =>
  api.get('/textbooks/standards').then(r => r.data)

export const fetchTextbook = (id) =>
  api.get(`/textbooks/${id}`).then(r => r.data.textbook)

// ── Auth ────────────────────────────────────────────────────────────────────
export const register = (data) => api.post('/auth/register', data).then(r => r.data)
export const login = (data) => api.post('/auth/login', data).then(r => r.data)
export const googleLogin = (data) => api.post('/auth/google', data).then(r => r.data)
export const getMe = () => api.get('/auth/me').then(r => r.data.user)

// ── Bookmarks ───────────────────────────────────────────────────────────────
export const fetchBookmarks = () =>
  api.get('/bookmarks/').then(r => r.data.bookmarks)
export const addBookmark = (paper_id) =>
  api.post('/bookmarks/', { paper_id }).then(r => r.data)
export const removeBookmark = (paper_id) =>
  api.delete(`/bookmarks/paper/${paper_id}`).then(r => r.data)

// ── Admin ────────────────────────────────────────────────────────────────────
export const fetchAdminStats = () =>
  api.get('/admin/stats').then(r => r.data.stats)

export const uploadPaper = (formData) =>
  api.post('/admin/papers', formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
  }).then(r => r.data)

export const fetchVerificationQueue = (status = 'unverified') =>
  api.get('/admin/verification-queue', { params: { status } }).then(r => r.data)

export const verifyPaper = (paperId, action, rejectionNote = '') =>
  api.post(`/admin/papers/${paperId}/verify`, {
    action,
    rejection_note: rejectionNote,
  }).then(r => r.data)

export const fetchVerificationStats = () =>
  api.get('/admin/verification-stats').then(r => r.data.verification_stats)

// ── Notifications ────────────────────────────────────────────────────────────
export const fetchNotifications = () =>
  api.get('/notifications/').then(r => r.data)
export const markNotificationRead = (notifId) =>
  api.post(`/notifications/${notifId}/read`).then(r => r.data)

// ── Open Source Provenance & References ─────────────────────────────────────
export const fetchSources = () =>
  api.get('/sources/').then(r => r.data)

// ── Study Pack Bundle & PDF Proxy ─────────────────────────────────────────
export const getStudyPackUrl = (paperId) =>
  `${api.defaults.baseURL || ''}/papers/${paperId}/bundle`

export const getProxyPdfUrl = (url) => {
  if (!url) return ''
  return `${api.defaults.baseURL || ''}/papers/proxy-pdf?url=${encodeURIComponent(url)}`
}

// ── Revision Notes ─────────────────────────────────────────────────────────
export const fetchPaperNote = (paperId) =>
  api.get(`/papers/${paperId}/notes`).then(r => r.data)
export const savePaperNote = (paperId, note) =>
  api.post(`/papers/${paperId}/notes`, { note }).then(r => r.data)
export const fetchUserAllNotes = () =>
  api.get('/papers/user/all-notes').then(r => r.data.notes || [])

// ── Exam Simulator & Practice Mode ─────────────────────────────────────────
export const fetchPracticeHistory = (paperId) =>
  api.get(`/papers/${paperId}/practice`).then(r => r.data.attempts || [])
export const recordPracticeAttempt = (paperId, attemptData) =>
  api.post(`/papers/${paperId}/practice`, attemptData).then(r => r.data)
export const fetchUserPracticeSummary = () =>
  api.get('/papers/user/practice-summary').then(r => r.data.attempts || [])

// ── Exam Readiness & Syllabus Tracker ───────────────────────────────────────
export const fetchUserSyllabusProgress = (params) =>
  api.get('/papers/user/syllabus', { params }).then(r => r.data)
export const updateUserSyllabusProgress = (data) =>
  api.post('/papers/user/syllabus', data).then(r => r.data)

// ── Gemini AI Doubt Solver & Explainer ─────────────────────────────────────
export const askGeminiDoubt = (payload) =>
  api.post('/ai/explain', payload).then(r => r.data)

// ── Chapters & Lessons Hub ─────────────────────────────────────────────────
export const fetchChapters = (params = {}) =>
  api.get('/chapters/', { params }).then(r => r.data)

export const fetchChapterDetail = (id) =>
  api.get(`/chapters/${id}`).then(r => r.data.chapter)

// ── Curriculum & GitHub Open Source Synchronizer ───────────────────────────
export const fetchCategoryCurriculum = (examSlug, categorySlug) =>
  api.get(`/curriculum/${examSlug}/${categorySlug}`).then(r => r.data)

export const fetchCurriculumOverview = () =>
  api.get('/curriculum/overview').then(r => r.data)

export const fetchGitHubStats = () =>
  api.get('/curriculum/github-stats').then(r => r.data)

export default api
