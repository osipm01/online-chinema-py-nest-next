export class ApiError extends Error {
  constructor(
    message: string,
    public status: number,
    public data?: unknown,
  ) {
    super(message)
    this.name = 'ApiError'
    Object.setPrototypeOf(this, ApiError.prototype) // важно для instanceof при таргете ES5
  }
}

/** Ошибка сети / недоступность сервера / abort */
export class NetworkError extends Error {
  constructor(
    message: string,
    public cause?: unknown,
  ) {
    super(message)
    this.name = 'NetworkError'
    Object.setPrototypeOf(this, NetworkError.prototype)
  }
}

/** Ошибка парсинга ответа */
export class ParseError extends Error {
  constructor(
    message: string,
    public raw?: string,
    public cause?: unknown,
  ) {
    super(message)
    this.name = 'ParseError'
    Object.setPrototypeOf(this, ParseError.prototype)
  }
}

/** Прерванный запрос */
export class RequestAbortedError extends Error {
  constructor(message = 'Request aborted') {
    super(message)
    this.name = 'RequestAbortedError'
    Object.setPrototypeOf(this, RequestAbortedError.prototype)
  }
}

export interface RequestOptions {
  method?: HttpMethod
  body?: unknown
  query?: Record<string, string | number | boolean | undefined | null>
  signal?: AbortSignal
}

export type HttpMethod = 'GET' | 'POST' | 'PUT' | 'PATCH' | 'DELETE'

export interface RequestOptions {
  method?: HttpMethod
  body?: unknown
  query?: Record<string, string | number | boolean | undefined | null>
  signal?: AbortSignal
  /** Полный URL бэкенда (приоритет над backendPort) */
  backendUrl?: string
  /** Порт бэкенда, напр. 8000 */
  backendPort?: number | string
}

export class BaseApiService {
  protected prefix = '/api/proxy'

  protected async request<T>(path: string, options: RequestOptions = {}): Promise<T> {
    const { method = 'GET', body, query, signal, backendUrl, backendPort } = options

    // 1. Валидация входных данных
    let url: URL
    try {
      url = new URL(`${this.prefix}${path}`, window.location.origin)
    } catch (e) {
      throw new ApiError(`Invalid URL: ${this.prefix}${path}`, 0, e)
    }

    if (query) {
      try {
        for (const [k, v] of Object.entries(query)) {
          if (v !== undefined && v !== null) url.searchParams.set(k, String(v))
        }
      } catch (e) {
        throw new ApiError('Failed to build query string', 0, e)
      }
    }

    // 2. Сериализация body
    let serializedBody: string | undefined
    if (body !== undefined) {
      try {
        serializedBody = JSON.stringify(body)
      } catch (e) {
        throw new ApiError('Failed to serialize request body', 0, e)
      }
    }

    // 3. Проверка на уже отменённый сигнал
    if (signal?.aborted) {
      throw new RequestAbortedError()
    }

    // 4. Заголовки: прокидываем целевой бэкенд в прокси
    const headers: Record<string, string> = {}
    if (serializedBody !== undefined) headers['Content-Type'] = 'application/json'
    if (backendUrl) headers['x-backend-url'] = backendUrl
    if (backendPort !== undefined) headers['x-backend-port'] = String(backendPort)

    // 5. Сам запрос
    let res: Response
    try {
      res = await fetch(url.toString(), {
        method,
        credentials: 'include',
        signal,
        headers,
        body: serializedBody,
      })
    } catch (e) {
      if (e instanceof DOMException && e.name === 'AbortError') {
        throw new RequestAbortedError()
      }
      throw new NetworkError(
        e instanceof Error ? e.message : 'Network request failed',
        e,
      )
    }

    // 6. Чтение тела
    let text: string
    try {
      text = await res.text()
    } catch (e) {
      throw new ParseError('Failed to read response body', undefined, e)
    }

    // 7. Парсинг
    let data: unknown = null
    if (text) {
      try {
        data = JSON.parse(text)
      } catch {
        data = text
      }
    }

    // 8. Обработка HTTP-ошибок
    if (!res.ok) {
      const message =
        (isRecord(data) && (data.detail || data.message)) ||
        res.statusText ||
        `Request failed with status ${res.status}`
      throw new ApiError(String(message), res.status, data)
    }

    return data as T
  }
}

function isRecord(v: unknown): v is Record<string, unknown> {
  return typeof v === 'object' && v !== null
}
