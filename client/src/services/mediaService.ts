import { BaseApiService } from './baseApiService'
import type {
  Media,
  MediaDetail,
  Season,
  // SeasonWithEpisodes,
  Episode,
} from '@/types/mediaTypes'


export class MediaService extends BaseApiService {
  private readonly base = '/media'

  getMovies(params?: { skip?: number; limit?: number }): Promise<Media[]> {
    return this.request<Media[]>(`${this.base}/movies`, {
      query: { skip: params?.skip ?? 0, limit: params?.limit ?? 100 },
    })
  }

  getTvShows(params?: { skip?: number; limit?: number }): Promise<Media[]> {
    return this.request<Media[]>(`${this.base}/tv-shows`, {
      query: { skip: params?.skip ?? 0, limit: params?.limit ?? 100 },
    })
  }

  getByCategory(categoryId: number): Promise<Media[]> {
    return this.request<Media[]>(`${this.base}/category/${categoryId}`)
  }

  search(query: string, params?: { skip?: number; limit?: number }): Promise<Media[]> {
    return this.request<Media[]>(`${this.base}/search`, {
      query: {
        query,
        skip: params?.skip ?? 0,
        limit: params?.limit ?? 100,
      },
    })
  }

  getRecent(limit = 10): Promise<Media[]> {
    return this.request<Media[]>(`${this.base}/recent`, { query: { limit } })
  }

  getById(mediaId: number): Promise<MediaDetail> {
    return this.request<MediaDetail>(`${this.base}/${mediaId}`)
  }

  // ==================== SEASONS ====================

  getSeasonsByMedia(mediaId: number): Promise<Season[]> {
    return this.request<Season[]>(`${this.base}/${mediaId}/seasons`)
  }

  // ==================== EPISODES ====================

  getEpisode(episodeId: number): Promise<Episode> {
    return this.request<Episode>(`${this.base}/episodes/${episodeId}`)
  }

  getEpisodesBySeason(seasonId: number): Promise<Episode[]> {
    return this.request<Episode[]>(`${this.base}/seasons/${seasonId}/episodes`)
  }

}
