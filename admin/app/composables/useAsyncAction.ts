export function useAsyncAction<T extends (...args: any[]) => Promise<any>>(
  action: T,
  options?: { onSuccess?: () => void; onError?: (e: any) => void }
) {
  const isProcessing = ref(false)
  const error = ref<string | null>(null)

  const execute = async (...args: Parameters<T>) => {
    isProcessing.value = true
    error.value = null
    try {
      const result = await action(...args)
      options?.onSuccess?.()
      return result
    } catch (e: any) {
      error.value = e?.message || 'Произошла ошибка'
      options?.onError?.(e)
      throw e
    } finally {
      isProcessing.value = false
    }
  }

  return { isProcessing, error, execute }
}