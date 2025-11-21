import React, { useEffect, useState } from 'react'
import api from '../api'
import { Card, LoadingContainer, Alert, Table, EmptyState, Badge } from '../components'

// References:
// - see docs/13_app_arch.txt §1 Presentation (User interface for folder management)
// - see docs/02_functional_req.txt §1, §8 (Users add/remove monitored folders)

type Folder = {
  id: number
  name: string
  path: string
  owner_id: number
  created_at?: string
  modified_at?: string
}

type FoldersResponse = {
  items: Folder[]
  total: number
  limit: number
  offset: number
  has_more: boolean
}

export default function Folders() {
  const [folders, setFolders] = useState<Folder[]>([])
  const [loading, setLoading] = useState(true)
  const [submitting, setSubmitting] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [success, setSuccess] = useState<string | null>(null)

  const [name, setName] = useState('')
  const [path, setPath] = useState('')

  async function load() {
    try {
      setLoading(true)
      setError(null)
      const { data } = await api.get<FoldersResponse>('/folders/')
      setFolders(data.items || data as any) // Handle both paginated and non-paginated responses
    } catch (err: any) {
      setError(err.response?.data?.error || 'Failed to load folders')
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    load()
  }, [])

  async function create(e: React.FormEvent) {
    e.preventDefault()

    if (!name.trim() || !path.trim()) {
      setError('Name and path are required')
      return
    }

    try {
      setSubmitting(true)
      setError(null)
      setSuccess(null)

      await api.post('/folders/', { name, path })

      setName('')
      setPath('')
      setSuccess('Folder "' + name + '" added successfully!')

      await load()
    } catch (err: any) {
      setError(err.response?.data?.error || 'Failed to create folder')
    } finally {
      setSubmitting(false)
    }
  }

  async function remove(folder: Folder) {
    if (!confirm('Are you sure you want to delete "' + folder.name + '"?')) {
      return
    }

    try {
      setError(null)
      setSuccess(null)

      await api.delete('/folders/' + folder.id)
      setSuccess('Folder "' + folder.name + '" deleted successfully!')

      await load()
    } catch (err: any) {
      setError(err.response?.data?.error || 'Failed to delete folder')
    }
  }

  const columns = [
    {
      key: 'name',
      header: 'Name',
      render: (folder: Folder) => <strong>{folder.name}</strong>
    },
    {
      key: 'path',
      header: 'Path',
      render: (folder: Folder) => <code style={{ fontSize: '0.875rem' }}>{folder.path}</code>
    },
    {
      key: 'status',
      header: 'Status',
      render: () => <Badge type="success">Monitoring</Badge>
    },
    {
      key: 'actions',
      header: 'Actions',
      render: (folder: Folder) => (
        <button
          onClick={() => remove(folder)}
          className="btn btn-danger btn-sm"
        >
          Delete
        </button>
      )
    }
  ]

  return (
    <div className="main-content">
      <Card
        title="📁 Monitored Folders"
        actions={
          <Badge type="info">{folders.length} folder{folders.length !== 1 ? 's' : ''}</Badge>
        }
      >
        {error && <Alert type="error" message={error} onClose={() => setError(null)} />}
        {success && <Alert type="success" message={success} onClose={() => setSuccess(null)} />}

        <form onSubmit={create} className="mb-3">
          <div className="grid grid-2 gap-2">
            <div className="form-group">
              <label className="form-label">Folder Name</label>
              <input
                type="text"
                className="form-input"
                placeholder="e.g., Documents"
                value={name}
                onChange={(e) => setName(e.target.value)}
                disabled={submitting}
              />
            </div>

            <div className="form-group">
              <label className="form-label">Folder Path</label>
              <input
                type="text"
                className="form-input"
                placeholder="e.g., C:\Users\Alex\Documents"
                value={path}
                onChange={(e) => setPath(e.target.value)}
                disabled={submitting}
              />
            </div>
          </div>

          <button
            type="submit"
            className="btn btn-primary"
            disabled={submitting || !name.trim() || !path.trim()}
          >
            {submitting ? 'Adding...' : '+ Add Folder'}
          </button>
        </form>

        {loading ? (
          <LoadingContainer message="Loading folders..." />
        ) : folders.length === 0 ? (
          <EmptyState
            icon="📁"
            title="No folders yet"
            message="Add a folder to start monitoring file system events"
            action={null}
          />
        ) : (
          <Table
            columns={columns}
            data={folders}
            loading={false}
          />
        )}
      </Card>
    </div>
  )
}
