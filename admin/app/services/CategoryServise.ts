import type { 
  Category, 
  CategoryWithCount, 
  CategoryWithMedia, 
  CreateCategoryDto, 
  UpdateCategoryDto 
} from '../types/CategoryTypes';

export class CategoryService {
  private $api: typeof $fetch;
  private baseUrl = 'http://127.0.0.1:8000';

  constructor() {
    this.$api = $fetch;
  }

  /**
   * POST /api/categories/create
   * Создать категорию с проверкой уникальности имени
   */
  async create(data: CreateCategoryDto): Promise<Category> {
    return await this.$api<Category>('/api/categories/create', {
      baseURL: this.baseUrl, // <- Добавляем baseURL сюда
      method: 'POST',
      body: data,
    });
  }

  /**
   * GET /api/categories/
   * Получить список всех категорий
   */
  async getAll(): Promise<Category[]> {
    return await this.$api<Category[]>('/api/categories/', {
      baseURL: this.baseUrl // <- И во все остальные методы
    });
  }

  /**
   * GET /api/categories/with-count
   * Получить категории с количеством привязанных медиа
   */
  async getWithCount(params?: { skip?: number; limit?: number }): Promise<CategoryWithCount[]> {
    return await this.$api<CategoryWithCount[]>('/api/categories/with-count', {
      baseURL: this.baseUrl,
      method: 'GET',
      query: {
        skip: params?.skip ?? 0,
        limit: params?.limit ?? 100,
      },
    });
  }

  /**
   * GET /api/categories/{category_id}
   * Получить категорию по её ID
   */
  async getById(categoryId: number): Promise<Category> {
    return await this.$api<Category>(`/api/categories/${categoryId}`, {
      baseURL: this.baseUrl
    });
  }

  /**
   * PUT /api/categories/{category_id}
   * Обновить информацию о категории
   */
  async update(categoryId: number, data: UpdateCategoryDto): Promise<Category> {
    return await this.$api<Category>(`/api/categories/${categoryId}`, {
      baseURL: this.baseUrl,
      method: 'PUT',
      body: data,
    });
  }

  /**
   * DELETE /api/categories/{category_id}
   * Удалить категорию по ID (Возвращает 204 No Content)
   */
  async delete(categoryId: number): Promise<void> {
    await this.$api<void>(`/api/categories/${categoryId}`, {
      baseURL: this.baseUrl,
      method: 'DELETE',
    });
  }

  /**
   * GET /api/categories/{category_id}/media
   * Получить категорию со списком всех привязанных медиа
   */
  async getMedia(categoryId: number): Promise<CategoryWithMedia> {
    return await this.$api<CategoryWithMedia>(`/api/categories/${categoryId}/media`, {
      baseURL: this.baseUrl
    });
  }

  /**
   * POST /api/categories/{category_id}/media/{media_id}
   * Привязать медиа к категории (Many-to-Many)
   */
  async addMedia(categoryId: number, mediaId: number): Promise<string> {
    return await this.$api<string>(`/api/categories/${categoryId}/media/${mediaId}`, {
      baseURL: this.baseUrl,
      method: 'POST',
    });
  }

  /**
   * DELETE /api/categories/{category_id}/media/{media_id}
   * Отвязать медиа от категории (Many-to-Many)
   */
  async removeMedia(categoryId: number, mediaId: number): Promise<string> {
    return await this.$api<string>(`/api/categories/${categoryId}/media/${mediaId}`, {
      baseURL: this.baseUrl,
      method: 'DELETE',
    });
  }
}
