// src/hooks/useTaskStream.js
// Manages SSE connection for a task and aggregates stream events.

import { useState, useEffect, useRef, useCallback } from 'react'
import { api } from '../utils/api'

export function useTaskStream(taskId) {
  const [events, setEvents] = useState([])    // all events in order
  const [tokens, setTokens] = useState({})    // agent -> accumulated text
  const [status, setStatus] = useState(null)
  const [result, setResult] = useState(null)
  const [error, setError] = useState(null)
  const [streaming, setStreaming] = useState(false)
  const esRef = useRef(null)

  const reset = useCallback(() => {
    setEvents([])
    setTokens({})
    setStatus(null)
    setResult(null)
    setError(null)
    setStreaming(false)
  }, [])

  const connect = useCallback((id) => {
    if (esRef.current) {
      esRef.current.close()
    }
    reset()
    setStreaming(true)

    const es = api.streamTask(id)
    esRef.current = es

    es.onmessage = (e) => {
      try {
        const event = JSON.parse(e.data)
        const { type, data } = event

        setEvents(prev => [...prev, event])

        if (type === 'status') {
          setStatus(data)
        } else if (type === 'token') {
          const agent = data.agent || 'unknown'
          setTokens(prev => ({
            ...prev,
            [agent]: (prev[agent] || '') + data.token,
          }))
        } else if (type === 'done') {
          setResult(data)
          setStreaming(false)
          es.close()
        } else if (type === 'error') {
          setError(data.error)
          setStreaming(false)
          es.close()
        }
      } catch (err) {
        console.error('SSE parse error', err)
      }
    }

    es.onerror = () => {
      setError('Connection lost. Task may still be running.')
      setStreaming(false)
      es.close()
    }
  }, [reset])

  // Auto-connect when taskId changes
  useEffect(() => {
    if (taskId) connect(taskId)
    return () => {
      if (esRef.current) esRef.current.close()
    }
  }, [taskId, connect])

  return { events, tokens, status, result, error, streaming, connect, reset }
}
