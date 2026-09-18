import { AdminUserService } from '~/services/AdminUserService'

export const useAdminUserService = () => {
  const { getAccessToken } = useAuth()
  const { $fetch } = useNuxtApp() as any;
  return new AdminUserService($fetch, getAccessToken)
}