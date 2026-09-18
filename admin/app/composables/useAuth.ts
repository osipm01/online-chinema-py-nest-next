import type { AuthResponse, IUser } from '~/types/AuthTypes'

interface IAuthState {
  user: IUser | null
  accessToken: string | null
  refreshToken: string | null
  isAuthenticated: boolean
}

const STORAGE_KEY = 'auth_session'

export const useAuth = () => {
  const authState = useState<IAuthState>('auth', () => ({
    user: null,
    accessToken: null,
    refreshToken: null,
    isAuthenticated: false,
  }))

  const authService = useAuthService()

  const getAccessToken = () => authState.value.accessToken

  const getRefreshToken = () => authState.value.refreshToken

  // ---------- Storage ----------
  const getSessionFromStorage = (): IAuthState | null => {
    if (process.client) {
      try {
        const data = localStorage.getItem(STORAGE_KEY)
        return data ? JSON.parse(data) : null
      } catch (e) {
        console.error('Get session error:', e)
        return null
      }
    }
    return null
  }

  const saveSessionToStorage = (state: IAuthState) => {
    if (process.client) {
      try {
        localStorage.setItem(STORAGE_KEY, JSON.stringify(state))
      } catch (e) {
        console.error('Save session error:', e)
      }
    }
  }

  const removeSessionFromStorage = () => {
    if (process.client) {
      try {
        localStorage.removeItem(STORAGE_KEY)
      } catch (e) {
        console.error('Remove session error:', e)
      }
    }
  }

  // ---------- State helpers ----------
  const applyAuthResponse = (res: AuthResponse) => {
    authState.value.user = res.user
    authState.value.accessToken = res.access_token
    authState.value.refreshToken = res.refresh_token
    authState.value.isAuthenticated = true
    saveSessionToStorage(authState.value)
  }

  const setAuth = (userData: IUser, accessToken: string, refreshToken: string) => {
    authState.value.user = userData
    authState.value.accessToken = accessToken
    authState.value.refreshToken = refreshToken
    authState.value.isAuthenticated = true
    saveSessionToStorage(authState.value)
  }

  const logOut = async () => {
    const token = authState.value.accessToken
    // Пытаемся отозвать токен на бэке, но локально чистим в любом случае
    if (token) {
      try {
        await authService.logout(token)
      } catch (e) {
        console.warn('Logout on server failed:', e)
      }
    }
    authState.value.user = null
    authState.value.accessToken = null
    authState.value.refreshToken = null
    authState.value.isAuthenticated = false
    removeSessionFromStorage()
  }

  // ---------- API actions ----------
  const login = async (username: string, password: string) => {
    const res = await authService.login({ username, password })
    applyAuthResponse(res)
    return res
  }

  const register = async (username: string, password: string, role = 'USER') => {
    const res = await authService.register({ username, password, role })
    applyAuthResponse(res)
    return res
  }

  const refresh = async () => {
    const rt = authState.value.refreshToken
    if (!rt) throw new Error('No refresh token')
    const res = await authService.refresh(rt)
    authState.value.accessToken = res.access_token
    authState.value.refreshToken = res.refresh_token
    saveSessionToStorage(authState.value)
    return res
  }

  const fetchMe = async () => {
    const token = authState.value.accessToken
    if (!token) return null
    const user = await authService.me(token)
    authState.value.user = user
    saveSessionToStorage(authState.value)
    return user
  }

  const initializeAuth = () => {
    if (process.client) {
      const stored = getSessionFromStorage()
      if (stored?.isAuthenticated && stored.accessToken) {
        authState.value = stored
      }
    }
  }

return {
  // state
  user: computed(() => authState.value.user),
  isAuthenticated: computed(() => authState.value.isAuthenticated),

  // 👇 удобные поля пользователя
  userName: computed(() => authState.value.user?.username ?? ''),
  userRole: computed(() => authState.value.user?.role ?? ''),
  userId: computed(() => authState.value.user?.id ?? ''),

  // actions
  login,
  register,
  refresh,
  fetchMe,
  logOut,
  setAuth,
  initializeAuth,
  getAccessToken,
  getRefreshToken,
  // storage
  saveSessionToStorage,
  getSessionFromStorage,
}
}