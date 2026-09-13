import { CategoryService } from '~/services/CategoryServise';

export const useCategory = () => {
  const { $api } = useNuxtApp()
  return new CategoryService($api);
};