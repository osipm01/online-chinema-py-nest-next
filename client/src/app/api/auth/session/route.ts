// app/api/auth/session/route.ts
import { NextResponse } from 'next/server'
import { backendFetch } from '@/lib/backendFetch'
import { clearAuthCookies, setAuthCookies } from '@/lib/cookies'

export async function GET() {
  const { response, newTokens } = await backendFetch('/api/users/auth/me/')

  if (!response.ok) {
    const res = NextResponse.json({ user: null }, { status: 200 })
    if (response.status === 401) await clearAuthCookies(res)
    return res
  }

  const user = await response.json()
  const res = NextResponse.json({ user })

  if (newTokens) {
    await setAuthCookies(res, newTokens.access_token, newTokens.refresh_token)
  }
  return res
}
