// src/components/AgentPanel.jsx
// Displays real-time token output from a specific agent.
import React, { useRef, useEffect } from 'react'

const AGENT_LABELS = {
  planner: { label: '🧠 Planner', color: '#d29922', bg: '#3b2f0e22' },
  validator: { label: '🔍 Validator', color: '#bc8cff', bg: '#2d1f4e22' },
}

function getAgentConfig(agentKey) {
  if (agentKey.startsWith('executor_')) {
    const n = parseInt(agentKey.split('_')[1], 10)
    return { label: `⚙️ Executor — Step ${n + 1}`, color: '#58a6ff', bg: '#1f3a5f22' }
  }
  return AGENT_LABELS[agentKey] || { label: agentKey, color: '#8b949e', bg: '#21262d' }
}

export function AgentPanel({ agentKey, text, isActive }) {
  const cfg = getAgentConfig(agentKey)
  const endRef = useRef(null)

  useEffect(() => {
    if (isActive) endRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [text, isActive])

  if (!text) return null

  return (
    <div style={{
      border: `1px solid ${cfg.color}44`,
      borderRadius: '10px',
      overflow: 'hidden',
      marginBottom: '12px',
      background: cfg.bg,
    }}>
      {/* Header */}
      <div style={{
        padding: '8px 14px',
        borderBottom: `1px solid ${cfg.color}33`,
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'space-between',
        background: `${cfg.color}11`,
      }}>
        <span style={{ color: cfg.color, fontWeight: 600, fontSize: '13px' }}>
          {cfg.label}
        </span>
        {isActive && (
          <span style={{ display: 'flex', gap: '3px', alignItems: 'center' }}>
            {[0,1,2].map(i => (
              <span key={i} style={{
                width: '5px', height: '5px', borderRadius: '50%',
                background: cfg.color,
                animation: `blink 1.2s ${i * 0.2}s infinite`,
              }} />
            ))}
          </span>
        )}
      </div>

      {/* Content */}
      <div style={{
        padding: '12px 14px',
        fontFamily: 'var(--font-mono)',
        fontSize: '12.5px',
        lineHeight: '1.7',
        color: '#c9d1d9',
        whiteSpace: 'pre-wrap',
        wordBreak: 'break-word',
        maxHeight: '320px',
        overflowY: 'auto',
      }}>
        {text}
        {isActive && <span className="cursor" style={{
          display: 'inline-block',
          width: '8px', height: '1.1em',
          background: cfg.color,
          marginLeft: '2px',
          verticalAlign: 'text-bottom',
          animation: 'blink-cursor 0.8s step-end infinite',
        }} />}
        <div ref={endRef} />
      </div>

      <style>{`
        @keyframes blink { 0%,100%{opacity:1} 50%{opacity:0.2} }
        @keyframes blink-cursor { 0%,100%{opacity:1} 50%{opacity:0} }
      `}</style>
    </div>
  )
}
