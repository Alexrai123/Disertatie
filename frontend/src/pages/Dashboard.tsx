import React, { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import api from '../api'
import { Card, LoadingContainer, Alert, Badge } from '../components'

// Dashboard Statistics Types
type DashboardStats = {
    folders: number
    files: number
    events: number
    logs: number
    users?: number
    ai_rules?: number
}

type RecentEvent = {
    id: number
    event_type: string
    timestamp: string
    processed_flag: boolean
}

type AIStats = {
    total_rules: number
    adaptive_rules: number
    severity_distribution: {
        Low: number
        Medium: number
        High: number
        Critical: number
    }
}

type FeedbackStats = {
    total_feedback: number
    approvals: number
    rejections: number
    modifications: number
    approval_rate: number
}

export default function Dashboard() {
    const [loading, setLoading] = useState(true)
    const [error, setError] = useState<string | null>(null)

    const [stats, setStats] = useState<DashboardStats>({
        folders: 0,
        files: 0,
        events: 0,
        logs: 0,
    })

    const [recentEvents, setRecentEvents] = useState<RecentEvent[]>([])
    const [aiStats, setAIStats] = useState<AIStats | null>(null)
    const [feedbackStats, setFeedbackStats] = useState<FeedbackStats | null>(null)

    async function loadDashboard() {
        try {
            setLoading(true)
            setError(null)

            // Load all statistics in parallel
            const [foldersRes, filesRes, eventsRes, logsRes] = await Promise.all([
                api.get('/folders/'),
                api.get('/files/'),
                api.get('/events/?limit=5'),
                api.get('/logs/'),
            ])

            // Extract counts
            setStats({
                folders: foldersRes.data.total || foldersRes.data.length || 0,
                files: filesRes.data.total || filesRes.data.length || 0,
                events: eventsRes.data.total || eventsRes.data.length || 0,
                logs: logsRes.data.length || 0,
            })

            // Recent events
            const events = eventsRes.data.items || eventsRes.data || []
            setRecentEvents(events.slice(0, 5))

            // Try to load AI statistics (admin only endpoints)
            try {
                const aiRes = await api.get('/ai-rules/')
                const rules = aiRes.data.items || aiRes.data || []

                const aiStatsData: AIStats = {
                    total_rules: rules.length,
                    adaptive_rules: rules.filter((r: any) => r.adaptive_flag).length,
                    severity_distribution: {
                        Low: rules.filter((r: any) => r.severity_level === 'Low').length,
                        Medium: rules.filter((r: any) => r.severity_level === 'Medium').length,
                        High: rules.filter((r: any) => r.severity_level === 'High').length,
                        Critical: rules.filter((r: any) => r.severity_level === 'Critical').length,
                    }
                }
                setAIStats(aiStatsData)
            } catch {
                // Not admin or endpoint not available
            }

        } catch (err: any) {
            setError(err.response?.data?.error || 'Failed to load dashboard')
        } finally {
            setLoading(false)
        }
    }

    useEffect(() => {
        loadDashboard()
    }, [])

    if (loading) {
        return (
            <div className="main-content">
                <LoadingContainer message="Loading dashboard..." />
            </div>
        )
    }

    if (error) {
        return (
            <div className="main-content">
                <Alert type="error" message={error} />
            </div>
        )
    }

    const getEventTypeBadge = (type: string) => {
        const badges: Record<string, 'success' | 'warning' | 'danger'> = {
            create: 'success',
            modify: 'warning',
            delete: 'danger',
        }
        return <Badge type={badges[type] || 'info'}>{type}</Badge>
    }

    const formatTimestamp = (timestamp: string) => {
        const date = new Date(timestamp)
        const now = new Date()
        const diff = now.getTime() - date.getTime()
        const minutes = Math.floor(diff / 60000)

        if (minutes < 1) return 'Just now'
        if (minutes < 60) return `${minutes}m ago`
        if (minutes < 1440) return `${Math.floor(minutes / 60)}h ago`
        return date.toLocaleDateString()
    }

    return (
        <div className="main-content">
            <div className="mb-3">
                <h1>📊 Dashboard</h1>
                <p className="text-muted">System overview and statistics</p>
            </div>

            {/* Statistics Cards */}
            <div className="grid grid-4 mb-3">
                <Card>
                    <div className="flex flex-col">
                        <span className="text-muted" style={{ fontSize: '0.875rem' }}>Monitored Folders</span>
                        <h2 style={{ margin: '0.5rem 0' }}>{stats.folders}</h2>
                        <Link to="/folders" className="text-primary" style={{ fontSize: '0.875rem' }}>
                            View all →
                        </Link>
                    </div>
                </Card>

                <Card>
                    <div className="flex flex-col">
                        <span className="text-muted" style={{ fontSize: '0.875rem' }}>Monitored Files</span>
                        <h2 style={{ margin: '0.5rem 0' }}>{stats.files}</h2>
                        <Link to="/files" className="text-primary" style={{ fontSize: '0.875rem' }}>
                            View all →
                        </Link>
                    </div>
                </Card>

                <Card>
                    <div className="flex flex-col">
                        <span className="text-muted" style={{ fontSize: '0.875rem' }}>Total Events</span>
                        <h2 style={{ margin: '0.5rem 0' }}>{stats.events}</h2>
                        <Link to="/events" className="text-primary" style={{ fontSize: '0.875rem' }}>
                            View all →
                        </Link>
                    </div>
                </Card>

                <Card>
                    <div className="flex flex-col">
                        <span className="text-muted" style={{ fontSize: '0.875rem' }}>System Logs</span>
                        <h2 style={{ margin: '0.5rem 0' }}>{stats.logs}</h2>
                        <Link to="/logs" className="text-primary" style={{ fontSize: '0.875rem' }}>
                            View all →
                        </Link>
                    </div>
                </Card>
            </div>

            <div className="grid grid-2 gap-2">
                {/* Recent Events */}
                <Card title="📊 Recent Events">
                    {recentEvents.length === 0 ? (
                        <p className="text-muted">No recent events</p>
                    ) : (
                        <div style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem' }}>
                            {recentEvents.map((event) => (
                                <div
                                    key={event.id}
                                    className="card"
                                    style={{ padding: '0.75rem' }}
                                >
                                    <div className="flex justify-between items-center">
                                        <div className="flex items-center gap-2">
                                            <code style={{ fontSize: '0.75rem' }}>#{event.id}</code>
                                            {getEventTypeBadge(event.event_type)}
                                        </div>
                                        <span className="text-muted" style={{ fontSize: '0.75rem' }}>
                                            {formatTimestamp(event.timestamp)}
                                        </span>
                                    </div>
                                    <div className="mt-1">
                                        {event.processed_flag ? (
                                            <Badge type="success">✓ Processed</Badge>
                                        ) : (
                                            <Badge type="warning">⏳ Pending</Badge>
                                        )}
                                    </div>
                                </div>
                            ))}
                        </div>
                    )}
                    <Link to="/events" className="btn btn-secondary btn-sm mt-2" style={{ width: '100%' }}>
                        View All Events
                    </Link>
                </Card>

                {/* AI Statistics */}
                {aiStats ? (
                    <Card title="🤖 AI Engine Status">
                        <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
                            <div>
                                <div className="flex justify-between items-center mb-1">
                                    <span className="text-muted">Total Rules</span>
                                    <strong>{aiStats.total_rules}</strong>
                                </div>
                                <div className="flex justify-between items-center">
                                    <span className="text-muted">Adaptive Rules</span>
                                    <Badge type="success">{aiStats.adaptive_rules}</Badge>
                                </div>
                            </div>

                            <div>
                                <h4 style={{ fontSize: '0.875rem', marginBottom: '0.5rem' }}>Severity Distribution</h4>
                                <div style={{ display: 'flex', flexDirection: 'column', gap: '0.5rem' }}>
                                    <div className="flex justify-between items-center">
                                        <Badge type="info">Low</Badge>
                                        <span>{aiStats.severity_distribution.Low}</span>
                                    </div>
                                    <div className="flex justify-between items-center">
                                        <Badge type="warning">Medium</Badge>
                                        <span>{aiStats.severity_distribution.Medium}</span>
                                    </div>
                                    <div className="flex justify-between items-center">
                                        <Badge type="warning">High</Badge>
                                        <span>{aiStats.severity_distribution.High}</span>
                                    </div>
                                    <div className="flex justify-between items-center">
                                        <Badge type="danger">Critical</Badge>
                                        <span>{aiStats.severity_distribution.Critical}</span>
                                    </div>
                                </div>
                            </div>

                            <Link to="/ai-rules" className="btn btn-primary btn-sm" style={{ width: '100%' }}>
                                Manage AI Rules
                            </Link>
                        </div>
                    </Card>
                ) : (
                    <Card title="🤖 AI Engine Status">
                        <p className="text-muted">AI statistics available for admin users</p>
                    </Card>
                )}
            </div>

            {/* System Health */}
            <Card title="💚 System Health" className="mt-3">
                <div className="grid grid-3 gap-2">
                    <div className="card" style={{ padding: '1rem', textAlign: 'center' }}>
                        <div style={{ fontSize: '2rem', marginBottom: '0.5rem' }}>✅</div>
                        <strong>File Monitoring</strong>
                        <p className="text-muted" style={{ fontSize: '0.875rem', margin: '0.25rem 0 0 0' }}>
                            Active
                        </p>
                    </div>

                    <div className="card" style={{ padding: '1rem', textAlign: 'center' }}>
                        <div style={{ fontSize: '2rem', marginBottom: '0.5rem' }}>✅</div>
                        <strong>AI Engine</strong>
                        <p className="text-muted" style={{ fontSize: '0.875rem', margin: '0.25rem 0 0 0' }}>
                            Running
                        </p>
                    </div>

                    <div className="card" style={{ padding: '1rem', textAlign: 'center' }}>
                        <div style={{ fontSize: '2rem', marginBottom: '0.5rem' }}>✅</div>
                        <strong>Database</strong>
                        <p className="text-muted" style={{ fontSize: '0.875rem', margin: '0.25rem 0 0 0' }}>
                            Connected
                        </p>
                    </div>
                </div>
            </Card>
        </div>
    )
}
