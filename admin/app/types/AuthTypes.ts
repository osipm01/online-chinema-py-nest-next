export interface IUser {
  id: number
  username: string
  role: 'ADMIN' | 'USER' | string
}

export interface AuthResponse {
  user: IUser
  access_token: string
  refresh_token: string
  token_type: string
}

export interface RefreshResponse {
  access_token: string
  refresh_token: string
}

export interface LoginDto {
  username: string
  password: string
}

export interface RegisterDto {
  username: string
  password: string
  role: string
}

export interface ChangePasswordDto {
  old_password: string
  new_password: string
}

export interface ResetPasswordDto {
  username: string
}

export interface ResetPasswordConfirmDto {
  token: string
  new_password: string
}

export interface DetailResponse {
  detail: string
}

export interface ResetPasswordResponse {
  detail: string
  reset_token?: string
}