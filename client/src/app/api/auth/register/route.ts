// app/api/auth/register/route.ts
import { NextRequest, NextResponse } from 'next/server'
import { setAuthCookies } from '@/lib/cookies'
import type { AuthResponse, RegisterDto } from '@/types/authTypes'

const BACKEND = process.env.NEXT_PUBLIC_API_URL ?? 'http://127.0.0.1:9090'

export async function POST(req: NextRequest) {
  const body = (await req.json()) as RegisterDto

  const backendRes = await fetch(`${BACKEND}/api/users/auth/register/`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(body),
    cache: 'no-store',
  })

  const data = await backendRes.json().catch(() => null)

  if (!backendRes.ok) {
    return NextResponse.json(data ?? { detail: 'Register failed' }, {
      status: backendRes.status,
    })
  }

  const auth = data as AuthResponse
  const res = NextResponse.json({ user: auth.user })
  await setAuthCookies(res, auth.access_token, auth.refresh_token)
  return res
}
