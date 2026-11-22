/**
 * App router — all routes + AnimatePresence page transitions.
 *
 * Route hierarchy (Phase 3):
 *   /                              → Home (exam cards)
 *   /exam/:slug                    → Exam page (category cards + official site card)
 *   /exam/:slug/:category          → Category page (year+session cards)
 *   /exam/:slug/:category/:year    → Year/Paper listing (flip cards, ?session= filter)
 *   /paper/:id                     → Paper detail (PDF viewer + download)
 *   /search                        → Search
 *   /login  /register              → Auth
 *   /bookmarks                     → Bookmarks
 *   /admin                         → Admin dashboard
 */
import { BrowserRouter, Routes, Route, useLocation } from 'react-router-dom'
import { AnimatePresence } from 'framer-motion'
import Navbar           from './components/layout/Navbar'
import Footer           from './components/layout/Footer'
import ToastContainer   from './components/ui/ToastContainer'
import CommandPalette   from './components/ui/CommandPalette'
import PageTransition   from './components/animations/PageTransition'

import HomePage       from './pages/Home'
import ExamPage       from './pages/Exam'
import CategoryPage   from './pages/Category'
import YearPage       from './pages/Year'
import PaperDetail    from './pages/PaperDetail'
import SearchPage     from './pages/Search'
import TextbooksPage  from './pages/Textbooks'
import LessonsPage    from './pages/Lessons'
import SourcesPage    from './pages/Sources'
import RepositoriesPage from './pages/Repositories'
import LoginPage      from './pages/Auth/Login'
import RegisterPage   from './pages/Auth/Register'
import BookmarksPage  from './pages/Bookmarks'
import AdminDashboard from './pages/Admin'

function NotFound() {
  return (
    <PageTransition>
      <div className="page-content">
        <div className="container">
          <div className="empty-state">
            <div className="empty-state-icon">🗂️</div>
            <h3>Page not found</h3>
            <p>This drawer doesn't exist in the archive.</p>
            <a href="/" className="btn btn-primary">← Back to Home</a>
          </div>
        </div>
      </div>
    </PageTransition>
  )
}

function AppContent() {
  const location = useLocation()

  return (
    <div style={{ display: 'flex', flexDirection: 'column', minHeight: '100vh' }}>
      <Navbar />

      <AnimatePresence mode="wait" initial={false}>
        <Routes location={location} key={location.pathname}>
          <Route path="/" element={
            <PageTransition><HomePage /></PageTransition>
          } />
          <Route path="/exam/:slug" element={
            <PageTransition><ExamPage /></PageTransition>
          } />
          {/* Category page: year+session listing */}
          <Route path="/exam/:slug/:category" element={
            <PageTransition><CategoryPage /></PageTransition>
          } />
          {/* Year/paper listing, optional ?session= */}
          <Route path="/exam/:slug/:category/:year" element={
            <PageTransition><YearPage /></PageTransition>
          } />
          <Route path="/paper/:id" element={
            <PageTransition><PaperDetail /></PageTransition>
          } />
          <Route path="/search" element={
            <PageTransition><SearchPage /></PageTransition>
          } />
          <Route path="/textbooks" element={
            <PageTransition><TextbooksPage /></PageTransition>
          } />
          <Route path="/lessons" element={
            <PageTransition><LessonsPage /></PageTransition>
          } />
          <Route path="/sources" element={
            <PageTransition><SourcesPage /></PageTransition>
          } />
          <Route path="/repositories" element={
            <PageTransition><RepositoriesPage /></PageTransition>
          } />
          <Route path="/github" element={
            <PageTransition><RepositoriesPage /></PageTransition>
          } />
          <Route path="/login" element={
            <PageTransition><LoginPage /></PageTransition>
          } />
          <Route path="/register" element={
            <PageTransition><RegisterPage /></PageTransition>
          } />
          <Route path="/bookmarks" element={
            <PageTransition><BookmarksPage /></PageTransition>
          } />
          <Route path="/admin" element={
            <PageTransition><AdminDashboard /></PageTransition>
          } />
          <Route path="*" element={<NotFound />} />
        </Routes>
      </AnimatePresence>

      <Footer />
      <ToastContainer />
      <CommandPalette />
    </div>
  )
}

export default function App() {
  return (
    <BrowserRouter>
      <AppContent />
    </BrowserRouter>
  )
}
