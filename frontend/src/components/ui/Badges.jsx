/**
 * Reusable badge components for papers.
 */

export function AnswerKeyBadge({ hasKey = true }) {
  if (!hasKey) {
    return (
      <span className="badge" style={{
        background: 'rgba(0,0,0,0.04)',
        color: 'var(--text-muted)',
        border: '1px solid var(--color-border)',
        fontSize: '0.72rem',
        fontWeight: 500,
        padding: '2px 7px',
        borderRadius: '6px'
      }}>
        📄 Question Paper Only
      </span>
    )
  }
  return (
    <span
      className="badge badge-answer-key"
      style={{
        display: 'inline-flex',
        alignItems: 'center',
        gap: '4px',
        fontWeight: 600,
        fontSize: '0.72rem',
        padding: '2px 7px',
        borderRadius: '6px',
        background: 'rgba(16, 185, 129, 0.12)',
        color: '#10B981',
        border: '1px solid rgba(16, 185, 129, 0.3)'
      }}
      title="Official Answer Key / Detailed Solutions available with this paper"
    >
      <span>🔑</span>
      <span>Official Ans Key</span>
    </span>
  )
}

export function LanguageBadge({ language }) {
  return <span className="badge badge-language">{language}</span>
}

export function YearBadge({ year }) {
  return <span className="badge badge-year mono">{year}</span>
}

export function ExamBadge({ name }) {
  return <span className="badge badge-exam">{name}</span>
}

export function PaperTypeBadge({ paperType }) {
  const isSample = paperType === 'sample'
  return (
    <span
      className="badge"
      style={{
        display: 'inline-flex',
        alignItems: 'center',
        gap: '4px',
        fontWeight: 600,
        fontSize: '0.75rem',
        padding: '3px 8px',
        borderRadius: '6px',
        background: isSample ? 'rgba(139, 92, 246, 0.12)' : 'rgba(16, 185, 129, 0.12)',
        color: isSample ? '#8B5CF6' : '#10B981',
        border: `1px solid ${isSample ? 'rgba(139, 92, 246, 0.28)' : 'rgba(16, 185, 129, 0.28)'}`,
      }}
      title={isSample ? 'Official Sample / Model Question Paper' : 'Genuine Previous Year Public/Board/Competitive Exam Paper'}
    >
      <span>{isSample ? '📝' : '✓'}</span>
      <span>{isSample ? 'Sample Paper' : 'Original Exam Paper'}</span>
    </span>
  )
}

export function OfflineBadge() {
  return (
    <span className="badge" style={{
      background: 'rgba(46, 95, 163, 0.2)',
      color: '#70A8E8',
      border: '1px solid rgba(70, 130, 210, 0.3)',
    }}>
      ↓ Offline
    </span>
  )
}
