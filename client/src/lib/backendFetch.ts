// lib/backendFetch.ts
import { cookies } from 'next/headers'
import { ACCESS_COOKIE, REFRESH_COOKIE } from './cookies'

const BACKEND = process.env.NEXT_PUBLIC_API_URL ?? 'http://127.0.0.1:9090'

interface RefreshResult {
  access_token: string
  refresh_token: string
}

/**
 * Делает запрос на backend с access_token из cookie.
 * При 401 пытается обновить токены через /refresh/ и повторяет запрос.
 * Возвращает Response + (возможно) новые токены, которые нужно записать в cookie.
 */
export async function backendFetch(
  path: string,
  init: RequestInit = {}
): Promise<{ response: Response; newTokens: RefreshResult | null }> {
  const store = await cookies()
  let accessToken = store.get(ACCESS_COOKIE)?.value
  const refreshToken = store.get(REFRESH_COOKIE)?.value

  const doFetch = (token?: string) =>
    fetch(`${BACKEND}${path}`, {
      ...init,
      headers: {
        ...(init.headers ?? {}),
        ...(token ? { Authorization: `Bearer ${token}` } : {}),
      },
      cache: 'no-store',
    })

  let response = await doFetch(accessToken ?? undefined)

  // Пробуем refresh при 401
  if (response.status === 401 && refreshToken) {
    const refreshRes = await fetch(`${BACKEND}/api/users/auth/refresh/`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ refresh_token: refreshToken }),
      cache: 'no-store',
    })

    if (refreshRes.ok) {
      const newTokens = (await refreshRes.json()) as RefreshResult
      accessToken = newTokens.access_token
      response = await doFetch(accessToken)
      return { response, newTokens }
    }
  }

  return { response, newTokens: null }
}
