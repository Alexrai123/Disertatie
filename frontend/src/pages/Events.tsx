import React, { useEffect, useState } from 'react'
import api from '../api'
import { Card, LoadingContainer, Alert, Table, EmptyState, Badge, Pagination } from '../components'

// References:
// - see docs/13_app_arch.txt §1 Presentation (Event Management Module UI)
// - see docs/02_functional_req.txt §2 System Monitoring

type EventItem = {
  id: number
  event_type: string
  target_file_id?: number | null
  target_folder_id?: number | null
  triggered_by_user_id?: number | null
  timestamp?: string | null
  processed_flag: boolean
}

type EventsResponse = {
  items: EventItem[]
  total: number
  limit: number
  offset: number
  has_more: boolean
}

export default function Events() {
  const [events, setEvents] = useState<EventItem[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  // Filters
  const [filterType, setFilterType] = useState<string>('all')
  const [filterProcessed, setFilterProcessed] = useState<string>('all')

  // Pagination
  const [currentPage, setCurrentPage] = useState(1)
  const [totalPages, setTotalPages] = useState(1)
  const [hasMore, setHasMore] = useState(false)
  const limit = 20

  async function load(page: number = 1) {
    try {
      setLoading(true)
      setError(null)

      const offset = (page - 1) * limit
      const params = new URLSearchParams({
        limit: limit.toString(),
        offset: offset.toString(),
      })

      if (filterType !== 'all') {
        params.append('event_type', filterType)
      }

      if (filterProcessed !== 'all') {
        params.append('processed', filterProcessed === 'true' ? 'true' : 'false')
      }

      const { data } = await api.get<EventsResponse>(`/events/?${params}`)

      setEvents(data.items || data as any)
      setHasMore(data.has_more || false)
      setTotalPages(Math.ceil((data.total || 0) / limit))
      setCurrentPage(page)
    } catch (err: any) {
      setError(err.response?.data?.error || 'Failed to load events')
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    load(1)
  }, [filterType, filterProcessed])

  const getEventTypeBadge = (type: string) => {
    const badges: Record<string, 'success' | 'warning' | 'danger'> = {
      create: 'success',
      modify: 'warning',
      delete: 'danger',
    }
    return <Badge type={badges[type] || 'info'}>{type}</Badge>
  }

  const getProcessedBadge = (processed: boolean) => {
    return processed ?
      <Badge type="success">✓ Processed</Badge> :
      <Badge type="warning">⏳ Pending</Badge>
  }

  const formatTimestamp = (timestamp?: string | null) => {
    if (!timestamp) return 'N/A'
    return new Date(timestamp).toLocaleString()
  }

  const columns = [
    {
      key: 'id',
      header: 'ID',
      render: (event: EventItem) => <code>#{event.id}</code>
    },
    {
      key: 'event_type',
      header: 'Type',
      render: (event: EventItem) => getEventTypeBadge(event.event_type)
    },
    {
      key: 'target',
      header: 'Target',
      render: (event: EventItem) => {
        if (event.target_file_id) return `File #${event.target_file_id}`
        if (event.target_folder_id) return `Folder #${event.target_folder_id}`
        return <span className="text-muted">N/A</span>
      }
    },
    {
      key: 'timestamp',
      header: 'Timestamp',
      render: (event: EventItem) => (
        <span className="text-muted" style={{ fontSize: '0.875rem' }}>
          {formatTimestamp(event.timestamp)}
        </span>
      )
    },
    {
      key: 'status',
      header: 'Status',
      render: (event: EventItem) => getProcessedBadge(event.processed_flag)
    },
  ]

  return (
    <div className="main-content">
      <Card
        title="📊 System Events"
        actions={
          <Badge type="info">{events.length} event{events.length !== 1 ? 's' : ''}</Badge>
        }
      >
        {error && <Alert type="error" message={error} onClose={() => setError(null)} />}

        {/* Filters */}
        <div className="grid grid-2 gap-2 mb-3">
          <div className="form-group">
            <label className="form-label">Event Type</label>
            <select
              className="form-select"
              value={filterType}
              onChange={(e) => setFilterType(e.target.value)}
            >
              <option value="all">All Types</option>
              <option value="create">Create</option>
              <option value="modify">Modify</option>
              <option value="delete">Delete</option>
            </select>
          </div>

          <div className="form-group">
            <label className="form-label">Processing Status</label>
            <select
              className="form-select"
              value={filterProcessed}
              onChange={(e) => setFilterProcessed(e.target.value)}
            >
              <option value="all">All Status</option>
              <option value="true">Processed</option>
              <option value="false">Pending</option>
            </select>
          </div>
        </div>

        {loading ? (
          <LoadingContainer message="Loading events..." />
        ) : events.length === 0 ? (
          <EmptyState
            icon="📊"
            title="No events found"
            message="Events will appear here when file system changes are detected"
          />
        ) : (
          <>
            <Table
              columns={columns}
              data={events}
              loading={false}
            />

            {totalPages > 1 && (
              <Pagination
                currentPage={currentPage}
                totalPages={totalPages}
                hasMore={hasMore}
                onPageChange={load}
              />
            )}
          </>
        )}
      </Card>
    </div>
  )
}
