

export default defineNuxtRouteMiddleware((to) => {
    const { isAuthenticated } = useAuth()
    
    // Если пользователь не авторизован
    if (!isAuthenticated.value) {
        // Перенаправляем на логин
        return navigateTo('/auth')
    }
})