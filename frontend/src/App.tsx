import React from 'react'
import { Routes, Route, Navigate, Link, useLocation } from 'react-router-dom'
import { AuthProvider, useAuth } from './auth'
import { ErrorBoundary } from './components'
import Login from './pages/Login'
import Dashboard from './pages/Dashboard'
import Folders from './pages/Folders'
import Files from './pages/Files'
import Events from './pages/Events'
import Logs from './pages/Logs'
import AIRules from './pages/AIRules'
import Chatbot from './pages/Chatbot'

function Nav() {
  const { user, logout } = useAuth()
  const location = useLocation()

  const isActive = (path: string) => location.pathname === path

  return (
    <nav className="navbar">
      <Link to="/" className="navbar-brand">
        🛡️ AI Monitoring Sandbox
      </Link>

      <ul className="navbar-nav">
        {user && (
          <>
            <li>
              <Link to="/dashboard" className={`nav-link ${isActive('/dashboard') ? 'active' : ''}`}>
                📊 Dashboard
              </Link>
            </li>
            <li>
              <Link to="/folders" className={`nav-link ${isActive('/folders') ? 'active' : ''}`}>
                📁 Folders
              </Link>
            </li>
            <li>
              <Link to="/files" className={`nav-link ${isActive('/files') ? 'active' : ''}`}>
                📄 Files
              </Link>
            </li>
            <li>
              <Link to="/events" className={`nav-link ${isActive('/events') ? 'active' : ''}`}>
                📊 Events
              </Link>
            </li>
            <li>
              <Link to="/logs" className={`nav-link ${isActive('/logs') ? 'active' : ''}`}>
                📝 Logs
              </Link>
            </li>
            {user.role === 'admin' && (
              <>
                <li>
                  <Link to="/ai-rules" className={`nav-link ${isActive('/ai-rules') ? 'active' : ''}`}>
                    🤖 AI Rules
                  </Link>
                </li>
                <li>
                  <Link to="/chatbot" className={`nav-link ${isActive('/chatbot') ? 'active' : ''}`}>
                    💬 Chatbot
                  </Link>
                </li>
              </>
            )}
            <li>
              <button onClick={logout} className="btn btn-secondary btn-sm">
                Logout ({user.username})
              </button>
            </li>
          </>
        )}
        {!user && (
          <li>
            <Link to="/login" className="btn btn-primary btn-sm">
              Login
            </Link>
          </li>
        )}
      </ul>
    </nav>
  )
}

function PrivateRoute({ children, adminOnly = false }: { children: JSX.Element; adminOnly?: boolean }) {
  const { user } = useAuth()
  if (!user) return <Navigate to="/login" replace />
  if (adminOnly && user.role !== 'admin') return <Navigate to="/" replace />
  return children
}

function HomePage() {
  const { user } = useAuth()

  return (
    <div className="main-content">
      <div className="card">
        <div className="card-header">
          <h1 className="card-title">Welcome to Secure AI Monitoring Sandbox</h1>
        </div>
        <div className="card-body">
          {user ? (
            <>
              <p>Hello, <strong>{user.username}</strong>! You are logged in as <span className="badge badge-primary">{user.role}</span>.</p>

              <div className="grid grid-3 mt-3">
                <div className="card">
                  <h3>📊 Dashboard</h3>
                  <p className="text-muted">View system statistics</p>
                  <Link to="/dashboard" className="btn btn-primary btn-sm">View Dashboard</Link>
                </div>

                <div className="card">
                  <h3>📁 Folders</h3>
                  <p className="text-muted">Manage monitored folders</p>
                  <Link to="/folders" className="btn btn-primary btn-sm">View Folders</Link>
                </div>

                <div className="card">
                  <h3>📊 Events</h3>
                  <p className="text-muted">Monitor file system events</p>
                  <Link to="/events" className="btn btn-primary btn-sm">View Events</Link>
                </div>
              </div>

              {user.role === 'admin' && (
                <div className="mt-3">
                  <h3>Admin Tools</h3>
                  <div className="grid grid-2">
                    <div className="card">
                      <h4>🤖 AI Rules</h4>
                      <p className="text-muted">Configure AI behavior and rules</p>
                      <Link to="/ai-rules" className="btn btn-success btn-sm">Manage Rules</Link>
                    </div>

                    <div className="card">
                      <h4>💬 Chatbot</h4>
                      <p className="text-muted">AI assistant for system insights</p>
                      <Link to="/chatbot" className="btn btn-success btn-sm">Open Chatbot</Link>
                    </div>
                  </div>
                </div>
              )}
            </>
          ) : (
            <>
              <p>A secure, AI-powered file monitoring system with adaptive learning capabilities.</p>
              <Link to="/login" className="btn btn-primary mt-2">Get Started</Link>
            </>
          )}
        </div>
      </div>
    </div>
  )
}

export default function App() {
  return (
    <ErrorBoundary>
      <AuthProvider>
        <div className="app-container">
          <Nav />
          <Routes>
            <Route path="/" element={<HomePage />} />
            <Route path="/login" element={<Login />} />
            <Route path="/dashboard" element={<PrivateRoute><Dashboard /></PrivateRoute>} />
            <Route path="/folders" element={<PrivateRoute><Folders /></PrivateRoute>} />
            <Route path="/files" element={<PrivateRoute><Files /></PrivateRoute>} />
            <Route path="/events" element={<PrivateRoute><Events /></PrivateRoute>} />
            <Route path="/logs" element={<PrivateRoute><Logs /></PrivateRoute>} />
            <Route path="/ai-rules" element={<PrivateRoute adminOnly><AIRules /></PrivateRoute>} />
            <Route path="/chatbot" element={<PrivateRoute adminOnly><Chatbot /></PrivateRoute>} />
          </Routes>
        </div>
      </AuthProvider>
    </ErrorBoundary>
  )
}
