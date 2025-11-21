import React, { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { useAuth } from '../auth'
import { Card, Alert, Spinner } from '../components'

export default function Login() {
  const { login } = useAuth()
  const nav = useNavigate()
  const [username, setUsername] = useState('')
  const [password, setPassword] = useState('')
  const [error, setError] = useState<string | null>(null)
  const [loading, setLoading] = useState(false)

  async function onSubmit(e: React.FormEvent) {
    e.preventDefault()

    if (!username.trim() || !password.trim()) {
      setError('Username and password are required')
      return
    }

    try {
      setLoading(true)
      setError(null)
      await login(username, password)
      nav('/')
    } catch (err: any) {
      setError(err?.response?.data?.detail || 'Login failed. Please check your credentials.')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="main-content" style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', minHeight: '80vh' }}>
      <Card title="🛡️ Secure Login" style={{ maxWidth: '400px', width: '100%' }}>
        {error && <Alert type="error" message={error} onClose={() => setError(null)} />}

        <form onSubmit={onSubmit}>
          <div className="form-group">
            <label className="form-label">Username</label>
            <input
              type="text"
              className="form-input"
              placeholder="Enter your username"
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              disabled={loading}
              autoFocus
            />
          </div>

          <div className="form-group">
            <label className="form-label">Password</label>
            <input
              type="password"
              className="form-input"
              placeholder="Enter your password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              disabled={loading}
            />
          </div>

          <button
            type="submit"
            className="btn btn-primary btn-lg"
            style={{ width: '100%' }}
            disabled={loading}
          >
            {loading ? (
              <>
                <Spinner size="sm" />
                <span>Logging in...</span>
              </>
            ) : (
              'Login'
            )}
          </button>
        </form>

        <div className="mt-3 text-center text-muted" style={{ fontSize: '0.875rem' }}>
          <p>Demo Credentials:</p>
          <p><strong>Admin:</strong> admin / admin</p>
          <p><strong>User:</strong> user / user</p>
        </div>
      </Card>
    </div>
  )
}
