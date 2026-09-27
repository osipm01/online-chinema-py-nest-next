'use client'

import { useCallback, useEffect, useState } from 'react'
import { useRouter } from 'next/navigation'

export interface AuthUser {
  id: number
  username: string
  // добавь поля, которые возвращает твой бэкенд (например, roles)
}

export interface LoginPayload {
  username: string
  password: string
}

interface UseAuthResult {
  user: AuthUser | null
  isAuthenticated: boolean
  isLoading: boolean
  error: string | null
  login: (payload: LoginPayload) => Promise<void>
  logout: () => Promise<void>
  refresh: () => Promise<void>
}

export function useAuth(): UseAuthResult {
  const router = useRouter()
  const [user, setUser] = useState<AuthUser | null>(null)
  const [isLoading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  /** Загружаем текущего пользователя через BFF */
  const fetchMe = useCallback(async () => {
    try {
      const res = await fetch('/api/proxy/auth/me', {
        credentials: 'include',
        cache: 'no-store',
      })
      if (res.status === 401) {
        setUser(null)
        return
      }
      if (!res.ok) throw new Error(`HTTP ${res.status}`)
      setUser((await res.json()) as AuthUser)
    } catch (e) {
      setUser(null)
    }
  }, [])

  useEffect(() => {
    fetchMe().finally(() => setLoading(false))
  }, [fetchMe])

  const login = useCallback(
    async (payload: LoginPayload) => {
      setError(null)
      setLoading(true)
      try {
        const res = await fetch('/api/auth/login', {
          method: 'POST',
          credentials: 'include',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(payload),
        })
        const data = await res.json().catch(() => null)
        if (!res.ok) {
          throw new Error(data?.detail ?? data?.message ?? 'Login failed')
        }
        await fetchMe()
        router.refresh()
      } catch (e) {
        setError((e as Error).message)
        throw e
      } finally {
        setLoading(false)
      }
    },
    [fetchMe, router],
  )

  const logout = useCallback(async () => {
    setLoading(true)
    try {
      await fetch('/api/auth/logout', {
        method: 'POST',
        credentials: 'include',
      })
      setUser(null)
      router.refresh()
    } finally {
      setLoading(false)
    }
  }, [router])

  const refresh = useCallback(async () => {
    setLoading(true)
    try {
      await fetch('/api/auth/refresh', {
        method: 'POST',
        credentials: 'include',
      })
      await fetchMe()
    } finally {
      setLoading(false)
    }
  }, [fetchMe])

  return {
    user,
    isAuthenticated: !!user,
    isLoading,
    error,
    login,
    logout,
    refresh,
  }
}
