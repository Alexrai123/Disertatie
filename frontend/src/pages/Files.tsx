import React, { useEffect, useState } from 'react'
import api from '../api'
import { Card, LoadingContainer, Alert, Table, EmptyState, Badge } from '../components'

// References:
// - see docs/13_app_arch.txt §1 Presentation (User interface for file management)
// - see docs/02_functional_req.txt §1, §8 (Users add/remove monitored files)

type FileItem = {
  id: number
  name: string
  path: string
  folder_id: number
  owner_id: number
  created_at?: string
  modified_at?: string
  hash?: string | null
}

type Folder = {
  id: number
  name: string
  path: string
}

type FilesResponse = {
  items: FileItem[]
  total: number
  limit: number
  offset: number
  has_more: boolean
}

type FoldersResponse = {
  items: Folder[]
  total: number
}

export default function Files() {
  const [files, setFiles] = useState<FileItem[]>([])
  const [folders, setFolders] = useState<Folder[]>([])
  const [loading, setLoading] = useState(true)
  const [submitting, setSubmitting] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [success, setSuccess] = useState<string | null>(null)

  const [name, setName] = useState('')
  const [path, setPath] = useState('')
  const [folderId, setFolderId] = useState<number | ''>('')

  async function load() {
    try {
      setLoading(true)
      setError(null)

      const [filesRes, foldersRes] = await Promise.all([
        api.get<FilesResponse>('/files/'),
        api.get<FoldersResponse>('/folders/'),
      ])

      setFiles(filesRes.data.items || filesRes.data as any)
      setFolders(foldersRes.data.items || foldersRes.data as any)
    } catch (err: any) {
      setError(err.response?.data?.error || 'Failed to load data')
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    load()
  }, [])

  async function create(e: React.FormEvent) {
    e.preventDefault()

    if (!name.trim() || !path.trim() || !folderId) {
      setError('All fields are required')
      return
    }

    try {
      setSubmitting(true)
      setError(null)
      setSuccess(null)

      await api.post('/files/', { name, path, folder_id: folderId })

      setName('')
      setPath('')
      setFolderId('')
      setSuccess(`File "${name}" added successfully!`)

      await load()
    } catch (err: any) {
      setError(err.response?.data?.error || 'Failed to create file')
    } finally {
      setSubmitting(false)
    }
  }

  async function remove(file: FileItem) {
    if (!confirm(`Are you sure you want to delete "${file.name}"?`)) {
      return
    }

    try {
      setError(null)
      setSuccess(null)

      await api.delete(`/files/${file.id}`)
      setSuccess(`File "${file.name}" deleted successfully!`)

      await load()
    } catch (err: any) {
      setError(err.response?.data?.error || 'Failed to delete file')
    }
  }

  const getFolderName = (folderId: number) => {
    const folder = folders.find(f => f.id === folderId)
    return folder ? folder.name : `Folder #${folderId}`
  }

  const columns = [
    {
      key: 'name',
      header: 'Name',
      render: (file: FileItem) => <strong>{file.name}</strong>
    },
    {
      key: 'path',
      header: 'Path',
      render: (file: FileItem) => <code style={{ fontSize: '0.875rem' }}>{file.path}</code>
    },
    {
      key: 'folder',
      header: 'Folder',
      render: (file: FileItem) => (
        <Badge type="primary">{getFolderName(file.folder_id)}</Badge>
      )
    },
    {
      key: 'status',
      header: 'Status',
      render: () => <Badge type="success">Monitoring</Badge>
    },
    {
      key: 'actions',
      header: 'Actions',
      render: (file: FileItem) => (
        <button
          onClick={() => remove(file)}
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
        title="📄 Monitored Files"
        actions={
          <Badge type="info">{files.length} file{files.length !== 1 ? 's' : ''}</Badge>
        }
      >
        {error && <Alert type="error" message={error} onClose={() => setError(null)} />}
        {success && <Alert type="success" message={success} onClose={() => setSuccess(null)} />}

        <form onSubmit={create} className="mb-3">
          <div className="grid grid-3 gap-2">
            <div className="form-group">
              <label className="form-label">File Name</label>
              <input
                type="text"
                className="form-input"
                placeholder="e.g., document.txt"
                value={name}
                onChange={(e) => setName(e.target.value)}
                disabled={submitting}
              />
            </div>

            <div className="form-group">
              <label className="form-label">File Path</label>
              <input
                type="text"
                className="form-input"
                placeholder="e.g., C:\Users\Alex\document.txt"
                value={path}
                onChange={(e) => setPath(e.target.value)}
                disabled={submitting}
              />
            </div>

            <div className="form-group">
              <label className="form-label">Parent Folder</label>
              <select
                className="form-select"
                value={folderId}
                onChange={(e) => setFolderId(Number(e.target.value))}
                disabled={submitting || folders.length === 0}
              >
                <option value="">Select folder</option>
                {folders.map((f) => (
                  <option key={f.id} value={f.id}>{f.name}</option>
                ))}
              </select>
            </div>

            <div className="form-group" style={{ display: 'flex', alignItems: 'flex-end' }}>
              <input
                type="file"
                id="file-upload"
                style={{ display: 'none' }}
                onChange={(e) => {
                  const file = e.target.files?.[0];
                  if (file && folderId) {
                    setName(file.name);
                    const selectedFolder = folders.find(f => f.id === folderId);
                    if (selectedFolder) {
                      // Construct path based on OS separators (assuming mostly forward slashes for Docker/Linux/Web)
                      const separator = selectedFolder.path.includes('\\') ? '\\' : '/';
                      const cleanPath = selectedFolder.path.endsWith(separator)
                        ? selectedFolder.path
                        : selectedFolder.path + separator;
                      setPath(cleanPath + file.name);
                    }
                  }
                }}
              />
              <button
                type="button"
                className="btn btn-secondary"
                disabled={!folderId}
                onClick={() => document.getElementById('file-upload')?.click()}
                title={!folderId ? "Select a parent folder first" : "Browse for a file"}
              >
                📂 Browse
              </button>
            </div>
          </div>

          <button
            type="submit"
            className="btn btn-primary"
            disabled={submitting || !name.trim() || !path.trim() || !folderId}
          >
            {submitting ? 'Adding...' : '+ Add File'}
          </button>

          {folders.length === 0 && (
            <p className="text-warning mt-2">
              ⚠️ Please create a folder first before adding files
            </p>
          )}
        </form>

        {loading ? (
          <LoadingContainer message="Loading files..." />
        ) : files.length === 0 ? (
          <EmptyState
            icon="📄"
            title="No files yet"
            message="Add files to monitor their changes in real-time"
          />
        ) : (
          <Table
            columns={columns}
            data={files}
            loading={false}
          />
        )}
      </Card>
    </div>
  )
}
