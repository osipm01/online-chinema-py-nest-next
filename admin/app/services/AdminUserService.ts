import type { IUser } from '~/types/AuthTypes'

// --- DTO под UpdateUserSerializer / UserSerializer на бэке ---

export interface AdminCreateUserDto {
  username: string
  password: string
  role?: string          // 'admin' | 'user' | ... (см. RolseEnum)
}

export interface AdminUpdateUserDto {
  username?: string
  password?: string      // write_only, min_length=6
  role?: string
  is_active?: boolean
}

export interface ListUsersParams {
  skip?: number
  limit?: number
}

export type TokenGetter = () => string | null

export class AdminUserService {
  private $api: typeof $fetch
  private baseUrl: string
  private getToken: TokenGetter

  constructor(
    api: typeof $fetch,
    getToken: TokenGetter,
    baseUrl = 'http://127.0.0.1:9090'
  ) {
    this.$api = api
    this.baseUrl = baseUrl
    this.getToken = getToken
  }

  private request<T>(url: string, options: any = {}): Promise<T> {
    const token = this.getToken()
    const headers = new Headers(options.headers || {})
    if (token && !headers.has('Authorization')) {
      headers.set('Authorization', `Bearer ${token}`)
    }
    return this.$api<T>(url, {
      baseURL: this.baseUrl,
      ...options,
      headers,
    })
  }

  // ==================== USERS CRUD ====================

  /**
   * GET /api/users/
   * Список пользователей. Эндпоинт может поддерживать пагинацию
   * (skip/limit) — если нет, параметры просто проигнорируются бэком.
   */
  async getAllUsers(params?: ListUsersParams): Promise<IUser[]> {
    return this.request<IUser[]>('/api/users/', {
      method: 'GET',
      query: {
        skip: params?.skip ?? 0,
        limit: params?.limit ?? 100,
      },
    })
  }

  /** GET /api/users/{id}/ */
  async getUserById(userId: number): Promise<IUser> {
    return this.request<IUser>(`/api/users/${userId}/`, {
      method: 'GET',
    })
  }

  /** POST /api/users/ — создать пользователя */
  async createUser(data: AdminCreateUserDto): Promise<IUser> {
    return this.request<IUser>('/api/users/', {
      method: 'POST',
      body: data,
    })
  }

  /** PUT /api/users/{id}/ — полное обновление */
  async updateUser(userId: number, data: AdminUpdateUserDto): Promise<IUser> {
    return this.request<IUser>(`/api/users/${userId}/`, {
      method: 'PUT',
      body: data,
    })
  }

  /** PATCH /api/users/{id}/ — частичное обновление (удобнее для UI) */
  async patchUser(userId: number, data: AdminUpdateUserDto): Promise<IUser> {
    return this.request<IUser>(`/api/users/${userId}/`, {
      method: 'PATCH',
      body: data,
    })
  }

  /** DELETE /api/users/{id}/ */
  async deleteUser(userId: number): Promise<void> {
    await this.request<void>(`/api/users/${userId}/`, {
      method: 'DELETE',
    })
  }

  // ==================== УДОБНЫЕ ХЕЛПЕРЫ ====================

  /** Заблокировать/разблокировать через PATCH is_active */
  async setActive(userId: number, isActive: boolean): Promise<IUser> {
    return this.patchUser(userId, { is_active: isActive })
  }

  /** Сменить роль через PATCH role */
  async changeRole(userId: number, role: string): Promise<IUser> {
    return this.patchUser(userId, { role })
  }
}