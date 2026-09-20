import { AdminUserService } from '~/services/AdminUserService'

export const useAdminUserService = () => {
  const { getAccessToken } = useAuth()
  const { $api } = useNuxtApp() ;
  return new AdminUserService($api, getAccessToken)
}