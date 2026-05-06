// src/components/TaskForm.jsx
import React, { useState } from 'react'

const EXAMPLE_TASKS = [
  "Write a comprehensive blog post about the benefits of remote work for software engineers",
  "Create a Python script that reads a CSV file, calculates statistics, and generates a summary report",
  "Plan a 7-day study schedule to learn machine learning fundamentals from scratch",
  "Draft a professional README.md for a FastAPI REST API project with authentication",
]

export function TaskForm({ onSubmit, loading, models = ['mistral', 'llama3', 'codellama'] }) {
  const [title, setTitle] = useState('')
  const [description, setDescription] = useState('')
  const [model, setModel] = useState('mistral')

  function handleSubmit(e) {
    e.preventDefault()
    if (!title.trim() || !description.trim()) return
    onSubmit({ title: title.trim(), description: description.trim(), model })
  }

  function useExample(ex) {
    const words = ex.split(' ').slice(0, 5).join(' ')
    setTitle(words + '...')
    setDescription(ex)
  }

  return (
    <div style={{
      background: 'var(--bg-1)',
      border: '1px solid var(--border)',
      borderRadius: 'var(--radius-lg)',
      padding: '24px',
    }}>
      <h2 style={{ fontSize: '16px', fontWeight: 600, marginBottom: '4px' }}>
        New Task
      </h2>
      <p style={{ color: 'var(--text-secondary)', fontSize: '13px', marginBottom: '20px' }}>
        Describe your task in natural language. The AI pipeline will plan, execute, and validate it.
      </p>

      {/* Example prompts */}
      <div style={{ marginBottom: '20px' }}>
        <p style={{ fontSize: '12px', color: 'var(--text-muted)', marginBottom: '8px', textTransform: 'uppercase', letterSpacing: '0.05em' }}>
          Quick examples
        </p>
        <div style={{ display: 'flex', flexWrap: 'wrap', gap: '6px' }}>
          {EXAMPLE_TASKS.map((ex, i) => (
            <button
              key={i}
              onClick={() => useExample(ex)}
              style={{
                background: 'var(--bg-2)',
                border: '1px solid var(--border)',
                borderRadius: '6px',
                padding: '4px 10px',
                fontSize: '12px',
                color: 'var(--text-secondary)',
                cursor: 'pointer',
                transition: 'var(--transition)',
              }}
              onMouseEnter={e => { e.target.style.borderColor = 'var(--accent)'; e.target.style.color = 'var(--accent)' }}
              onMouseLeave={e => { e.target.style.borderColor = 'var(--border)'; e.target.style.color = 'var(--text-secondary)' }}
            >
              {ex.slice(0, 40)}…
            </button>
          ))}
        </div>
      </div>

      <form onSubmit={handleSubmit} style={{ display: 'flex', flexDirection: 'column', gap: '14px' }}>
        {/* Title */}
        <div>
          <label style={labelStyle}>Task Title</label>
          <input
            value={title}
            onChange={e => setTitle(e.target.value)}
            placeholder="Short, descriptive title"
            required
            style={inputStyle}
            onFocus={e => e.target.style.borderColor = 'var(--accent)'}
            onBlur={e => e.target.style.borderColor = 'var(--border)'}
          />
        </div>

        {/* Description */}
        <div>
          <label style={labelStyle}>Task Description</label>
          <textarea
            value={description}
            onChange={e => setDescription(e.target.value)}
            placeholder="Describe your task in detail. The more context, the better the result."
            required
            rows={5}
            style={{ ...inputStyle, resize: 'vertical', minHeight: '100px', fontFamily: 'var(--font)' }}
            onFocus={e => e.target.style.borderColor = 'var(--accent)'}
            onBlur={e => e.target.style.borderColor = 'var(--border)'}
          />
        </div>

        {/* Model selector */}
        <div>
          <label style={labelStyle}>Model</label>
          <select
            value={model}
            onChange={e => setModel(e.target.value)}
            style={{ ...inputStyle, cursor: 'pointer' }}
          >
            {models.map(m => (
              <option key={m} value={m}>{m}</option>
            ))}
          </select>
        </div>

        <button
          type="submit"
          disabled={loading || !title.trim() || !description.trim()}
          style={{
            background: loading ? 'var(--bg-3)' : 'var(--accent)',
            color: loading ? 'var(--text-muted)' : '#0d1117',
            border: 'none',
            borderRadius: 'var(--radius-sm)',
            padding: '11px 20px',
            fontSize: '14px',
            fontWeight: 600,
            cursor: loading ? 'not-allowed' : 'pointer',
            transition: 'var(--transition)',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            gap: '8px',
          }}
        >
          {loading ? (
            <>
              <span style={{ width: '14px', height: '14px', border: '2px solid var(--text-muted)', borderTopColor: 'var(--accent)', borderRadius: '50%', animation: 'spin 0.6s linear infinite', display: 'inline-block' }} />
              Launching pipeline…
            </>
          ) : '🚀 Run Task Pipeline'}
        </button>
      </form>
      <style>{`@keyframes spin { to { transform: rotate(360deg); } }`}</style>
    </div>
  )
}

const labelStyle = {
  display: 'block',
  fontSize: '12px',
  fontWeight: 500,
  color: 'var(--text-secondary)',
  marginBottom: '6px',
  textTransform: 'uppercase',
  letterSpacing: '0.04em',
}

const inputStyle = {
  width: '100%',
  background: 'var(--bg-2)',
  border: '1px solid var(--border)',
  borderRadius: 'var(--radius-sm)',
  padding: '9px 12px',
  color: 'var(--text-primary)',
  fontSize: '14px',
  outline: 'none',
  transition: 'border-color var(--transition)',
  fontFamily: 'var(--font)',
}
