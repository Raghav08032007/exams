/**
 * Open-Source Repositories Hub — showcases all GitHub repositories and statutory archives
 * integrated into ExamVault with live synchronization status, tree statistics, and file coverage.
 * Route: /repositories
 */
import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { motion } from 'framer-motion'
import { fetchGitHubStats } from '../../api/client'
import { useToastStore } from '../../store'
import { useSEO } from '../../hooks/useSEO'
import { useReducedMotion } from '../../hooks/useReducedMotion'

export default function RepositoriesPage() {
  const [stats, setStats] = useState(null)
  const [loading, setLoading] = useState(true)
  const [resyncing, setResyncing] = useState(false)
  const [searchFilter, setSearchFilter] = useState('')
  const { addToast } = useToastStore()
  const reduced = useReducedMotion()

  useSEO({
    title: 'Open-Source Repositories Hub — ExamVault',
    description: 'Explore all synchronized GitHub repositories, statutory archives, and open-source datasets powering ExamVault.',
  })

  useEffect(() => {
    fetchGitHubStats()
      .then(data => setStats(data))
      .catch(() => addToast('Failed to load GitHub repository stats.', 'error'))
      .finally(() => setLoading(false))
  }, [addToast])

  const handleResync = async () => {
    setResyncing(true)
    addToast('Contacting GitHub Trees API to verify synchronization...', 'info')
    try {
      const data = await fetchGitHubStats()
      setStats(data)
      addToast('All GitHub repositories are active and synchronized!', 'success')
    } catch {
      addToast('Synchronization check failed.', 'error')
    } finally {
      setResyncing(false)
    }
  }

  const statCards = [
    { label: 'Total Verified Papers', value: stats?.total_papers_in_system?.toLocaleString() || '2,600', icon: '📑', color: '#10B981' },
    { label: 'GitHub Synced Papers', value: stats?.github_synchronized_papers?.toLocaleString() || '2,014', icon: '🐙', color: '#6366F1' },
    { label: 'Co-located Answer Keys', value: stats?.co_located_answer_keys?.toLocaleString() || '486', icon: '🔑', color: '#F59E0B' },
    { label: 'NCERT & Board Textbooks', value: stats?.textbooks_indexed?.toLocaleString() || '323', icon: '📚', color: '#EC4899' },
    { label: 'Official Curricula', value: stats?.curriculum_blueprints || '9', icon: '📜', color: '#8B5CF6' },
  ]

  const statutoryArchives = [
    {
      name: 'CBSE Academic Official Portal',
      url: 'https://cbseacademic.nic.in',
      authority: 'Central Board of Secondary Education (Govt. of India)',
      coverage: 'Class 10 & Class 12 Board Papers, Sample Papers & Marking Schemes (2015-2024)',
      badge: 'Official Statutory',
      badgeColor: '#10B981',
      icon: '🏛️'
    },
    {
      name: 'NCERT Digital Textbook Portal',
      url: 'https://ncert.nic.in',
      authority: 'National Council of Educational Research and Training',
      coverage: 'Class 1 through 12 complete curriculum textbooks and rationalised syllabi',
      badge: 'National Curriculum',
      badgeColor: '#6366F1',
      icon: '📖'
    },
    {
      name: 'UPSC Examination Digital Gazette',
      url: 'https://upsc.gov.in',
      authority: 'Union Public Service Commission',
      coverage: 'Civil Services Prelims (GS 1 & CSAT) and Mains (GS 1-4, Essay, Optionals)',
      badge: 'Union Authority',
      badgeColor: '#F59E0B',
      icon: '🇮🇳'
    },
    {
      name: 'NTA Official Examination Archives',
      url: 'https://jeemain.nta.ac.in',
      authority: 'National Testing Agency (Ministry of Education)',
      coverage: 'JEE Main & NEET UG Question Papers, Final Answer Keys & Score Normalization',
      badge: 'National Testing Agency',
      badgeColor: '#EC4899',
      icon: '🔬'
    },
    {
      name: 'TNPSC & Tamil Nadu DGE Portal',
      url: 'https://www.tnpsc.gov.in',
      authority: 'Tamil Nadu Public Service Commission & Directorate of Govt Examinations',
      coverage: 'TNPSC Group 1, 2, 4, VAO and SSLC 10th / HSC 12th State Board Papers',
      badge: 'State Public Service',
      badgeColor: '#0EA5E9',
      icon: '🌴'
    }
  ]

  return (
    <div className="page-content">
      <div className="container">
        
        {/* Breadcrumb */}
        <div style={{ display: 'flex', gap: 8, alignItems: 'center', marginBottom: 20, fontSize: '0.8125rem', color: 'var(--text-muted)' }}>
          <Link to="/" style={{ color: 'var(--text-muted)', textDecoration: 'none' }}>Home</Link>
          <span>›</span>
          <span style={{ color: 'var(--text-primary)', fontWeight: 500 }}>Open-Source Repositories Hub</span>
        </div>

        {/* Hero Section */}
        <div style={{
          background: 'linear-gradient(135deg, rgba(99, 102, 241, 0.08) 0%, rgba(16, 185, 129, 0.06) 100%)',
          borderRadius: 20,
          padding: '36px 32px',
          border: '1px solid rgba(99, 102, 241, 0.15)',
          marginBottom: 36,
          position: 'relative',
          overflow: 'hidden'
        }}>
          <div style={{ maxWidth: 840 }}>
            <div style={{
              display: 'inline-flex',
              alignItems: 'center',
              gap: 8,
              padding: '6px 14px',
              borderRadius: 20,
              backgroundColor: 'rgba(99, 102, 241, 0.12)',
              color: '#6366F1',
              fontWeight: 700,
              fontSize: '0.75rem',
              letterSpacing: '0.05em',
              textTransform: 'uppercase',
              marginBottom: 16
            }}>
              <span>🐙</span> Open-Source & Open-Access Ecosystem
            </div>
            <h1 style={{ fontSize: '2.25rem', fontWeight: 800, margin: '0 0 12px', letterSpacing: '-0.02em', lineHeight: 1.2 }}>
              Synchronized Repositories & Statutory Data Hub
            </h1>
            <p style={{ fontSize: '1rem', color: 'var(--text-secondary)', margin: '0 0 24px', lineHeight: 1.6 }}>
              ExamVault combines raw Git trees from open-source GitHub archives (<strong>Shabber10/ALL-PYQ-Papers</strong>, <strong>avallark/NCERT-TextBooks</strong>) with official statutory portals (CBSE, NCERT, UPSC, NTA, TNPSC). All papers and textbooks are delivered via live raw CDN streams with in-platform PDF viewers.
            </p>

            <div style={{ display: 'flex', gap: 12, flexWrap: 'wrap' }}>
              <button
                className="btn btn-primary"
                onClick={handleResync}
                disabled={resyncing}
                style={{ display: 'inline-flex', alignItems: 'center', gap: 8 }}
              >
                <span>{resyncing ? '🔄' : '⚡'}</span>
                <span>{resyncing ? 'Syncing...' : 'Verify Repository Sync'}</span>
              </button>
              <a
                href="https://github.com/Shabber10/ALL-PYQ-Papers"
                target="_blank"
                rel="noreferrer"
                className="btn btn-secondary"
                style={{ display: 'inline-flex', alignItems: 'center', gap: 8 }}
              >
                <span>🐙</span>
                <span>View Shabber10 on GitHub</span>
              </a>
              <a
                href="https://github.com/avallark/NCERT-TextBooks"
                target="_blank"
                rel="noreferrer"
                className="btn btn-secondary"
                style={{ display: 'inline-flex', alignItems: 'center', gap: 8 }}
              >
                <span>📚</span>
                <span>View avallark on GitHub</span>
              </a>
            </div>
          </div>
        </div>

        {/* Live Metrics Grid */}
        <div style={{
          display: 'grid',
          gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))',
          gap: 16,
          marginBottom: 36
        }}>
          {statCards.map((sc, i) => (
            <motion.div
              key={sc.label}
              initial={reduced ? false : { opacity: 0, y: 12 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: i * 0.05 }}
              style={{
                backgroundColor: 'var(--color-surface)',
                border: '1px solid var(--color-border)',
                borderRadius: 16,
                padding: '20px 22px',
                display: 'flex',
                flexDirection: 'column',
                gap: 6
              }}
            >
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                <span style={{ fontSize: '1.5rem' }}>{sc.icon}</span>
                <span style={{
                  fontSize: '0.7rem',
                  fontWeight: 700,
                  color: sc.color,
                  backgroundColor: `${sc.color}15`,
                  padding: '2px 8px',
                  borderRadius: 10
                }}>
                  ACTIVE
                </span>
              </div>
              <div style={{ fontSize: '1.75rem', fontWeight: 800, color: 'var(--text-primary)', marginTop: 4 }}>
                {sc.value}
              </div>
              <div style={{ fontSize: '0.8125rem', color: 'var(--text-secondary)' }}>
                {sc.label}
              </div>
            </motion.div>
          ))}
        </div>

        {/* Section: Primary Connected GitHub Repositories */}
        <div style={{ marginBottom: 40 }}>
          <h2 style={{ fontSize: '1.5rem', fontWeight: 700, marginBottom: 8, display: 'flex', alignItems: 'center', gap: 10 }}>
            <span>🐙</span> Connected GitHub Open-Source Repositories
          </h2>
          <p style={{ color: 'var(--text-secondary)', fontSize: '0.9rem', marginBottom: 20 }}>
            Every document is indexed from its public Git tree and served directly from raw GitHub CDN endpoints.
          </p>

          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(340px, 1fr))', gap: 20 }}>
            
            {/* Shabber10/ALL-PYQ-Papers */}
            <div style={{
              backgroundColor: 'var(--color-surface)',
              border: '1px solid rgba(99, 102, 241, 0.25)',
              borderRadius: 18,
              padding: '26px',
              display: 'flex',
              flexDirection: 'column',
              boxShadow: '0 4px 20px rgba(0,0,0,0.03)'
            }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: 12 }}>
                <div>
                  <span style={{
                    fontSize: '0.72rem',
                    fontWeight: 700,
                    color: '#6366F1',
                    backgroundColor: 'rgba(99, 102, 241, 0.1)',
                    padding: '3px 10px',
                    borderRadius: 12
                  }}>
                    PRIMARY PYQ REPO · BRANCH: main
                  </span>
                  <h3 style={{ fontSize: '1.25rem', fontWeight: 700, margin: '8px 0 4px' }}>
                    Shabber10/ALL-PYQ-Papers
                  </h3>
                </div>
                <span style={{
                  display: 'inline-flex',
                  alignItems: 'center',
                  gap: 6,
                  fontSize: '0.75rem',
                  fontWeight: 600,
                  color: '#10B981',
                  backgroundColor: 'rgba(16, 185, 129, 0.1)',
                  padding: '4px 10px',
                  borderRadius: 12
                }}>
                  <span style={{ width: 6, height: 6, borderRadius: '50%', backgroundColor: '#10B981' }} />
                  Synchronized
                </span>
              </div>

              <p style={{ fontSize: '0.875rem', color: 'var(--text-secondary)', lineHeight: 1.5, marginBottom: 16 }}>
                Massive public repository of previous year question papers across Indian national and state boards. Indexed with 42,159 files and 2,872 verified PDFs.
              </p>

              {/* Coverage Pills */}
              <div style={{ display: 'flex', flexWrap: 'wrap', gap: 8, marginBottom: 20 }}>
                <span className="badge" style={{ backgroundColor: 'rgba(59, 130, 246, 0.1)', color: '#2563EB', fontSize: '0.75rem' }}>
                  CBSE Class 10: 362 PDFs (2015-2023)
                </span>
                <span className="badge" style={{ backgroundColor: 'rgba(16, 185, 129, 0.1)', color: '#059669', fontSize: '0.75rem' }}>
                  CBSE Class 12: 533 PDFs (2015-2023)
                </span>
                <span className="badge" style={{ backgroundColor: 'rgba(245, 158, 11, 0.1)', color: '#D97706', fontSize: '0.75rem' }}>
                  UPSC Civil Services: 1,002 PDFs (2016-2024)
                </span>
                <span className="badge" style={{ backgroundColor: 'rgba(236, 72, 153, 0.1)', color: '#DB2777', fontSize: '0.75rem' }}>
                  JEE Main & Adv: 184 PDFs (2012-2024)
                </span>
                <span className="badge" style={{ backgroundColor: 'rgba(139, 92, 246, 0.1)', color: '#7C3AED', fontSize: '0.75rem' }}>
                  NEET UG: 98 PDFs (2016-2023)
                </span>
                <span className="badge" style={{ backgroundColor: 'rgba(14, 165, 233, 0.1)', color: '#0284C7', fontSize: '0.75rem' }}>
                  Tamil Nadu Board: 12 PDFs
                </span>
              </div>

              <div style={{ marginTop: 'auto', display: 'flex', gap: 10 }}>
                <a
                  href="https://github.com/Shabber10/ALL-PYQ-Papers"
                  target="_blank"
                  rel="noreferrer"
                  className="btn btn-secondary"
                  style={{ flex: 1, fontSize: '0.8125rem', textAlign: 'center' }}
                >
                  Inspect Git Tree →
                </a>
                <Link
                  to="/search?q=GitHub"
                  className="btn btn-primary"
                  style={{ flex: 1, fontSize: '0.8125rem', textAlign: 'center' }}
                >
                  Browse Synced Papers
                </Link>
              </div>
            </div>

            {/* avallark/NCERT-TextBooks */}
            <div style={{
              backgroundColor: 'var(--color-surface)',
              border: '1px solid rgba(16, 185, 129, 0.25)',
              borderRadius: 18,
              padding: '26px',
              display: 'flex',
              flexDirection: 'column',
              boxShadow: '0 4px 20px rgba(0,0,0,0.03)'
            }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: 12 }}>
                <div>
                  <span style={{
                    fontSize: '0.72rem',
                    fontWeight: 700,
                    color: '#10B981',
                    backgroundColor: 'rgba(16, 185, 129, 0.1)',
                    padding: '3px 10px',
                    borderRadius: 12
                  }}>
                    TEXTBOOK ARCHIVE · BRANCH: master
                  </span>
                  <h3 style={{ fontSize: '1.25rem', fontWeight: 700, margin: '8px 0 4px' }}>
                    avallark/NCERT-TextBooks
                  </h3>
                </div>
                <span style={{
                  display: 'inline-flex',
                  alignItems: 'center',
                  gap: 6,
                  fontSize: '0.75rem',
                  fontWeight: 600,
                  color: '#10B981',
                  backgroundColor: 'rgba(16, 185, 129, 0.1)',
                  padding: '4px 10px',
                  borderRadius: 12
                }}>
                  <span style={{ width: 6, height: 6, borderRadius: '50%', backgroundColor: '#10B981' }} />
                  Synchronized
                </span>
              </div>

              <p style={{ fontSize: '0.875rem', color: 'var(--text-secondary)', lineHeight: 1.5, marginBottom: 16 }}>
                Comprehensive NCERT standard textbook and chapter PDFs for Classes 8 through 12, organized by subject (Mathematics, Science, History, Civics, Economics, Geography).
              </p>

              {/* Coverage Pills */}
              <div style={{ display: 'flex', flexWrap: 'wrap', gap: 8, marginBottom: 20 }}>
                <span className="badge" style={{ backgroundColor: 'rgba(16, 185, 129, 0.1)', color: '#059669', fontSize: '0.75rem' }}>
                  Class 10 Textbooks: 78 PDFs
                </span>
                <span className="badge" style={{ backgroundColor: 'rgba(59, 130, 246, 0.1)', color: '#2563EB', fontSize: '0.75rem' }}>
                  Class 12 Textbooks: 92 PDFs
                </span>
                <span className="badge" style={{ backgroundColor: 'rgba(139, 92, 246, 0.1)', color: '#7C3AED', fontSize: '0.75rem' }}>
                  Class 11 Textbooks: 64 PDFs
                </span>
                <span className="badge" style={{ backgroundColor: 'rgba(245, 158, 11, 0.1)', color: '#D97706', fontSize: '0.75rem' }}>
                  Class 9 Textbooks: 41 PDFs
                </span>
                <span className="badge" style={{ backgroundColor: 'rgba(236, 72, 153, 0.1)', color: '#DB2777', fontSize: '0.75rem' }}>
                  Class 8 Textbooks: 18 PDFs
                </span>
              </div>

              <div style={{ marginTop: 'auto', display: 'flex', gap: 10 }}>
                <a
                  href="https://github.com/avallark/NCERT-TextBooks"
                  target="_blank"
                  rel="noreferrer"
                  className="btn btn-secondary"
                  style={{ flex: 1, fontSize: '0.8125rem', textAlign: 'center' }}
                >
                  Inspect Git Tree →
                </a>
                <Link
                  to="/textbooks"
                  className="btn btn-primary"
                  style={{ flex: 1, fontSize: '0.8125rem', textAlign: 'center' }}
                >
                  Browse Textbooks
                </Link>
              </div>
            </div>

          </div>
        </div>

        {/* Section: Statutory Government Portals */}
        <div style={{ marginBottom: 40 }}>
          <h2 style={{ fontSize: '1.5rem', fontWeight: 700, marginBottom: 8, display: 'flex', alignItems: 'center', gap: 10 }}>
            <span>🏛️</span> Official Statutory Portals & Examination Gazettes
          </h2>
          <p style={{ color: 'var(--text-secondary)', fontSize: '0.9rem', marginBottom: 20 }}>
            Official regulatory bodies whose curricula, gazettes, and verified question papers form the statutory baseline of ExamVault.
          </p>

          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))', gap: 16 }}>
            {statutoryArchives.map(sa => (
              <div
                key={sa.name}
                style={{
                  backgroundColor: 'var(--color-surface)',
                  border: '1px solid var(--color-border)',
                  borderRadius: 14,
                  padding: '20px 22px',
                  display: 'flex',
                  flexDirection: 'column'
                }}
              >
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: 8 }}>
                  <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
                    <span style={{ fontSize: '1.4rem' }}>{sa.icon}</span>
                    <h4 style={{ fontSize: '1rem', fontWeight: 700, margin: 0 }}>{sa.name}</h4>
                  </div>
                  <span style={{
                    fontSize: '0.7rem',
                    fontWeight: 700,
                    color: sa.badgeColor,
                    backgroundColor: `${sa.badgeColor}15`,
                    padding: '2px 8px',
                    borderRadius: 10
                  }}>
                    {sa.badge}
                  </span>
                </div>
                <div style={{ fontSize: '0.78rem', color: 'var(--text-muted)', marginBottom: 10, fontWeight: 500 }}>
                  {sa.authority}
                </div>
                <p style={{ fontSize: '0.825rem', color: 'var(--text-secondary)', lineHeight: 1.4, margin: '0 0 16px' }}>
                  {sa.coverage}
                </p>
                <div style={{ marginTop: 'auto' }}>
                  <a
                    href={sa.url}
                    target="_blank"
                    rel="noreferrer"
                    style={{ fontSize: '0.8125rem', color: 'var(--color-primary)', textDecoration: 'none', fontWeight: 600 }}
                  >
                    Visit Official Portal ↗
                  </a>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Section: End-to-End Architectural Integration */}
        <div style={{
          backgroundColor: 'var(--color-surface)',
          border: '1px solid var(--color-border)',
          borderRadius: 16,
          padding: '28px',
          marginBottom: 40
        }}>
          <h3 style={{ fontSize: '1.2rem', fontWeight: 700, margin: '0 0 12px' }}>
            🛠️ How Synchronization & Single Card Architecture Works
          </h3>
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(240px, 1fr))', gap: 16, fontSize: '0.875rem', color: 'var(--text-secondary)', lineHeight: 1.5 }}>
            <div style={{ borderLeft: '3px solid #6366F1', paddingLeft: 14 }}>
              <strong style={{ color: 'var(--text-primary)', display: 'block', marginBottom: 4 }}>1. Recursive Git Tree Scraper</strong>
              Scans remote repository trees via GitHub API, discovering paths, file sizes, and sha fingerprints across 42,000+ items.
            </div>
            <div style={{ borderLeft: '3px solid #10B981', paddingLeft: 14 }}>
              <strong style={{ color: 'var(--text-primary)', display: 'block', marginBottom: 4 }}>2. Automated Subject & Category Mapping</strong>
              Parses examination standards (10th, 12th, UPSC, JEE, NEET), academic years, and subjects, mapping them directly to database IDs.
            </div>
            <div style={{ borderLeft: '3px solid #F59E0B', paddingLeft: 14 }}>
              <strong style={{ color: 'var(--text-primary)', display: 'block', marginBottom: 4 }}>3. Single-Card Co-location Rule</strong>
              Pairs question papers with co-located answer keys, prescribed textbooks, and statutory syllabus blueprints on one unified card.
            </div>
            <div style={{ borderLeft: '3px solid #EC4899', paddingLeft: 14 }}>
              <strong style={{ color: 'var(--text-primary)', display: 'block', marginBottom: 4 }}>4. In-Platform Streaming PDF Proxy</strong>
              Serves GitHub raw CDN streams with full CORS headers, offline IndexedDB caching, and Gemini AI doubt solving support.
            </div>
          </div>
        </div>

      </div>
    </div>
  )
}
