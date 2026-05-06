// src/App.jsx — Root application component
import React, { useState, useEffect, useCallback } from 'react'
import { TaskForm } from './components/TaskForm'
import { TaskDetail } from './components/TaskDetail'
import { TaskHistory } from './components/TaskHistory'
import { api } from './utils/api'

export default function App() {
  const [tasks, setTasks] = useState([])
  const [selectedTask, setSelectedTask] = useState(null)
  const [view, setView] = useState('home')  // 'home' | 'detail'
  const [health, setHealth] = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)

  // Load tasks + health on mount
  useEffect(() => {
    loadTasks()
    checkHealth()
  }, [])

  async function checkHealth() {
    try {
      const h = await api.health()
      setHealth(h)
    } catch {
      setHealth({ status: 'offline', ollama_online: false, available_models: [] })
    }
  }

  async function loadTasks() {
    try {
      const data = await api.listTasks()
      setTasks(data.tasks || [])
    } catch (e) {
      console.error('Failed to load tasks:', e)
    }
  }

  const handleCreateTask = useCallback(async (formData) => {
    setLoading(true)
    setError(null)
    try {
      const task = await api.createTask(formData)
      setTasks(prev => [task, ...prev])
      setSelectedTask(task)
      setView('detail')
    } catch (e) {
      setError(e.message)
    } finally {
      setLoading(false)
    }
  }, [])

  const handleSelectTask = useCallback((task) => {
    setSelectedTask(task)
    setView('detail')
  }, [])

  const handleDeleteTask = useCallback(async (taskId) => {
    await api.deleteTask(taskId)
    setTasks(prev => prev.filter(t => t.id !== taskId))
    if (selectedTask?.id === taskId) {
      setSelectedTask(null)
      setView('home')
    }
  }, [selectedTask])

  const handleBack = useCallback(() => {
    setView('home')
    loadTasks()  // refresh list
  }, [])

  const models = health?.available_models?.length
    ? health.available_models
    : ['mistral', 'llama3', 'codellama']

  return (
    <div style={{ minHeight: '100vh', background: 'var(--bg-0)' }}>
      {/* ── Navbar ────────────────────────────────────────────────────────── */}
      <nav style={{
        background: 'var(--bg-1)',
        borderBottom: '1px solid var(--border)',
        padding: '0 24px',
        height: '56px',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'space-between',
        position: 'sticky',
        top: 0,
        zIndex: 100,
      }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
          <span style={{ fontSize: '20px' }}>🤖</span>
          <span style={{ fontWeight: 700, fontSize: '15px', color: 'var(--text-primary)' }}>
            LocalAI TaskMaster
          </span>
          <span style={{ fontSize: '11px', color: 'var(--text-muted)', background: 'var(--bg-2)', padding: '2px 8px', borderRadius: '99px', border: '1px solid var(--border)' }}>
            local-first
          </span>
        </div>

        <div style={{ display: 'flex', alignItems: 'center', gap: '16px' }}>
          {/* Ollama status indicator */}
          <div style={{ display: 'flex', alignItems: 'center', gap: '6px', fontSize: '12px' }}>
            <span style={{
              width: '8px', height: '8px',
              borderRadius: '50%',
              background: health?.ollama_online ? '#3fb950' : '#f85149',
              boxShadow: health?.ollama_online ? '0 0 6px #3fb95088' : '0 0 6px #f8514988',
            }} />
            <span style={{ color: 'var(--text-secondary)' }}>
              Ollama {health?.ollama_online ? 'online' : 'offline'}
            </span>
          </div>

          <button
            onClick={() => { setView('home'); setSelectedTask(null) }}
            style={{
              background: 'var(--bg-2)',
              border: '1px solid var(--border)',
              borderRadius: 'var(--radius-sm)',
              padding: '5px 14px',
              color: 'var(--text-secondary)',
              fontSize: '13px',
              cursor: 'pointer',
              fontFamily: 'var(--font)',
            }}
          >
            + New Task
          </button>
        </div>
      </nav>

      {/* ── Main Layout ───────────────────────────────────────────────────── */}
      <div style={{
        maxWidth: '1200px',
        margin: '0 auto',
        padding: '24px 16px',
        display: 'grid',
        gridTemplateColumns: view === 'detail' ? '1fr 320px' : '600px 1fr',
        gap: '20px',
        alignItems: 'start',
      }}>
        {/* Left column */}
        <div>
          {view === 'home' ? (
            <>
              <TaskForm
                onSubmit={handleCreateTask}
                loading={loading}
                models={models}
              />
              {error && (
                <div style={{ marginTop: '12px', background: 'var(--danger-muted)', border: '1px solid var(--danger)', borderRadius: 'var(--radius-sm)', padding: '10px 16px', color: 'var(--danger)', fontSize: '13px' }}>
                  {error}
                </div>
              )}
              {/* Ollama offline warning */}
              {health && !health.ollama_online && (
                <div style={{ marginTop: '12px', background: 'var(--warning-muted)', border: '1px solid var(--warning)', borderRadius: 'var(--radius-sm)', padding: '12px 16px', fontSize: '13px', color: 'var(--warning)' }}>
                  ⚠️ <strong>Ollama is offline.</strong> Start it first:
                  <code style={{ display: 'block', marginTop: '6px', background: 'var(--bg-3)', padding: '6px 10px', borderRadius: '4px', fontSize: '12px', color: 'var(--text-primary)' }}>
                    ollama serve
                  </code>
                  Then pull a model:
                  <code style={{ display: 'block', marginTop: '4px', background: 'var(--bg-3)', padding: '6px 10px', borderRadius: '4px', fontSize: '12px', color: 'var(--text-primary)' }}>
                    ollama pull mistral
                  </code>
                </div>
              )}
            </>
          ) : (
            <TaskDetail
              task={selectedTask}
              onBack={handleBack}
            />
          )}
        </div>

        {/* Right column — always shows history */}
        <div>
          <TaskHistory
            tasks={tasks}
            onSelect={handleSelectTask}
            onDelete={handleDeleteTask}
            activeId={selectedTask?.id}
          />
        </div>
      </div>
    </div>
  )
}
