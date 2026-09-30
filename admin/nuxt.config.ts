export default defineNuxtConfig({

  devServer: {
    port: 3400 // Укажите нужный порт
  },

  app: {
    baseURL: '/admin/' 
  },

  compatibilityDate: '2025-07-15',
  devtools: { enabled: false },
  ssr: false,
  css: ['~~/assets/css/main.css'],

  modules: ['nuxt-toastify'],
  toastify: {
    position: 'top-right',
    autoClose: 3000,
    theme: 'dark',
  },

  // ✅ Регистрируем все компоненты из ~/components без префикса
  components: [
    {
      path: '~/components',
      pathPrefix: false,
    },
  ],
})