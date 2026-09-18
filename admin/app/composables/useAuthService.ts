import { AuthService } from '~/services/AuthService'

export const useAuthService = () => {
  const { $api } = useNuxtApp()
  return new AuthService($api)
}