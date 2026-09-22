// app/api/auth/refresh/route.ts
import { NextResponse } from 'next/server'
import { readAuthCookies, setAuthCookies, clearAuthCookies } from '@/lib/cookies'
import type { RefreshResponse } from '@/types/authTypes'

const BACKEND = process.env.NEXT_PUBLIC_API_URL ?? 'http://127.0.0.1:9090'

export async function POST() {
  const { refreshToken } = await readAuthCookies()

  if (!refreshToken) {
    const res = NextResponse.json({ detail: 'No refresh token' }, { status: 401 })
    await clearAuthCookies(res)
    return res
  }

  const backendRes = await fetch(`${BACKEND}/api/users/auth/refresh/`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ refresh_token: refreshToken }),
    cache: 'no-store',
  })

  const data = await backendRes.json().catch(() => null)

  if (!backendRes.ok) {
    const res = NextResponse.json(data ?? { detail: 'Refresh failed' }, {
      status: backendRes.status,
    })
    await clearAuthCookies(res)
    return res
  }

  const tokens = data as RefreshResponse
  const res = NextResponse.json({ ok: true })
  await setAuthCookies(res, tokens.access_token, tokens.refresh_token)
  return res
}
