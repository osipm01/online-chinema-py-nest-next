
// вместо useFetch использовать useApiFetch!!!

export const useApiFetch = <T>(url: string, options: any = {}) => {
  const { $api } = useNuxtApp()
  const key = `api:${url}:${JSON.stringify(options.query ?? {})}`
  return useAsyncData<T>(key, () => $api<T>(url, options), options)
}