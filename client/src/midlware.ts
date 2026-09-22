// middleware.ts
import { NextRequest, NextResponse } from 'next/server'
import { ACCESS_COOKIE, REFRESH_COOKIE } from '@/lib/cookies'

const PROTECTED = ['/dashboard', '/profile']
const AUTH_ONLY = ['/login', '/register']

export function middleware(req: NextRequest) {
  const { pathname } = req.nextUrl
  const hasSession =
    req.cookies.has(ACCESS_COOKIE) || req.cookies.has(REFRESH_COOKIE)

  if (PROTECTED.some((p) => pathname.startsWith(p)) && !hasSession) {
    const url = req.nextUrl.clone()
    url.pathname = '/login'
    url.searchParams.set('next', pathname)
    return NextResponse.redirect(url)
  }

  if (AUTH_ONLY.some((p) => pathname.startsWith(p)) && hasSession) {
    const url = req.nextUrl.clone()
    url.pathname = '/dashboard'
    return NextResponse.redirect(url)
  }

  return NextResponse.next()
}

export const config = {
  matcher: ['/dashboard/:path*', '/profile/:path*', '/login', '/register'],
}
