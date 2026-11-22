/**
 * Sources & Open Archive Provenance Page.
 * Displays all GitHub repositories, direct download folders, official examination portals,
 * and curriculum references powering ExamVault with live metrics and verified/unverified classifications.
 * Route: /sources
 */
import { useEffect, useState, useMemo } from 'react'
import { Link } from 'react-router-dom'
import { fetchSources } from '../../api/client'
import { useSEO } from '../../hooks/useSEO'
import { useToastStore } from '../../store'

export default function SourcesPage() {
  const [data, setData] = useState(null)
  const [loading, setLoading] = useState(true)
  const [selectedCategory, setSelectedCategory] = useState('all')
  const [searchQuery, setSearchQuery] = useState('')
  const { addToast } = useToastStore()

  useSEO({
    title: 'Open Source Provenance & Data Sources — ExamVault',
    description: 'Explore all GitHub repositories, direct repository download folders, official examination gazettes, and statutory public sources powering ExamVault.'
  })

  useEffect(() => {
    fetchSources()
      .then(setData)
      .catch(() => addToast('Failed to load data sources.', 'error'))
      .finally(() => setLoading(false))
  }, [addToast])

  const sourcesList = data?.sources || []

  // Extract unique categories
  const categories = useMemo(() => {
    const set = new Set()
    sourcesList.forEach(s => {
      if (s.category) set.add(s.category)
    })
    return ['all', ...Array.from(set).sort()]
  }, [sourcesList])

  // Filter sources
  const filteredSources = useMemo(() => {
    return sourcesList.filter(s => {
      const matchesCategory = selectedCategory === 'all' || s.category === selectedCategory
      const matchesSearch = !searchQuery || 
        s.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
        (s.description && s.description.toLowerCase().includes(searchQuery.toLowerCase())) ||
        (s.direct_repo_path && s.direct_repo_path.toLowerCase().includes(searchQuery.toLowerCase()))
      return matchesCategory && matchesSearch
    })
  }, [sourcesList, selectedCategory, searchQuery])

  return (
    <div className="page-content">
      <div className="container" style={{ maxWidth: 1120 }}>

        {/* Breadcrumb */}
        <div style={{ display: 'flex', gap: 8, alignItems: 'center', marginBottom: 20, fontSize: '0.8125rem', color: 'var(--text-muted)' }}>
          <Link to="/" style={{ color: 'var(--text-muted)', textDecoration: 'none' }}>Home</Link>
          <span>›</span>
          <span style={{ color: 'var(--text-primary)', fontWeight: 500 }}>Sources & Provenance Hub</span>
        </div>

        {/* Header */}
        <div style={{
          backgroundColor: 'var(--color-surface)',
          border: '1px solid var(--color-border)',
          borderRadius: 20,
          padding: '32px',
          marginBottom: 28,
          boxShadow: '0 4px 20px rgba(0,0,0,0.02)'
        }}>
          <div style={{
            display: 'inline-flex',
            alignItems: 'center',
            gap: 8,
            padding: '4px 12px',
            borderRadius: 20,
            backgroundColor: 'rgba(99, 102, 241, 0.1)',
            color: '#6366F1',
            fontWeight: 700,
            fontSize: '0.75rem',
            marginBottom: 12
          }}>
            <span>🐙</span> ALL-PYQ-PAPERS & STATUTORY REPOSITORY PROVENANCE
          </div>
          <h1 style={{ fontSize: '2rem', fontWeight: 800, margin: '0 0 10px', letterSpacing: '-0.02em' }}>
            Data Sources & Repository Index
          </h1>
          <p style={{ color: 'var(--text-secondary)', margin: '0 0 20px', fontSize: '0.95rem', maxWidth: 840, lineHeight: 1.6 }}>
            Every paper, textbook, and answer key in ExamVault is attributed to its original open-source GitHub repository path (<strong>Shabber10/ALL-PYQ-Papers</strong>, <strong>avallark/NCERT-TextBooks</strong>) or statutory board portal. Review verified vs provisional paper classifications and inspect raw Git trees below.
          </p>

          <div style={{ display: 'flex', gap: 12, flexWrap: 'wrap' }}>
            <a
              href="https://github.com/Shabber10/ALL-PYQ-Papers"
              target="_blank"
              rel="noreferrer"
              className="btn btn-primary"
              style={{ display: 'inline-flex', alignItems: 'center', gap: 8 }}
            >
              <span>🐙</span>
              <span>Shabber10/ALL-PYQ-Papers Repository ↗</span>
            </a>
            <a
              href="https://pyqs-by-shabber.netlify.app"
              target="_blank"
              rel="noreferrer"
              className="btn btn-secondary"
              style={{ display: 'inline-flex', alignItems: 'center', gap: 8 }}
            >
              <span>🌐</span>
              <span>Netlify Web App Mirror ↗</span>
            </a>
            <Link
              to="/repositories"
              className="btn btn-secondary"
              style={{ display: 'inline-flex', alignItems: 'center', gap: 8 }}
            >
              <span>⚡</span>
              <span>View Live Sync Metrics</span>
            </Link>
          </div>
        </div>

        {/* Live Metrics Strip */}
        <div style={{
          display: 'grid',
          gridTemplateColumns: 'repeat(auto-fit, minmax(180px, 1fr))',
          gap: 16,
          marginBottom: 32
        }}>
          <div style={{
            backgroundColor: 'var(--color-surface)',
            border: '1px solid var(--color-border)',
            borderRadius: 14,
            padding: '18px 20px',
            textAlign: 'center'
          }}>
            <div style={{ fontSize: '1.75rem', fontWeight: 800, color: 'var(--text-primary)' }}>
              {data?.metrics?.total_papers?.toLocaleString() || '3,283'}
            </div>
            <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)', textTransform: 'uppercase', fontWeight: 600, marginTop: 4 }}>
              Total Papers Indexed
            </div>
          </div>

          <div style={{
            backgroundColor: 'var(--color-surface)',
            border: '1px solid rgba(16, 185, 129, 0.3)',
            borderRadius: 14,
            padding: '18px 20px',
            textAlign: 'center'
          }}>
            <div style={{ fontSize: '1.75rem', fontWeight: 800, color: '#10B981' }}>
              {data?.metrics?.verified_papers?.toLocaleString() || '2,756'}
            </div>
            <div style={{ fontSize: '0.75rem', color: '#059669', textTransform: 'uppercase', fontWeight: 700, marginTop: 4 }}>
              🟢 Verified Official Papers
            </div>
          </div>

          <div style={{
            backgroundColor: 'var(--color-surface)',
            border: '1px solid rgba(245, 158, 11, 0.3)',
            borderRadius: 14,
            padding: '18px 20px',
            textAlign: 'center'
          }}>
            <div style={{ fontSize: '1.75rem', fontWeight: 800, color: '#F59E0B' }}>
              {data?.metrics?.unverified_papers?.toLocaleString() || '527'}
            </div>
            <div style={{ fontSize: '0.75rem', color: '#D97706', textTransform: 'uppercase', fontWeight: 700, marginTop: 4 }}>
              🟡 Provisional / Community
            </div>
          </div>

          <div style={{
            backgroundColor: 'var(--color-surface)',
            border: '1px solid var(--color-border)',
            borderRadius: 14,
            padding: '18px 20px',
            textAlign: 'center'
          }}>
            <div style={{ fontSize: '1.75rem', fontWeight: 800, color: '#6366F1' }}>
              {data?.metrics?.answer_keys?.toLocaleString() || '486'}
            </div>
            <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)', textTransform: 'uppercase', fontWeight: 600, marginTop: 4 }}>
              🔑 Co-located Solution Keys
            </div>
          </div>

          <div style={{
            backgroundColor: 'var(--color-surface)',
            border: '1px solid var(--color-border)',
            borderRadius: 14,
            padding: '18px 20px',
            textAlign: 'center'
          }}>
            <div style={{ fontSize: '1.75rem', fontWeight: 800, color: '#EC4899' }}>
              {data?.metrics?.textbooks?.toLocaleString() || '323'}
            </div>
            <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)', textTransform: 'uppercase', fontWeight: 600, marginTop: 4 }}>
              📚 Curriculum Textbooks
            </div>
          </div>
        </div>

        {/* Search & Category Filter */}
        <div style={{
          display: 'flex',
          gap: 12,
          flexWrap: 'wrap',
          marginBottom: 24,
          backgroundColor: 'var(--color-surface)',
          border: '1px solid var(--color-border)',
          borderRadius: 14,
          padding: '14px 18px',
          alignItems: 'center'
        }}>
          <input
            type="text"
            placeholder="Search sources by exam, state, path..."
            value={searchQuery}
            onChange={e => setSearchQuery(e.target.value)}
            style={{
              flex: 1,
              minWidth: 220,
              padding: '8px 14px',
              borderRadius: 8,
              border: '1px solid var(--color-border)',
              backgroundColor: 'var(--color-bg)',
              color: 'var(--text-primary)',
              fontSize: '0.875rem'
            }}
          />

          <select
            value={selectedCategory}
            onChange={e => setSelectedCategory(e.target.value)}
            style={{
              padding: '8px 12px',
              borderRadius: 8,
              border: '1px solid var(--color-border)',
              backgroundColor: 'var(--color-bg)',
              color: 'var(--text-primary)',
              fontSize: '0.875rem'
            }}
          >
            {categories.map(c => (
              <option key={c} value={c}>
                {c === 'all' ? `All Sources (${sourcesList.length})` : c}
              </option>
            ))}
          </select>

          <span style={{ fontSize: '0.8125rem', color: 'var(--text-muted)', marginLeft: 'auto' }}>
            Showing {filteredSources.length} sources
          </span>
        </div>

        {/* Sources Cards Grid */}
        <div style={{
          display: 'grid',
          gridTemplateColumns: 'repeat(auto-fill, minmax(340px, 1fr))',
          gap: 18,
          marginBottom: 40
        }}>
          {filteredSources.map(source => (
            <div
              key={source.id}
              style={{
                backgroundColor: 'var(--color-surface)',
                border: '1px solid var(--color-border)',
                borderRadius: 16,
                padding: '22px',
                display: 'flex',
                flexDirection: 'column',
                boxShadow: '0 2px 10px rgba(0,0,0,0.02)'
              }}
            >
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: 10 }}>
                <span className="badge" style={{
                  backgroundColor: source.category.includes('GitHub') ? 'rgba(99, 102, 241, 0.1)' : 'var(--color-bg)',
                  color: source.category.includes('GitHub') ? '#6366F1' : 'var(--text-primary)',
                  fontSize: '0.72rem',
                  fontWeight: 600
                }}>
                  {source.category}
                </span>

                <span style={{
                  fontSize: '0.72rem',
                  fontWeight: 700,
                  color: source.status === 'Active & Synchronized' ? '#10B981' : '#6366F1',
                  backgroundColor: source.status === 'Active & Synchronized' ? 'rgba(16, 185, 129, 0.1)' : 'rgba(99, 102, 241, 0.1)',
                  padding: '2px 8px',
                  borderRadius: 8
                }}>
                  {source.status}
                </span>
              </div>

              <h3 style={{ fontSize: '1.05rem', fontWeight: 700, margin: '0 0 8px', lineHeight: 1.4 }}>
                {source.name}
              </h3>

              <p style={{ fontSize: '0.825rem', color: 'var(--text-secondary)', margin: '0 0 14px', lineHeight: 1.5, flex: 1 }}>
                {source.description}
              </p>

              {source.direct_repo_path && source.direct_repo_path !== 'N/A' && (
                <div style={{ marginBottom: 14 }}>
                  <span style={{ fontSize: '0.72rem', color: 'var(--text-muted)', display: 'block', marginBottom: 4 }}>
                    Git Tree Path:
                  </span>
                  <code style={{
                    fontSize: '0.75rem',
                    backgroundColor: 'var(--color-bg)',
                    padding: '3px 8px',
                    borderRadius: 6,
                    border: '1px solid var(--color-border)',
                    wordBreak: 'break-all'
                  }}>
                    {source.direct_repo_path}
                  </code>
                </div>
              )}

              <div style={{
                marginTop: 'auto',
                display: 'flex',
                justifyContent: 'space-between',
                alignItems: 'center',
                borderTop: '1px solid var(--color-border)',
                paddingTop: 12
              }}>
                <span style={{ fontSize: '0.8125rem', fontWeight: 600, color: 'var(--text-primary)' }}>
                  {source.papers_count ? `${source.papers_count.toLocaleString()} files` : 'Statutory Reference'}
                </span>

                <a
                  href={source.url}
                  target="_blank"
                  rel="noreferrer"
                  style={{
                    fontSize: '0.8125rem',
                    color: 'var(--color-primary)',
                    fontWeight: 600,
                    textDecoration: 'none'
                  }}
                >
                  Visit Source ↗
                </a>
              </div>
            </div>
          ))}
        </div>

      </div>
    </div>
  )
}
