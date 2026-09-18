import { CategoryService } from '~/services/CategoryServise';

export const useCategory = () => {
  const { $api } = useNuxtApp()
  const { getAccessToken } = useAuth()

  return new CategoryService($api, getAccessToken);
};