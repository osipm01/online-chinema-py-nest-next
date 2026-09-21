// plugins/api.ts
import { $fetch, type FetchContext } from 'ofetch'

export default defineNuxtPlugin((nuxtApp) => {
  const { getAccessToken, getRefreshToken, refresh, logOut } = useAuth()

  let refreshPromise: Promise<string> | null = null

  const api = $fetch.create({
    baseURL: 'http://127.0.0.1:8000',

    onRequest({ options }) {
      const token = getAccessToken()
      if (token) {
        // options.headers может быть Headers | Record | undefined
        const headers = new Headers(options.headers as HeadersInit)
        headers.set('Authorization', `Bearer ${token}`)
        options.headers = headers
      }
    },

    async onResponseError({ request, response, options }: FetchContext) {
      // 1) Не перехватываем сам refresh и login — иначе будет зацикливание
      const url = typeof request === 'string' ? request : request.toString()
      const isAuthEndpoint =
        url.includes('/auth/refresh/') || url.includes('/auth/login/')

      if (response.status !== 401 || isAuthEndpoint) {
        throw response
      }

      // 2) Нет refresh-токена — сразу разлогин
      if (!getRefreshToken()) {
        await logOut()
        await nuxtApp.runWithContext(() => navigateTo('/auth'))
        throw response
      }

      try {
        // 3) single-flight refresh
        if (!refreshPromise) {
          refreshPromise = refresh()
            .then((res) => res.access_token)
            .finally(() => {
              refreshPromise = null
            })
        }

        const newToken = await refreshPromise

        // 4) повторяем исходный запрос с новым токеном
        const headers = new Headers(options.headers as HeadersInit)
        headers.set('Authorization', `Bearer ${newToken}`)

        return await $fetch(request, {
          ...options,
          baseURL: 'http://127.0.0.1:8000',
          headers,
        })
      } catch (e) {
        // refresh не удался → чистим сессию
        await logOut()
        await nuxtApp.runWithContext(() => navigateTo('/auth'))
        throw e
      }
    },
  })

  return {
    provide: { api },
  }
})