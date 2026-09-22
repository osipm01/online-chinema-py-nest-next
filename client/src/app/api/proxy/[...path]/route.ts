// app/api/proxy/[...path]/route.ts
import { NextRequest, NextResponse } from 'next/server'
import { backendFetch } from '@/lib/backendFetch'
import { setAuthCookies } from '@/lib/cookies'

export const dynamic = 'force-dynamic'

async function handler(
  req: NextRequest,
  { params }: { params: Promise<{ path: string[] }> }
) {
  const { path } = await params
  const search = req.nextUrl.search
  const backendPath = `/api/${path.join('/')}${search}`

  const init: RequestInit = { method: req.method }

  if (req.method !== 'GET' && req.method !== 'HEAD') {
    const contentType = req.headers.get('content-type')
    if (contentType) {
      init.headers = { 'Content-Type': contentType }
    }
    init.body = await req.text()
  }

  const { response, newTokens } = await backendFetch(backendPath, init)

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

export { handler as GET, handler as POST, handler as PUT, handler as PATCH, handler as DELETE }
