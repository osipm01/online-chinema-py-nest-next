import type {
  Category,
  CategoryWithCount,
  CategoryWithMedia,
  CreateCategoryDto,
  UpdateCategoryDto,
} from '../types/CategoryTypes'
import type { TokenGetter } from './MediaService' // или вынесите в отдельный файл

export class CategoryService {
  private $api: typeof $fetch
  private baseUrl = 'http://127.0.0.1:8001' // 👈 свой микросервис
  private getToken: TokenGetter

  constructor(api: typeof $fetch, getToken: TokenGetter = () => null) {
    this.$api = api
    this.getToken = getToken
  }

  private request<T>(url: string, options: any = {}): Promise<T> {
    const token = this.getToken()
    const headers = new Headers(options.headers || {})
    if (token && !headers.has('Authorization')) {
      headers.set('Authorization', `Bearer ${token}`)
    }
    return this.$api<T>(url, { baseURL: this.baseUrl, ...options, headers })
  }

  async create(data: CreateCategoryDto): Promise<Category> {
    return this.request<Category>('/api/categories/create', {
      method: 'POST',
      body: data,
    })
  }

  async getAll(): Promise<Category[]> {
    return this.request<Category[]>('/api/categories/')
  }

  async getWithCount(params?: { skip?: number; limit?: number }): Promise<CategoryWithCount[]> {
    return this.request<CategoryWithCount[]>('/api/categories/with-count', {
      method: 'GET',
      query: {
        skip: params?.skip ?? 0,
        limit: params?.limit ?? 100,
      },
    })
  }

  async getById(categoryId: number): Promise<Category> {
    return this.request<Category>(`/api/categories/${categoryId}`)
  }

  async update(categoryId: number, data: UpdateCategoryDto): Promise<Category> {
    return this.request<Category>(`/api/categories/${categoryId}`, {
      method: 'PUT',
      body: data,
    })
  }

  async delete(categoryId: number): Promise<void> {
    await this.request<void>(`/api/categories/${categoryId}`, { method: 'DELETE' })
  }

  async getMedia(categoryId: number): Promise<CategoryWithMedia> {
    return this.request<CategoryWithMedia>(`/api/categories/${categoryId}/media`)
  }

  async addMedia(categoryId: number, mediaId: number): Promise<string> {
    return this.request<string>(`/api/categories/${categoryId}/media/${mediaId}`, {
      method: 'POST',
    })
  }

  async removeMedia(categoryId: number, mediaId: number): Promise<string> {
    return this.request<string>(`/api/categories/${categoryId}/media/${mediaId}`, {
      method: 'DELETE',
    })
  }
}