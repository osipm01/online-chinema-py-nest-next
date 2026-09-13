export default defineNuxtPlugin((nuxtApp) => {
  const { getAccessToken, logOut } = useAuth()

  const api = $fetch.create({
    baseURL: 'http://127.0.0.1:8000',

    onRequest({ options }) {
      const token = getAccessToken()
      if (token) {
        options.headers.set('Authorization', `Bearer ${token}`)
      }
    },

    async onResponseError({ response }) {
      if (response.status === 401) {
        logOut()
        await nuxtApp.runWithContext(() => navigateTo('/auth'))
      }
    },
  })

  return {
    provide: { api },
  }
})