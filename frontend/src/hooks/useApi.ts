import { useState, useEffect, useCallback } from 'react'

const API = import.meta.env.VITE_API_URL || 'http://localhost:8002'

function getToken(): string | null {
  return localStorage.getItem('cl_access_token')
}

async function apiFetch(path: string, options: RequestInit = {}) {
  const token = getToken()
  const headers: Record<string, string> = {
    'Content-Type': 'application/json',
    ...(options.headers as Record<string, string> || {}),
  }
  if (token) headers['Authorization'] = `Bearer ${token}`

  const res = await fetch(`${API}${path}`, { ...options, headers })
  if (res.status === 401) {
    localStorage.removeItem('cl_access_token')
    throw new Error('Session expirée')
  }
  if (!res.ok) {
    const body = await res.json().catch(() => ({}))
    throw new Error(body.detail || `Erreur ${res.status}`)
  }
  return res.json()
}

export function useApi<T>(path: string | null, deps: any[] = []) {
  const [data, setData] = useState<T | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  const refetch = useCallback(() => {
    if (!path) { setLoading(false); return }
    setLoading(true)
    setError(null)
    apiFetch(path)
      .then(d => setData(d))
      .catch(e => setError(e.message))
      .finally(() => setLoading(false))
  }, [path, ...deps])

  useEffect(() => { refetch() }, [refetch])

  return { data, loading, error, refetch }
}

/** Polling hook — refreshes every `intervalMs` (default 5s) */
export function usePolling<T>(path: string | null, intervalMs = 5000) {
  const [data, setData] = useState<T | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [tick, setTick] = useState(0)

  useEffect(() => {
    if (!path) { setLoading(false); return }
    let cancelled = false
    const fetch_ = () => {
      apiFetch(path)
        .then(d => { if (!cancelled) { setData(d); setLoading(false); setError(null) } })
        .catch(e => { if (!cancelled) { setError(e.message); setLoading(false) } })
    }
    fetch_()
    const id = setInterval(() => { setTick(t => t + 1) }, intervalMs)
    return () => { cancelled = true; clearInterval(id) }
  }, [path, intervalMs])

  // re-fetch on tick
  useEffect(() => {
    if (!path || tick === 0) return
    apiFetch(path)
      .then(d => { setData(d); setError(null) })
      .catch(e => setError(e.message))
  }, [tick, path])

  return { data, loading, error, tick }
}

export { apiFetch }
