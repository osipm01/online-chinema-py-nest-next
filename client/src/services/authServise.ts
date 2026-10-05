// services/AuthService.ts
import type {
  AuthResponse,
  ChangePasswordDto,
  DetailResponse,
  IUser,
  LoginDto,
  RegisterDto,
  ResetPasswordConfirmDto,
  ResetPasswordDto,
  ResetPasswordResponse,
} from '../types/authTypes'

import { useAuthStore } from '../store/authStore'

export interface LoginResult {
  user: IUser
}

export class HttpError extends Error {
  status: number
  data: unknown

  constructor(status: number, data: unknown) {
    super(
      typeof data === 'object' && data && 'detail' in data
        ? String((data as { detail: unknown }).detail)
        : `HTTP ${status}`
    )
    this.name = 'HttpError'
    this.status = status
    this.data = data
  }
}

interface RequestOptions {
  method?: 'GET' | 'POST' | 'PUT' | 'PATCH' | 'DELETE'
  body?: unknown
  headers?: Record<string, string>
  signal?: AbortSignal
}

export class AuthService {
  private async request<T>(path: string, options: RequestOptions = {}): Promise<T> {
    const { method = 'GET', body, headers = {}, signal } = options

    const finalHeaders: Record<string, string> = {
      Accept: 'application/json',
      ...headers,
    }

    let finalBody: BodyInit | undefined
    if (body !== undefined && body !== null) {
      if (body instanceof FormData) {
        finalBody = body
      } else {
        finalHeaders['Content-Type'] =
          finalHeaders['Content-Type'] ?? 'application/json'
        finalBody = JSON.stringify(body)
      }
    }

    const response = await fetch(path, {
      method,
      headers: finalHeaders,
      body: finalBody,
      signal,
      cache: 'no-store',
      credentials: 'same-origin', // важно: cookies уйдут на сервер
    })

    const text = await response.text()
    let data: unknown = null
    if (text) {
      try {
        data = JSON.parse(text)
      } catch {
        data = text
      }
    }

    if (!response.ok) throw new HttpError(response.status, data)
    return data as T
  }

  async register(data: Omit<RegisterDto, 'role'>): Promise<LoginResult> {
      return this.request<LoginResult>('/api/auth/register', {
        method: 'POST',
        body: { ...data, role: 'user' },
      }).then(this.applyAuth)
    }

  async login(data: LoginDto): Promise<LoginResult> {
      return this.request<LoginResult>('/api/auth/login', {
        method: 'POST',
        body: data,
      }).then(this.applyAuth)
  }

  async logout(): Promise<DetailResponse> {
     try {
       return await this.request<DetailResponse>('/api/auth/logout', { method: 'POST' })
     } finally {
       useAuthStore.getState().clearAuth()
     }
   }

   /** Текущий пользователь. null — если не авторизован */
   async session(): Promise<IUser | null> {
     const data = await this.request<{ user: IUser | null }>('/api/auth/session')
     const { setUser, setBootstrapping } = useAuthStore.getState()
     setUser(data.user)
     setBootstrapping(false)
     return data.user
   }

   /** Кладёт пользователя в стор сразу после логина/регистрации */
  private applyAuth = (result: LoginResult): LoginResult => {
     const { setUser, setBootstrapping } = useAuthStore.getState()
     setUser(result.user)
     setBootstrapping(false)
     return result
   }

  refresh(): Promise<{ ok: true }> {
    return this.request<{ ok: true }>('/api/auth/refresh', { method: 'POST' })
  }

  me(): Promise<IUser> {
    return this.request<IUser>('/api/proxy/users/auth/me')
  }

  changePassword(data: ChangePasswordDto): Promise<DetailResponse> {
    return this.request<DetailResponse>('/api/proxy/users/auth/change-password', {
      method: 'POST',
      body: data,
    })
  }

  resetPassword(data: ResetPasswordDto): Promise<ResetPasswordResponse> {
    return this.request<ResetPasswordResponse>(
      '/api/proxy/users/auth/reset-password',
      { method: 'POST', body: data }
    )
  }

  resetPasswordConfirm(data: ResetPasswordConfirmDto): Promise<DetailResponse> {
    return this.request<DetailResponse>(
      '/api/proxy/users/auth/reset-password/confirm',
      { method: 'POST', body: data }
    )
  }
}

let instance: AuthService | null = null

export function getAuthService(): AuthService {
  if (!instance) instance = new AuthService()
  return instance
}

export function useAuthService(): AuthService {
  return getAuthService()
}
