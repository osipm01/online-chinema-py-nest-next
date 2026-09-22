export function useAsyncAction<T extends (...args: any[]) => Promise<any>>(
  action: T,
  options?: {
    onSuccess?: () => void
    onError?: (e: any) => void
    toast?: {
      successMessage?: string | (() => string)
      errorMessage?: (e: any) => string
    }
  }
) {
  const isProcessing = ref(false)
  const error = ref<string | null>(null)

  const notify = (
    message: string,
    type: 'success' | 'error'
  ) => {
    useToastify(message, {
      type,
      autoClose: 3000,
      theme: 'auto',
    })
  }

  const execute = async (...args: Parameters<T>) => {
    isProcessing.value = true
    error.value = null
    try {
      const result = await action(...args)

      const successMsg = options?.toast?.successMessage
      if (successMsg) {
        notify(
          typeof successMsg === 'function' ? successMsg() : successMsg,
          'success'
        )
      }

      options?.onSuccess?.()
      return result
    } catch (e: any) {
      error.value = e?.data?.detail || e?.message || 'Произошла ошибка'

      const errorMsg = options?.toast?.errorMessage
      if (errorMsg) {
        notify(errorMsg(e), 'error')
      }

      options?.onError?.(e)
      throw e
    } finally {
      isProcessing.value = false
    }
  }

  return { isProcessing, error, execute }
}