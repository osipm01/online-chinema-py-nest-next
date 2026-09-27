export class ApiError extends Error {
  constructor(
    message: string,
    public status: number,
    public data?: unknown,
  ) {
    super(message)
    this.name = 'ApiError'
  }
}

export type HttpMethod = 'GET' | 'POST' | 'PUT' | 'PATCH' | 'DELETE'

export interface RequestOptions {
  method?: HttpMethod
  body?: unknown
  query?: Record<string, string | number | boolean | undefined | null>
  signal?: AbortSignal
}

export class BaseApiService {
  /** Префикс BFF-прокси, к которому цепляется путь сервиса */
  protected prefix = '/api/proxy'

  protected async request<T>(path: string, options: RequestOptions = {}): Promise<T> {
    const { method = 'GET', body, query, signal } = options

    const url = new URL(`${this.prefix}${path}`, window.location.origin)
    if (query) {
      for (const [k, v] of Object.entries(query)) {
        if (v !== undefined && v !== null) url.searchParams.set(k, String(v))
      }
    }

    const res = await fetch(url.toString(), {
      method,
      credentials: 'include', // ← без этого httpOnly cookie не уйдут на BFF
      signal,
      headers: body !== undefined ? { 'Content-Type': 'application/json' } : undefined,
      body: body !== undefined ? JSON.stringify(body) : undefined,
    })

    const text = await res.text()
    const data = text ? safeParse(text) : null

    if (!res.ok) {
      const message =
        (data as any)?.detail ??
        (data as any)?.message ??
        `Request failed with status ${res.status}`
      throw new ApiError(message, res.status, data)
    }

    return data as T
  }
}

function safeParse(text: string): unknown {
  try {
    return JSON.parse(text)
  } catch {
    return text
  }
}
