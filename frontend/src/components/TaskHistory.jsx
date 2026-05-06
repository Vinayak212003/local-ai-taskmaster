// src/components/TaskHistory.jsx
import React from 'react'
import { StatusBadge } from './StatusBadge'

export function TaskHistory({ tasks, onSelect, onDelete, activeId }) {
  if (!tasks.length) {
    return (
      <div style={{
        background: 'var(--bg-1)',
        border: '1px solid var(--border)',
        borderRadius: 'var(--radius-lg)',
        padding: '32px',
        textAlign: 'center',
        color: 'var(--text-muted)',
      }}>
        <div style={{ fontSize: '32px', marginBottom: '8px' }}>📭</div>
        <p>No tasks yet. Create one to get started.</p>
      </div>
    )
  }

  return (
    <div style={{
      background: 'var(--bg-1)',
      border: '1px solid var(--border)',
      borderRadius: 'var(--radius-lg)',
      overflow: 'hidden',
    }}>
      <div style={{ padding: '14px 20px', borderBottom: '1px solid var(--border)', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <h3 style={{ fontSize: '14px', fontWeight: 600 }}>Task History</h3>
        <span style={{ fontSize: '12px', color: 'var(--text-muted)' }}>{tasks.length} tasks</span>
      </div>

      <div style={{ maxHeight: '520px', overflowY: 'auto' }}>
        {tasks.map((t, i) => (
          <div
            key={t.id}
            onClick={() => onSelect(t)}
            style={{
              padding: '14px 20px',
              borderBottom: i < tasks.length - 1 ? '1px solid var(--border-muted)' : 'none',
              cursor: 'pointer',
              background: activeId === t.id ? 'var(--accent-muted)' : 'transparent',
              borderLeft: activeId === t.id ? '3px solid var(--accent)' : '3px solid transparent',
              transition: 'background var(--transition)',
              display: 'flex',
              alignItems: 'flex-start',
              gap: '12px',
            }}
            onMouseEnter={e => { if (activeId !== t.id) e.currentTarget.style.background = 'var(--bg-2)' }}
            onMouseLeave={e => { if (activeId !== t.id) e.currentTarget.style.background = 'transparent' }}
          >
            <div style={{ flex: 1, minWidth: 0 }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '4px', flexWrap: 'wrap' }}>
                <StatusBadge status={t.status} />
                {t.validation_score != null && (
                  <span style={{ fontSize: '11px', color: t.validation_score >= 70 ? '#3fb950' : '#d29922', fontWeight: 600 }}>
                    {t.validation_score}/100
                  </span>
                )}
              </div>
              <div style={{ fontSize: '13px', fontWeight: 500, color: 'var(--text-primary)', marginBottom: '2px', overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>
                {t.title}
              </div>
              <div style={{ fontSize: '12px', color: 'var(--text-muted)' }}>
                {new Date(t.created_at).toLocaleString()} · {t.model}
                {t.subtasks?.length > 0 && ` · ${t.subtasks.length} subtasks`}
              </div>
            </div>

            <button
              onClick={e => { e.stopPropagation(); onDelete(t.id) }}
              style={{
                background: 'transparent',
                border: 'none',
                color: 'var(--text-muted)',
                cursor: 'pointer',
                padding: '4px 6px',
                borderRadius: 'var(--radius-sm)',
                fontSize: '14px',
                flexShrink: 0,
              }}
              onMouseEnter={e => { e.target.style.background = 'var(--danger-muted)'; e.target.style.color = 'var(--danger)' }}
              onMouseLeave={e => { e.target.style.background = 'transparent'; e.target.style.color = 'var(--text-muted)' }}
              title="Delete task"
            >
              ×
            </button>
          </div>
        ))}
      </div>
    </div>
  )
}
