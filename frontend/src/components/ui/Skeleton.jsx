/**
 * Skeleton loading placeholder — matches exam card dimensions.
 */
export function ExamCardSkeleton() {
  return (
    <div className="card" style={{ minHeight: 260 }}>
      <div className="skeleton" style={{ width: 56, height: 56, borderRadius: 12, marginBottom: 20 }} />
      <div className="skeleton" style={{ width: 80, height: 14, marginBottom: 10 }} />
      <div className="skeleton" style={{ width: '70%', height: 22, marginBottom: 8 }} />
      <div className="skeleton" style={{ width: '90%', height: 16, marginBottom: 6 }} />
      <div className="skeleton" style={{ width: '80%', height: 16 }} />
    </div>
  )
}

export function PaperItemSkeleton() {
  return (
    <div className="paper-item" style={{ pointerEvents: 'none' }}>
      <div className="skeleton" style={{ width: 56, height: 40, flexShrink: 0, borderRadius: 6 }} />
      <div style={{ flex: 1 }}>
        <div className="skeleton" style={{ width: '60%', height: 18, marginBottom: 8 }} />
        <div className="skeleton" style={{ width: '40%', height: 14 }} />
      </div>
      <div className="skeleton" style={{ width: 80, height: 32, borderRadius: 8 }} />
    </div>
  )
}

export function PageSkeleton({ count = 5 }) {
  return (
    <div className="papers-list">
      {Array.from({ length: count }).map((_, i) => (
        <PaperItemSkeleton key={i} />
      ))}
    </div>
  )
}
