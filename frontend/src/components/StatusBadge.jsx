// src/components/StatusBadge.jsx
import React from 'react'

const STATUS_CONFIG = {
  pending:    { color: '#8b949e', bg: '#21262d', label: 'Pending',    dot: true },
  planning:   { color: '#d29922', bg: '#3b2f0e', label: 'Planning',   dot: true, pulse: true },
  executing:  { color: '#58a6ff', bg: '#1f3a5f', label: 'Executing',  dot: true, pulse: true },
  validating: { color: '#bc8cff', bg: '#2d1f4e', label: 'Validating', dot: true, pulse: true },
  complete:   { color: '#3fb950', bg: '#1a3826', label: 'Complete',   dot: false },
  failed:     { color: '#f85149', bg: '#3d1a1a', label: 'Failed',     dot: false },
}

export function StatusBadge({ status }) {
  const cfg = STATUS_CONFIG[status] || STATUS_CONFIG.pending

  return (
    <span style={{
      display: 'inline-flex',
      alignItems: 'center',
      gap: '5px',
      padding: '3px 10px',
      borderRadius: '99px',
      background: cfg.bg,
      color: cfg.color,
      fontSize: '12px',
      fontWeight: 500,
      letterSpacing: '0.02em',
      border: `1px solid ${cfg.color}33`,
    }}>
      {cfg.dot && (
        <span style={{
          width: '7px',
          height: '7px',
          borderRadius: '50%',
          background: cfg.color,
          animation: cfg.pulse ? 'pulse 1.4s infinite' : 'none',
          flexShrink: 0,
        }} />
      )}
      {cfg.label}
      <style>{`
        @keyframes pulse {
          0%, 100% { opacity: 1; transform: scale(1); }
          50% { opacity: 0.4; transform: scale(0.8); }
        }
      `}</style>
    </span>
  )
}
