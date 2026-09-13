

interface IUser {
    refreshToken: string
    accessToken: string
    name: string
    email: string
    id: string
}

interface IAuthState {
    user: IUser | null
    isAuthenticated: boolean
}

export const useAuth = () => {
    const authState = useState<IAuthState>('auth', () => ({
        user: null,
        isAuthenticated: true
    }))

    const getAccessToken = () => { return authState.value.user?.accessToken }

    const getSessionFromStorage = (): IUser | null => {
        if (process.client) {
            try {
                const data = localStorage.getItem('auth_session')
                return data ? JSON.parse(data) : null
            } catch (e) {
                console.error('Get error:', e)
                return null
            }
        }
        return null
    }

    const saveSessionToStorage = (userData: IUser) => {
        if (process.client) {
            try {
                localStorage.setItem('auth_session', JSON.stringify(userData))
            } catch (e) {
                console.error('Save error:', e)
            }
        }
    }

    const removeSessionFromStorage = () => {
        if (process.client) {
            try {
                localStorage.removeItem('auth_session')
            } catch (e) {
                console.error('Remove error:', e)
            }
        }
    }

    const setAuth = (userData: IUser) => {
        authState.value.user = userData
        authState.value.isAuthenticated = true
        saveSessionToStorage(userData)
    }

    const logOut = () => {
        authState.value.user = null
        authState.value.isAuthenticated = false
        removeSessionFromStorage()
    }

    const initializeAuth = () => {
        if (process.client) {
            const stored = getSessionFromStorage()
            if (stored) {
                authState.value.user = stored
                authState.value.isAuthenticated = true
            }
        }
    }

    // временная для теста на прод УДАЛИТЬ!!!
    const setAuthTest = () => {
        // authState.value.user = userData
        authState.value.isAuthenticated = true
        // saveSessionToStorage(userData)
    }


    return {
        user: computed(() => authState.value.user),
        isAuthenticated: computed(() => authState.value.isAuthenticated),
        setAuth,
        logOut,
        saveSessionToStorage,
        getSessionFromStorage,
        initializeAuth, // можно экспортировать если нужно
        setAuthTest,
        getAccessToken
    }
}