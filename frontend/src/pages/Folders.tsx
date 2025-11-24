import React, { useEffect, useState } from 'react'
import api from '../api'
import { Card, LoadingContainer, Alert, Table, EmptyState, Badge, Modal } from '../components'

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
  const [deleteModalOpen, setDeleteModalOpen] = useState(false)
  const [folderToDelete, setFolderToDelete] = useState<Folder | null>(null)

  // Extract folder name from path
  function extractFolderName(folderPath: string): string {
    // Remove trailing slashes
    const cleanPath = folderPath.replace(/[/\\]+$/, '')
    // Get the last segment
    const segments = cleanPath.split(/[/\\]/)
    return segments[segments.length - 1] || ''
  }

  // Handle folder selection via directory picker
  async function selectFolder() {
    try {
      // Check if the File System Access API is supported
      if ('showDirectoryPicker' in window) {
        const dirHandle = await (window as any).showDirectoryPicker()
        const folderPath = dirHandle.name // This gives us the folder name

        // For a full path, we'd need to traverse up, but browsers don't expose full paths for security
        // So we'll use the name as both path and name, user can edit the path
        setPath(folderPath)
        setName(extractFolderName(folderPath))
      } else {
        setError('Folder picker not supported in this browser. Please enter the path manually.')
      }
    } catch (err: any) {
      // User cancelled or error occurred
      if (err.name !== 'AbortError') {
        console.error('Error selecting folder:', err)
      }
    }
  }

  // Auto-extract name when path changes
  function handlePathChange(newPath: string) {
    setPath(newPath)
    // Only auto-fill name if it's empty or matches the previous path's extracted name
    if (!name || name === extractFolderName(path)) {
      setName(extractFolderName(newPath))
    }
  }

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

    // Auto-fill name from path if name is empty
    const finalName = name.trim() || extractFolderName(path)

    if (!finalName || !path.trim()) {
      setError('Folder path is required')
      return
    }

    try {
      setSubmitting(true)
      setError(null)
      setSuccess(null)

      await api.post('/folders/', { name: finalName, path })

      setName('')
      setPath('')
      setSuccess('Folder "' + finalName + '" added successfully!')

      await load()
    } catch (err: any) {
      setError(err.response?.data?.error || 'Failed to create folder')
    } finally {
      setSubmitting(false)
    }
  }

  function remove(folder: Folder) {
    setFolderToDelete(folder)
    setDeleteModalOpen(true)
  }

  async function confirmDelete() {
    if (!folderToDelete) return

    try {
      setSubmitting(true)
      setError(null)
      setSuccess(null)

      await api.delete('/folders/' + folderToDelete.id)
      setSuccess('Folder "' + folderToDelete.name + '" deleted successfully!')

      setDeleteModalOpen(false)
      setFolderToDelete(null)

      await load()
    } catch (err: any) {
      setError(err.response?.data?.error || 'Failed to delete folder')
      setDeleteModalOpen(false)
    } finally {
      setSubmitting(false)
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
          <div className="form-group">
            <label className="form-label">Folder Path</label>
            <div style={{ display: 'flex', gap: '0.5rem' }}>
              <input
                type="text"
                className="form-input"
                placeholder="e.g., C:\Users\Alex\Documents"
                value={path}
                onChange={(e) => handlePathChange(e.target.value)}
                disabled={submitting}
                style={{ flex: 1 }}
              />
              <button
                type="button"
                onClick={selectFolder}
                className="btn btn-secondary"
                disabled={submitting}
                title="Browse for folder"
              >
                📁 Browse
              </button>
            </div>
          </div>

          <div className="form-group">
            <label className="form-label">Folder Name <span style={{ fontSize: '0.875rem', fontWeight: 'normal', opacity: 0.7 }}>(optional - auto-filled from path)</span></label>
            <input
              type="text"
              className="form-input"
              placeholder="e.g., Documents"
              value={name}
              onChange={(e) => setName(e.target.value)}
              disabled={submitting}
            />
          </div>

          <button
            type="submit"
            className="btn btn-primary"
            disabled={submitting || !path.trim()}
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

      <Modal
        isOpen={deleteModalOpen}
        title="Delete Folder"
        onClose={() => setDeleteModalOpen(false)}
        onConfirm={confirmDelete}
        confirmText={submitting ? 'Deleting...' : 'Delete'}
        confirmType="danger"
      >
        <p>Are you sure you want to delete the folder <strong>{folderToDelete?.name}</strong>?</p>
        <p className="text-muted" style={{ fontSize: '0.9rem' }}>This will stop monitoring for this folder. No files on disk will be deleted.</p>
      </Modal>
    </div>
  )
}
