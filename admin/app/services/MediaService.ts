import type {
  Media,
  MediaDetail,
  CreateMediaDto,
  UpdateMediaDto,
  Season,
  SeasonWithEpisodes,
  CreateSeasonDto,
  UpdateSeasonDto,
  Episode,
  CreateEpisodeDto,
  UpdateEpisodeDto,
} from '../types/MediaTypes'

export type TokenGetter = () => string | null

export class MediaService {
  private $api: typeof $fetch
  private baseUrl = 'http://127.0.0.1:8000'
  private getToken: TokenGetter

  constructor(api: typeof $fetch, getToken: TokenGetter = () => null) {
    this.$api = api
    this.getToken = getToken
  }

  /** Единая точка входа для всех запросов — тут подставляем токен */
  private request<T>(url: string, options: any = {}): Promise<T> {
    const token = this.getToken()

    const headers = new Headers(options.headers || {})
    if (token && !headers.has('Authorization')) {
      headers.set('Authorization', `Bearer ${token}`)
    }

    return this.$api<T>(url, {
      baseURL: this.baseUrl,
      ...options,
      headers,
    })
  }

  // ==================== MEDIA ====================

  async create(data: CreateMediaDto): Promise<Media> {
    return this.request<Media>('/api/media/create', {
      method: 'POST',
      body: data,
    })
  }

  async getMovies(params?: { skip?: number; limit?: number }): Promise<Media[]> {
    return this.request<Media[]>('/api/media/movies', {
      method: 'GET',
      query: {
        skip: params?.skip ?? 0,
        limit: params?.limit ?? 100,
      },
    })
  }

  async getTvShows(params?: { skip?: number; limit?: number }): Promise<Media[]> {
    return this.request<Media[]>('/api/media/tv-shows', {
      method: 'GET',
      query: {
        skip: params?.skip ?? 0,
        limit: params?.limit ?? 100,
      },
    })
  }

  async getByCategory(categoryId: number): Promise<Media[]> {
    return this.request<Media[]>(`/api/media/category/${categoryId}`)
  }

  async search(query: string, params?: { skip?: number; limit?: number }): Promise<Media[]> {
    return this.request<Media[]>('/api/media/search', {
      method: 'GET',
      query: {
        query,
        skip: params?.skip ?? 0,
        limit: params?.limit ?? 100,
      },
    })
  }

  async getRecent(limit = 10): Promise<Media[]> {
    return this.request<Media[]>('/api/media/recent', {
      method: 'GET',
      query: { limit },
    })
  }

  async getById(mediaId: number): Promise<MediaDetail> {
    return this.request<MediaDetail>(`/api/media/${mediaId}`)
  }

  async update(mediaId: number, data: UpdateMediaDto): Promise<Media> {
    return this.request<Media>(`/api/media/${mediaId}`, {
      method: 'PUT',
      body: data,
    })
  }

  async delete(mediaId: number): Promise<void> {
    await this.request<void>(`/api/media/${mediaId}`, { method: 'DELETE' })
  }

  // ==================== SEASONS ====================

  async createSeason(data: CreateSeasonDto): Promise<Season> {
    return this.request<Season>('/api/media/seasons/create', {
      method: 'POST',
      body: data,
    })
  }

  async getSeason(seasonId: number): Promise<SeasonWithEpisodes> {
    return this.request<SeasonWithEpisodes>(`/api/media/seasons/${seasonId}`)
  }

  async updateSeason(seasonId: number, data: UpdateSeasonDto): Promise<Season> {
    return this.request<Season>(`/api/media/seasons/${seasonId}`, {
      method: 'PUT',
      body: data,
    })
  }

  async deleteSeason(seasonId: number): Promise<void> {
    await this.request<void>(`/api/media/seasons/${seasonId}`, { method: 'DELETE' })
  }

  async getSeasonsByMedia(mediaId: number): Promise<Season[]> {
    return this.request<Season[]>(`/api/media/${mediaId}/seasons`)
  }

  // ==================== EPISODES ====================

  async createEpisode(data: CreateEpisodeDto): Promise<Episode> {
    return this.request<Episode>('/api/media/episodes/create', {
      method: 'POST',
      body: data,
    })
  }

  async getEpisode(episodeId: number): Promise<Episode> {
    return this.request<Episode>(`/api/media/episodes/${episodeId}`)
  }

  async updateEpisode(episodeId: number, data: UpdateEpisodeDto): Promise<Episode> {
    return this.request<Episode>(`/api/media/episodes/${episodeId}`, {
      method: 'PUT',
      body: data,
    })
  }

  async deleteEpisode(episodeId: number): Promise<void> {
    await this.request<void>(`/api/media/episodes/${episodeId}`, { method: 'DELETE' })
  }

  async getEpisodesBySeason(seasonId: number): Promise<Episode[]> {
    return this.request<Episode[]>(`/api/media/seasons/${seasonId}/episodes`)
  }

  // ==================== COMPOSITE HELPERS ====================
  // (без изменений — они вызывают публичные методы, токен подставится сам)

  async createMovieWithEpisode(
    media: Omit<CreateMediaDto, 'type'>,
    episode: Omit<CreateEpisodeDto, 'media_id' | 'season_id'>
  ): Promise<{ media: Media; episode: Episode }> {
    const createdMedia = await this.create({ ...media, type: 'movie' })
    const createdEpisode = await this.createEpisode({
      ...episode,
      media_id: createdMedia.id,
      season_id: 0,
    })
    return { media: createdMedia, episode: createdEpisode }
  }

  async createTvShowWithSeason(
    media: Omit<CreateMediaDto, 'type'>,
    season: Omit<CreateSeasonDto, 'media_id'>,
    episodes: Omit<CreateEpisodeDto, 'media_id' | 'season_id'>[]
  ): Promise<{ media: Media; season: Season; episodes: Episode[] }> {
    const createdMedia = await this.create({ ...media, type: 'tv_show' })
    const createdSeason = await this.createSeason({
      ...season,
      media_id: createdMedia.id,
    })
    const createdEpisodes = await Promise.all(
      episodes.map((ep) =>
        this.createEpisode({
          ...ep,
          media_id: createdMedia.id,
          season_id: createdSeason.id,
        })
      )
    )
    return { media: createdMedia, season: createdSeason, episodes: createdEpisodes }
  }

  async addSeasonWithEpisodes(
    mediaId: number,
    season: Omit<CreateSeasonDto, 'media_id'>,
    episodes: Omit<CreateEpisodeDto, 'media_id' | 'season_id'>[]
  ): Promise<{ season: Season; episodes: Episode[] }> {
    const createdSeason = await this.createSeason({ ...season, media_id: mediaId })
    const createdEpisodes = await Promise.all(
      episodes.map((ep) =>
        this.createEpisode({
          ...ep,
          media_id: mediaId,
          season_id: createdSeason.id,
        })
      )
    )
    return { season: createdSeason, episodes: createdEpisodes }
  }
}