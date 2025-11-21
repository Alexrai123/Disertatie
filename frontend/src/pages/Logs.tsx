import React, { useEffect, useState } from 'react'
import api from '../api'
import { Card, LoadingContainer, Alert, Table, EmptyState, Badge, Pagination } from '../components'

// References:
// - see docs/13_app_arch.txt §1 Presentation (Admin dashboard with logs)
// - see docs/02_functional_req.txt §1 Admin can view logs; Users view own activity logs

type LogItem = {
  id: number
  log_type: string
  message: string
  related_event_id?: number | null
  timestamp?: string | null
}

export default function Logs() {
  const [logs, setLogs] = useState<LogItem[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  // Filter
  const [filterType, setFilterType] = useState<string>('all')

  // Pagination
  const [currentPage, setCurrentPage] = useState(1)
  const limit = 50

  async function load(page: number = 1) {
    try {
      setLoading(true)
      setError(null)

      const { data } = await api.get<LogItem[]>('/logs/')

      // Client-side filtering and pagination
      let filtered = data
      if (filterType !== 'all') {
        filtered = data.filter(log => log.log_type === filterType)
      }

      const offset = (page - 1) * limit
      const paginated = filtered.slice(offset, offset + limit)

      setLogs(paginated)
      setCurrentPage(page)
    } catch (err: any) {
      setError(err.response?.data?.error || 'Failed to load logs')
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    load(1)
  }, [filterType])

  const getLogTypeBadge = (type: string) => {
    const badges: Record<string, 'success' | 'warning' | 'danger' | 'info' | 'primary'> = {
      NOTIFY: 'info',
      ESCALATE: 'danger',
      AI_FEEDBACK: 'primary',
      AI_LEARNING: 'success',
      FOLDER_CREATE: 'success',
      FOLDER_DELETE: 'warning',
      FILE_CREATE: 'success',
      FILE_DELETE: 'warning',
      FILE_MONITOR: 'info',
      FILE_MONITOR_ERROR: 'danger',
    }
    return <Badge type={badges[type] || 'info'}>{type}</Badge>
  }

  const formatTimestamp = (timestamp?: string | null) => {
    if (!timestamp) return 'N/A'
    return new Date(timestamp).toLocaleString()
  }

  const columns = [
    {
      key: 'id',
      header: 'ID',
      render: (log: LogItem) => <code>#{log.id}</code>
    },
    {
      key: 'log_type',
      header: 'Type',
      render: (log: LogItem) => getLogTypeBadge(log.log_type)
    },
    {
      key: 'message',
      header: 'Message',
      render: (log: LogItem) => (
        <span style={{ fontSize: '0.875rem' }}>{log.message}</span>
      )
    },
    {
      key: 'event',
      header: 'Related Event',
      render: (log: LogItem) => (
        log.related_event_id ?
          <code>Event #{log.related_event_id}</code> :
          <span className="text-muted">-</span>
      )
    },
    {
      key: 'timestamp',
      header: 'Timestamp',
      render: (log: LogItem) => (
        <span className="text-muted" style={{ fontSize: '0.875rem' }}>
          {formatTimestamp(log.timestamp)}
        </span>
      )
    },
  ]

  // Get unique log types for filter
  const logTypes = ['all', 'NOTIFY', 'ESCALATE', 'AI_FEEDBACK', 'AI_LEARNING',
    'FOLDER_CREATE', 'FOLDER_DELETE', 'FILE_CREATE', 'FILE_DELETE',
    'FILE_MONITOR', 'FILE_MONITOR_ERROR']

  return (
    <div className="main-content">
      <Card
        title="📝 System Logs"
        actions={
          <Badge type="info">{logs.length} log{logs.length !== 1 ? 's' : ''}</Badge>
        }
      >
        {error && <Alert type="error" message={error} onClose={() => setError(null)} />}

        {/* Filter */}
        <div className="form-group mb-3">
          <label className="form-label">Filter by Type</label>
          <select
            className="form-select"
            value={filterType}
            onChange={(e) => setFilterType(e.target.value)}
            style={{ maxWidth: '300px' }}
          >
            {logTypes.map(type => (
              <option key={type} value={type}>
                {type === 'all' ? 'All Types' : type}
              </option>
            ))}
          </select>
        </div>

        {loading ? (
          <LoadingContainer message="Loading logs..." />
        ) : logs.length === 0 ? (
          <EmptyState
            icon="📝"
            title="No logs found"
            message="System activity logs will appear here"
          />
        ) : (
          <Table
            columns={columns}
            data={logs}
            loading={false}
          />
        )}
      </Card>
    </div>
  )
}
