// app/api/auth/logout/route.ts
import { NextResponse } from 'next/server'
import { clearAuthCookies, readAuthCookies } from '@/lib/cookies'

const BACKEND = process.env.NEXT_PUBLIC_API_URL ?? 'http://127.0.0.1:9090'

export async function POST() {
  const { accessToken } = await readAuthCookies()

  // Сообщаем backend'у (не критично, если упадёт)
  if (accessToken) {
    await fetch(`${BACKEND}/api/users/auth/logout/`, {
      method: 'POST',
      headers: { Authorization: `Bearer ${accessToken}` },
      cache: 'no-store',
    }).catch(() => null)
  }

  const res = NextResponse.json({ detail: 'Logged out' })
  await clearAuthCookies(res)
  return res
}
