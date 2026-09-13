export default defineNuxtConfig({
  compatibilityDate: '2025-07-15',
  devtools: { enabled: true },
  ssr: false,
  css: ['~~/assets/css/main.css'],
  modules: ['nuxt-toastify'], 
  toastify: {
    position: 'top-right', // Доступно: 'top-right', 'top-center', 'top-left'
    autoClose: 3000,
    theme: 'dark'          // Можно изменить на 'light' или 'colored'
  }
})
