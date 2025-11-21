import React, { useEffect, useState } from 'react'
import api from '../api'

// References:
// - see docs/13_app_arch.txt §1 Presentation (Admin dashboard)
// - see docs/02_functional_req.txt §1 Admin manages rules
// - see docs/08_ai_behavior_rules.txt (rules semantics and adaptation)

type Rule = {
  id: number
  rule_name: string
  description?: string | null
  severity_level?: string | null
  action_type?: string | null
  adaptive_flag: boolean
}

export default function AIRules() {
  const [rules, setRules] = useState<Rule[]>([])
  const [form, setForm] = useState<Partial<Rule>>({ adaptive_flag: false })

  async function load() {
    const { data } = await api.get<Rule[]>('/ai-rules/')
    setRules(data)
  }

  useEffect(() => { load() }, [])

  async function save() {
    if (form.id) {
      await api.put(`/ai-rules/${form.id}`, form)
    } else {
      await api.post('/ai-rules/', form)
    }
    setForm({ adaptive_flag: false })
    load()
  }

  async function remove(id: number) {
    await api.delete(`/ai-rules/${id}`)
    load()
  }

  return (
    <div style={{ padding: 16 }}>
      <h2>AI Rules</h2>

      <div style={{ display: 'grid', gap: 8, maxWidth: 480 }}>
        <input placeholder="Rule name" value={form.rule_name || ''} onChange={(e) => setForm({ ...form, rule_name: e.target.value })} />
        <input placeholder="Description" value={form.description || ''} onChange={(e) => setForm({ ...form, description: e.target.value })} />
        <select value={form.severity_level || ''} onChange={(e) => setForm({ ...form, severity_level: e.target.value || undefined })}>
          <option value="">severity_level (optional)</option>
          <option>Low</option>
          <option>Medium</option>
          <option>High</option>
          <option>Critical</option>
        </select>
        <input placeholder="Action type (optional)" value={form.action_type || ''} onChange={(e) => setForm({ ...form, action_type: e.target.value })} />
        <label>
          <input type="checkbox" checked={!!form.adaptive_flag} onChange={(e) => setForm({ ...form, adaptive_flag: e.target.checked })} /> Adaptive
        </label>
        <div>
          <button onClick={save}>{form.id ? 'Update' : 'Create'}</button>
          {form.id && <button onClick={() => setForm({ adaptive_flag: false })} style={{ marginLeft: 8 }}>Cancel</button>}
        </div>
      </div>

      <ul>
        {rules.map((r) => (
          <li key={r.id}>
            <strong>{r.rule_name}</strong> — {r.severity_level || 'n/a'} — adaptive: {String(r.adaptive_flag)}
            <button onClick={() => setForm(r)} style={{ marginLeft: 8 }}>Edit</button>
            <button onClick={() => remove(r.id)} style={{ marginLeft: 8 }}>Delete</button>
          </li>
        ))}
      </ul>
    </div>
  )
}
