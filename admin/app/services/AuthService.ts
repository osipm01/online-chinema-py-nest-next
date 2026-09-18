import type {
  AuthResponse,
  ChangePasswordDto,
  DetailResponse,
  LoginDto,
  RefreshResponse,
  RegisterDto,
  ResetPasswordConfirmDto,
  ResetPasswordDto,
  ResetPasswordResponse,
  IUser,
} from '~/types/AuthTypes'

export class AuthService {
  private $api: typeof $fetch
  private baseUrl: string

  constructor(api: typeof $fetch, baseUrl = 'http://127.0.0.1:9090') {
    this.$api = api
    this.baseUrl = baseUrl
  }

  /** POST /api/auth/register/ */
  async register(data: RegisterDto): Promise<AuthResponse> {
    return await this.$api<AuthResponse>('/api/users/auth/register/', {
      baseURL: this.baseUrl,
      method: 'POST',
      body: data,
    })
  }

  /** POST /api/auth/login/ */
  async login(data: LoginDto): Promise<AuthResponse> {
    return await this.$api<AuthResponse>('/api/users/auth/login/', {
      baseURL: this.baseUrl,
      method: 'POST',
      body: data,
    })
  }

  /** POST /api/auth/refresh/ */
  async refresh(refreshToken: string): Promise<RefreshResponse> {
    return await this.$api<RefreshResponse>('/api/users/auth/refresh/', {
      baseURL: this.baseUrl,
      method: 'POST',
      body: { refresh_token: refreshToken },
    })
  }

  /** POST /api/auth/logout/ */
  async logout(accessToken: string): Promise<DetailResponse> {
    return await this.$api<DetailResponse>('/api/users/auth/logout/', {
      baseURL: this.baseUrl,
      method: 'POST',
      headers: { Authorization: `Bearer ${accessToken}` },
    })
  }

  /** GET /api/auth/me/ */
  async me(accessToken: string): Promise<IUser> {
    return await this.$api<IUser>('/api/users/auth/me/', {
      baseURL: this.baseUrl,
      method: 'GET',
      headers: { Authorization: `Bearer ${accessToken}` },
    })
  }

  /** POST /api/auth/change-password/ */
  async changePassword(accessToken: string, data: ChangePasswordDto): Promise<DetailResponse> {
    return await this.$api<DetailResponse>('/api/users/auth/change-password/', {
      baseURL: this.baseUrl,
      method: 'POST',
      headers: { Authorization: `Bearer ${accessToken}` },
      body: data,
    })
  }

  /** POST /api/auth/reset-password/ */
  async resetPassword(data: ResetPasswordDto): Promise<ResetPasswordResponse> {
    return await this.$api<ResetPasswordResponse>('/api/users/auth/reset-password/', {
      baseURL: this.baseUrl,
      method: 'POST',
      body: data,
    })
  }

  /** POST /api/auth/reset-password/confirm/ */
  async resetPasswordConfirm(data: ResetPasswordConfirmDto): Promise<DetailResponse> {
    return await this.$api<DetailResponse>('/api/users/auth/reset-password/confirm/', {
      baseURL: this.baseUrl,
      method: 'POST',
      body: data,
    })
  }
}