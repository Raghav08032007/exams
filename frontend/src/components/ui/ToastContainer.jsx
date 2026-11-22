/**
 * Toast notification container.
 * Uses the global useToastStore to render toasts in bottom-right corner.
 */
import { useToastStore } from '../../store'

export default function ToastContainer() {
  const { toasts, removeToast } = useToastStore()

  return (
    <div style={{ position: 'fixed', bottom: 24, right: 24, zIndex: 9999, display: 'flex', flexDirection: 'column', gap: 8 }}>
      {toasts.map((toast) => (
        <div
          key={toast.id}
          className={`toast toast-${toast.type}`}
          onClick={() => removeToast(toast.id)}
          style={{ cursor: 'pointer', animation: 'slideInRight 0.3s ease' }}
        >
          {toast.type === 'success' ? '✓' : '✕'} {toast.message}
        </div>
      ))}
      <style>{`
        @keyframes slideInRight {
          from { opacity: 0; transform: translateX(20px); }
          to   { opacity: 1; transform: translateX(0); }
        }
      `}</style>
    </div>
  )
}
