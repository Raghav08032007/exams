/**
 * Login page
 * Route: /login
 */
import { useState, useEffect } from 'react'
import { Link, useNavigate, useLocation } from 'react-router-dom'
import { login, googleLogin } from '../../api/client'
import { useAuthStore, useToastStore } from '../../store'

export default function LoginPage() {
  const navigate = useNavigate()
  const location = useLocation()
  const { user, setAuth } = useAuthStore()
  const { addToast } = useToastStore()

  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

  const from = location.state?.from?.pathname || '/'

  // Automatically redirect if user is already logged in
  useEffect(() => {
    if (user) {
      navigate(from, { replace: true })
    }
  }, [user, navigate, from])

  const handleSubmit = async (e) => {
    e.preventDefault()
    setError('')
    setLoading(true)
    try {
      const data = await login({ email, password })
      setAuth(data.user, data.access_token)
      addToast(`Welcome back, ${data.user.name}!`)
      navigate(from, { replace: true })
    } catch (err) {
      setError(err.response?.data?.error || 'Login failed. Please try again.')
    } finally {
      setLoading(false)
    }
  }

  const handleGoogleSignIn = async () => {
    setLoading(true)
    setError('')
    try {
      const demoEmail = prompt('Enter your Google email account:', 'user@gmail.com')
      if (!demoEmail) {
        setLoading(false)
        return
      }
      const nameGuess = demoEmail.split('@')[0].replace(/[._]/g, ' ').toUpperCase()
      const data = await googleLogin({
        email: demoEmail,
        name: nameGuess,
      })
      setAuth(data.user, data.access_token)
      addToast(`Signed in as ${data.user.name} via Google!`, 'success')
      navigate(from, { replace: true })
    } catch (err) {
      setError(err.response?.data?.error || 'Google Sign-In failed')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="auth-page">
      <div className="auth-card">
        <div style={{ textAlign: 'center', marginBottom: 'var(--space-6)' }}>
          <Link to="/" className="navbar-brand" style={{ justifyContent: 'center', display: 'flex', marginBottom: 'var(--space-4)' }}>
            Exam<span className="brand-vault">Vault</span>
            <span className="brand-dot" />
          </Link>

          {/* Auth Navigation Tabs: Sign In / Register */}
          <div
            style={{
              display: 'flex',
              background: 'var(--color-bg)',
              padding: '4px',
              borderRadius: '12px',
              border: '1px solid var(--color-border)',
              marginBottom: 'var(--space-5)',
            }}
          >
            <button
              type="button"
              className="btn btn-sm"
              style={{
                flex: 1,
                justifyContent: 'center',
                borderRadius: '8px',
                backgroundColor: 'var(--color-bg-card)',
                color: 'var(--text-primary)',
                fontWeight: 600,
                boxShadow: 'var(--shadow-sm)',
                border: 'none',
              }}
            >
              Sign In
            </button>
            <button
              type="button"
              className="btn btn-sm btn-ghost"
              onClick={() => navigate('/register', { state: location.state })}
              style={{
                flex: 1,
                justifyContent: 'center',
                borderRadius: '8px',
                color: 'var(--text-muted)',
                fontWeight: 500,
                border: 'none',
              }}
            >
              Register
            </button>
          </div>

          <h1 style={{ fontSize: '1.5rem', marginBottom: 'var(--space-2)' }}>
            Sign in
          </h1>
          <p style={{ color: 'var(--text-muted)', fontSize: '0.875rem' }}>
            Access your bookmarks and history
          </p>
        </div>

        <form onSubmit={handleSubmit}>
          <div className="form-group">
            <label className="form-label" htmlFor="login-email">Email</label>
            <input
              id="login-email"
              type="email"
              className="form-input"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              placeholder="you@example.com"
              required
              autoComplete="email"
            />
          </div>

          <div className="form-group">
            <label className="form-label" htmlFor="login-password">Password</label>
            <input
              id="login-password"
              type="password"
              className="form-input"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              placeholder="••••••••"
              required
              autoComplete="current-password"
            />
          </div>

          {error && <p className="form-error">{error}</p>}

          <button
            type="submit"
            className="btn btn-primary"
            style={{ width: '100%', justifyContent: 'center', marginTop: 'var(--space-3)' }}
            disabled={loading}
          >
            {loading ? 'Signing in…' : 'Sign In'}
          </button>
        </form>

        <div style={{ display: 'flex', alignItems: 'center', gap: 12, margin: 'var(--space-5) 0' }}>
          <div style={{ flex: 1, height: 1, background: 'var(--color-border)' }} />
          <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)', textTransform: 'uppercase', letterSpacing: '0.05em' }}>OR</span>
          <div style={{ flex: 1, height: 1, background: 'var(--color-border)' }} />
        </div>

        <button
          type="button"
          className="btn btn-ghost"
          style={{ width: '100%', justifyContent: 'center', gap: 10, border: '1px solid var(--color-border)', background: 'var(--color-bg-card)' }}
          onClick={handleGoogleSignIn}
          disabled={loading}
        >
          <svg width="18" height="18" viewBox="0 0 18 18">
            <path fill="#4285F4" d="M17.64 9.2c0-.74-.06-1.28-.19-1.84H9v3.34h4.96c-.1.83-.64 2.08-1.84 2.92l2.84 2.2c1.7-1.57 2.68-3.88 2.68-6.62z"/>
            <path fill="#34A853" d="M9 18c2.43 0 4.47-.8 5.96-2.18l-2.84-2.2c-.76.53-1.78.9-3.12.9-2.38 0-4.41-1.57-5.13-3.72H.97v2.29C2.47 16.03 5.48 18 9 18z"/>
            <path fill="#FBBC05" d="M3.87 10.8c-.19-.53-.3-1.1-.3-1.8s.11-1.27.29-1.8V4.91H.97C.35 6.14 0 7.53 0 9c0 1.47.35 2.86.97 4.09l2.9-2.29z"/>
            <path fill="#EA4335" d="M9 3.58c1.32 0 2.5.45 3.44 1.35l2.58-2.58C13.46.89 11.43 0 9 0 5.48 0 2.47 1.97.97 4.91l2.9 2.29c.72-2.15 2.75-3.62 5.13-3.62z"/>
          </svg>
          Sign in with Google
        </button>

        <p style={{ textAlign: 'center', marginTop: 'var(--space-6)', fontSize: '0.875rem', color: 'var(--text-muted)' }}>
          Don't have an account?{' '}
          <Link to="/register" state={location.state} style={{ color: 'var(--text-primary)', fontWeight: 600 }}>
            Register
          </Link>
        </p>
      </div>
    </div>
  )
}
