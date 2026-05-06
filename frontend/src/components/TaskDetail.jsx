// src/components/TaskDetail.jsx
// Full live pipeline view for an active task.
import React, { useMemo } from 'react'
import ReactMarkdown from 'react-markdown'
import { AgentPanel } from './AgentPanel'
import { StatusBadge } from './StatusBadge'
import { useTaskStream } from '../hooks/useTaskStream'

export function TaskDetail({ task, onBack }) {
  const { tokens, status, result, error, streaming } = useTaskStream(task.id)

  const agentOrder = useMemo(() => {
    const keys = Object.keys(tokens)
    const executors = keys.filter(k => k.startsWith('executor_'))
      .sort((a, b) => parseInt(a.split('_')[1]) - parseInt(b.split('_')[1]))
    return ['planner', ...executors, 'validator'].filter(k => keys.includes(k))
  }, [tokens])

  const currentAgent = status?.status === 'planning' ? 'planner'
    : status?.status === 'validating' ? 'validator'
    : agentOrder[agentOrder.length - 1]

  const score = result?.validation?.score
  const scoreColor = score >= 80 ? '#3fb950' : score >= 60 ? '#d29922' : '#f85149'

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
      {/* Header */}
      <div style={{
        background: 'var(--bg-1)',
        border: '1px solid var(--border)',
        borderRadius: 'var(--radius-lg)',
        padding: '20px 24px',
        display: 'flex',
        alignItems: 'flex-start',
        justifyContent: 'space-between',
        gap: '16px',
      }}>
        <div style={{ flex: 1, minWidth: 0 }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '10px', marginBottom: '6px', flexWrap: 'wrap' }}>
            <button onClick={onBack} style={backBtnStyle}>← Back</button>
            <StatusBadge status={streaming ? (status?.status || 'pending') : (result ? 'complete' : (error ? 'failed' : task.status))} />
          </div>
          <h2 style={{ fontSize: '17px', fontWeight: 600, marginBottom: '4px', wordBreak: 'break-word' }}>
            {task.title}
          </h2>
          <p style={{ color: 'var(--text-secondary)', fontSize: '13px' }}>
            {task.description.slice(0, 200)}{task.description.length > 200 ? '…' : ''}
          </p>
        </div>
        {score !== undefined && (
          <div style={{
            textAlign: 'center',
            padding: '12px 18px',
            background: 'var(--bg-2)',
            borderRadius: 'var(--radius)',
            border: `2px solid ${scoreColor}`,
            flexShrink: 0,
          }}>
            <div style={{ fontSize: '26px', fontWeight: 700, color: scoreColor }}>{score}</div>
            <div style={{ fontSize: '10px', color: 'var(--text-muted)', textTransform: 'uppercase', letterSpacing: '0.05em' }}>Score</div>
          </div>
        )}
      </div>

      {/* Status message */}
      {status && (
        <div style={{
          background: 'var(--bg-2)',
          border: '1px solid var(--border-muted)',
          borderRadius: 'var(--radius-sm)',
          padding: '10px 16px',
          fontSize: '13px',
          color: 'var(--text-secondary)',
          display: 'flex',
          alignItems: 'center',
          gap: '8px',
        }}>
          {streaming && <span style={{ width: '10px', height: '10px', border: '2px solid var(--accent)', borderTopColor: 'transparent', borderRadius: '50%', animation: 'spin 0.7s linear infinite', display: 'inline-block', flexShrink: 0 }} />}
          {status.message}
        </div>
      )}

      {/* Agent panels (live streaming) */}
      {agentOrder.length > 0 && (
        <div>
          <p style={{ fontSize: '12px', color: 'var(--text-muted)', textTransform: 'uppercase', letterSpacing: '0.05em', marginBottom: '10px' }}>
            Live Agent Output
          </p>
          {agentOrder.map(key => (
            <AgentPanel
              key={key}
              agentKey={key}
              text={tokens[key]}
              isActive={streaming && key === currentAgent}
            />
          ))}
        </div>
      )}

      {/* Error */}
      {error && (
        <div style={{ background: 'var(--danger-muted)', border: '1px solid var(--danger)', borderRadius: 'var(--radius)', padding: '16px 20px', color: 'var(--danger)' }}>
          <strong>Pipeline Error</strong>
          <p style={{ marginTop: '6px', fontSize: '13px' }}>{error}</p>
          <p style={{ marginTop: '8px', fontSize: '12px', color: '#f8514988' }}>
            Make sure Ollama is running: <code style={{ background: 'var(--bg-3)', padding: '2px 6px', borderRadius: '4px' }}>ollama serve</code>
          </p>
        </div>
      )}

      {/* Final result */}
      {result && (
        <div style={{
          background: 'var(--bg-1)',
          border: '1px solid var(--success)',
          borderRadius: 'var(--radius-lg)',
          overflow: 'hidden',
        }}>
          <div style={{ background: 'var(--success-muted)', padding: '10px 20px', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <span style={{ color: 'var(--success)', fontWeight: 600, fontSize: '14px' }}>✅ Pipeline Complete</span>
            <div style={{ display: 'flex', gap: '8px', fontSize: '12px', color: 'var(--text-secondary)' }}>
              <span>Quality: <strong style={{ color: 'var(--success)' }}>{result.validation?.quality}</strong></span>
              <span>·</span>
              <span>{result.subtask_count} subtasks</span>
            </div>
          </div>
          <div style={{ padding: '20px 24px' }}>
            <div className="md-content">
              <ReactMarkdown>{result.final_result || ''}</ReactMarkdown>
            </div>
          </div>
          {result.validation?.improvements && (
            <div style={{ padding: '12px 20px', background: 'var(--warning-muted)', borderTop: '1px solid var(--border)' }}>
              <span style={{ fontSize: '12px', color: 'var(--warning)' }}>
                💡 <strong>Suggestions:</strong> {result.validation.improvements}
              </span>
            </div>
          )}
        </div>
      )}

      <style>{`@keyframes spin { to { transform: rotate(360deg); } }`}</style>
    </div>
  )
}

const backBtnStyle = {
  background: 'var(--bg-2)',
  border: '1px solid var(--border)',
  borderRadius: 'var(--radius-sm)',
  padding: '4px 12px',
  color: 'var(--text-secondary)',
  fontSize: '12px',
  cursor: 'pointer',
  fontFamily: 'var(--font)',
}
