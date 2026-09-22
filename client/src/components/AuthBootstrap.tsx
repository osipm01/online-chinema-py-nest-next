// components/AuthBootstrap.tsx
'use client'

import { useEffect } from 'react'
import { useAuthStore } from '@/store/authStore'
import { getAuthService } from '../services/authServise'

export function AuthBootstrap({ children }: { children: React.ReactNode }) {
  const setUser = useAuthStore((s) => s.setUser)
  const setBootstrapping = useAuthStore((s) => s.setBootstrapping)

  useEffect(() => {
    let cancelled = false
    ;(async () => {
      try {
        const user = await getAuthService().session()
        if (!cancelled) setUser(user)
      } catch {
        if (!cancelled) setUser(null)
      } finally {
        if (!cancelled) setBootstrapping(false)
      }
    })()
    return () => {
      cancelled = true
    }
  }, [setUser, setBootstrapping])

  return <>{children}</>
}
