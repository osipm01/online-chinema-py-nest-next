import { BaseApiService } from './baseApiService'
import type {
  Category,
  CategoryWithCount,
  CategoryWithMedia,
} from '@/types/CategoryTypes'


export class CategoryService extends BaseApiService {
  private readonly base = '/categories'


  getAll(): Promise<Category[]> {
    return this.request<Category[]>(`${this.base}/`)
  }

  getWithCount(params?: { skip?: number; limit?: number }): Promise<CategoryWithCount[]> {
    return this.request<CategoryWithCount[]>(`${this.base}/with-count`, {
      query: {
        skip: params?.skip ?? 0,
        limit: params?.limit ?? 100,
      },
    })
  }

  getById(categoryId: number): Promise<Category> {
    return this.request<Category>(`${this.base}/${categoryId}`)
  }

  async delete(categoryId: number): Promise<void> {
    await this.request<void>(`${this.base}/${categoryId}`, { method: 'DELETE' })
  }

  getMedia(categoryId: number): Promise<CategoryWithMedia> {
    return this.request<CategoryWithMedia>(`${this.base}/${categoryId}/media`)
  }

  addMedia(categoryId: number, mediaId: number): Promise<string> {
    return this.request<string>(`${this.base}/${categoryId}/media/${mediaId}`, {
      method: 'POST',
    })
  }

  removeMedia(categoryId: number, mediaId: number): Promise<string> {
    return this.request<string>(`${this.base}/${categoryId}/media/${mediaId}`, {
      method: 'DELETE',
    })
  }
}
