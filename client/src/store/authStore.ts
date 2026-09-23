// store/authStore.ts
import { create } from 'zustand'
import { persist, createJSONStorage } from 'zustand/middleware'
import type { IUser } from '../types/authTypes'

export interface IAuthState {
  user: IUser | null
  isAuthenticated: boolean
  isBootstrapping: boolean
}

interface IAuthActions {
  setUser: (user: IUser | null) => void
  setAuthenticated: (v: boolean) => void
  setBootstrapping: (v: boolean) => void
  clearAuth: () => void
}

type AuthStore = IAuthState & IAuthActions

const STORAGE_KEY = 'auth_session'

export const useAuthStore = create<AuthStore>()(
  persist(
    (set) => ({
      user: null,
      isAuthenticated: false,
      isBootstrapping: true,

      setUser: (user) => set({ user, isAuthenticated: !!user }),
      setAuthenticated: (isAuthenticated) => set({ isAuthenticated }),
      setBootstrapping: (isBootstrapping) => set({ isBootstrapping }),

      clearAuth: () =>
        set({ user: null, isAuthenticated: false, isBootstrapping: false }),
    }),
    {
      name: STORAGE_KEY,
      storage: createJSONStorage(() => localStorage),
      partialize: (s) => ({ user: s.user, isAuthenticated: s.isAuthenticated }),
    }
  )
)

export const selectUser = (s: AuthStore) => s.user
export const selectIsAuthenticated = (s: AuthStore) => s.isAuthenticated
export const selectUserName = (s: AuthStore) => s.user?.username ?? ''
export const selectUserRole = (s: AuthStore) => s.user?.role ?? ''
export const selectUserId = (s: AuthStore) => s.user?.id ?? 0
