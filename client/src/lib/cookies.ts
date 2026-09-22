// lib/cookies.ts
import { cookies } from 'next/headers'
import type { NextResponse } from 'next/server'

export const ACCESS_COOKIE = 'access_token'
export const REFRESH_COOKIE = 'refresh_token'

const ACCESS_MAX_AGE = 60 * 15            // 15 мин
const REFRESH_MAX_AGE = 60 * 60 * 24 * 7  // 7 дней

const isProd = process.env.NODE_ENV === 'production'

const baseCookie = {
  httpOnly: true,
  secure: isProd,
  sameSite: 'lax' as const,
  path: '/',
}

export async function setAuthCookies(
  res: NextResponse,
  accessToken: string,
  refreshToken: string
) {
  res.cookies.set(ACCESS_COOKIE, accessToken, {
    ...baseCookie,
    maxAge: ACCESS_MAX_AGE,
  })
  res.cookies.set(REFRESH_COOKIE, refreshToken, {
    ...baseCookie,
    maxAge: REFRESH_MAX_AGE,
  })
}

export async function clearAuthCookies(res: NextResponse) {
  res.cookies.set(ACCESS_COOKIE, '', { ...baseCookie, maxAge: 0 })
  res.cookies.set(REFRESH_COOKIE, '', { ...baseCookie, maxAge: 0 })
}

/** Читает cookies на сервере (в Route Handlers / Server Components) */
export async function readAuthCookies() {
  const store = await cookies()
  return {
    accessToken: store.get(ACCESS_COOKIE)?.value ?? null,
    refreshToken: store.get(REFRESH_COOKIE)?.value ?? null,
  }
}
