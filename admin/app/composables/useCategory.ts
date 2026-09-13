import { CategoryService } from '~/services/CategoryServise';

export const useCategory = () => {
  return new CategoryService();
};