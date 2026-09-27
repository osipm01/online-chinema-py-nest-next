'use client'

import { useCallback, useEffect, useRef, useState } from 'react'

export interface UseAsyncResult<T> {
  data: T | null
  error: Error | null
  loading: boolean
  reload: () => Promise<void>
  setData: (data: T | null) => void
}

/**
 * Обёртка над асинхронной функцией.
 * Пример:
 *   const { data, loading, error } = useAsync(() => media.getRecent(10), [])
 */
export function useAsync<T>(
  fn: () => Promise<T>,
  deps: unknown[] = [],
): UseAsyncResult<T> {
  const [data, setData] = useState<T | null>(null)
  const [error, setError] = useState<Error | null>(null)
  const [loading, setLoading] = useState(true)
  const mounted = useRef(true)

  useEffect(() => {
    mounted.current = true
    return () => {
      mounted.current = false
    }
  }, [])

  const run = useCallback(async () => {
    setLoading(true)
    setError(null)
    try {
      const result = await fn()
      if (mounted.current) setData(result)
    } catch (e) {
      if (mounted.current) setError(e as Error)
    } finally {
      if (mounted.current) setLoading(false)
    }
  }, deps)

  useEffect(() => {
    run()
  }, [run])

  return { data, error, loading, reload: run, setData }
}
