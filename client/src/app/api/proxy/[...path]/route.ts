import { NextRequest, NextResponse } from 'next/server'
import { backendFetch } from '@/lib/backendFetch'
import { setAuthCookies } from '@/lib/cookies'

export const dynamic = 'force-dynamic'

const DEFAULT_BACKEND =
  process.env.NEXT_PUBLIC_API_URL ?? 'http://127.0.0.1:9090'

const ALLOWED_PORTS = new Set(['8000', '9090'])

async function handler(
  req: NextRequest,
  { params }: { params: Promise<{ path: string[] }> }
) {
  const { path } = await params
  const search = req.nextUrl.search
  const backendPath = `/api/${path.join('/')}${search}`

  // --- выбираем целевой бэкенд ---
  const headerUrl = req.headers.get('x-backend-url')
  const headerPort = req.headers.get('x-backend-port')

  let baseUrl = DEFAULT_BACKEND
  if (headerUrl) {
    baseUrl = headerUrl
  } else if (headerPort) {
    if (!ALLOWED_PORTS.has(headerPort)) {
      return NextResponse.json(
        { error: `Backend port ${headerPort} not allowed` },
        { status: 403 }
      )
    }
    const proto = process.env.BACKEND_PROTO ?? 'http'
    const host = process.env.BACKEND_HOST ?? '127.0.0.1'
    baseUrl = `${proto}://${host}:${headerPort}`
  }

  // --- готовим init ---
  const init: RequestInit = { method: req.method }

  if (req.method !== 'GET' && req.method !== 'HEAD') {
    const contentType = req.headers.get('content-type')
    if (contentType) {
      init.headers = { 'Content-Type': contentType }
    }
    init.body = await req.text()
  }

  // --- идём на бэкенд с нужным baseUrl ---
  const { response, newTokens } = await backendFetch(
    backendPath,
    init,
    baseUrl
  )

  const res = new NextResponse(response.body, {
    status: response.status,
    headers: {
      'Content-Type':
        response.headers.get('content-type') ?? 'application/json',
    },
  })

  if (newTokens) {
    await setAuthCookies(res, newTokens.access_token, newTokens.refresh_token)
  }

  return res
}

export {
  handler as GET,
  handler as POST,
  handler as PUT,
  handler as PATCH,
  handler as DELETE,
}
