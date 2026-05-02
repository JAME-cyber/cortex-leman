import { useState, useEffect, useCallback } from 'react'
import { auth } from '../lib/api'

export function useAuth() {
  const [user, setUser] = useState<any>(null)
  const [loading, setLoading] = useState(true)

  const loadUser = useCallback(async () => {
    try {
      const me = await auth.me()
      setUser(me)
    } catch {
      setUser(null)
      localStorage.removeItem('cl_access_token')
    } finally {
      setLoading(false)
    }
  }, [])

  useEffect(() => { loadUser() }, [loadUser])

  const login = async (email: string, password: string) => {
    const res = await auth.login(email, password)
    localStorage.setItem('cl_access_token', res.access_token)
    setUser(res.user)
    return res.user
  }

  const logout = () => {
    localStorage.removeItem('cl_access_token')
    setUser(null)
  }

  return { user, loading, login, logout, refresh: loadUser }
}
