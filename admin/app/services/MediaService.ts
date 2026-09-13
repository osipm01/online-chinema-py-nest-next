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
} from '../types/MediaTypes';

export class MediaService {
  private $api: typeof $fetch;
  private baseUrl = 'http://127.0.0.1:8000';

  constructor(api: typeof $fetch) {
    this.$api = api;
  }

  // ==================== MEDIA ====================

  /**
   * POST /api/media/create
   * Создать новый медиаресурс (фильм или сериал).
   * Можно сразу передать список category_ids для привязки категорий.
   */
  async create(data: CreateMediaDto): Promise<Media> {
    return await this.$api<Media>('/api/media/create', {
      baseURL: this.baseUrl,
      method: 'POST',
      body: data,
    });
  }

  /**
   * GET /api/media/movies
   * Получить список всех фильмов с пагинацией
   */
  async getMovies(params?: { skip?: number; limit?: number }): Promise<Media[]> {
    return await this.$api<Media[]>('/api/media/movies', {
      baseURL: this.baseUrl,
      method: 'GET',
      query: {
        skip: params?.skip ?? 0,
        limit: params?.limit ?? 100,
      },
    });
  }

  /**
   * GET /api/media/tv-shows
   * Получить список всех сериалов с пагинацией
   */
  async getTvShows(params?: { skip?: number; limit?: number }): Promise<Media[]> {
    return await this.$api<Media[]>('/api/media/tv-shows', {
      baseURL: this.baseUrl,
      method: 'GET',
      query: {
        skip: params?.skip ?? 0,
        limit: params?.limit ?? 100,
      },
    });
  }

  /**
   * GET /api/media/category/{category_id}
   * Получить все медиафайлы, привязанные к конкретной категории
   */
  async getByCategory(categoryId: number): Promise<Media[]> {
    return await this.$api<Media[]>(`/api/media/category/${categoryId}`, {
      baseURL: this.baseUrl,
    });
  }

  /**
   * GET /api/media/search
   * Поиск медиа по названию или описанию
   */
  async search(
    query: string,
    params?: { skip?: number; limit?: number }
  ): Promise<Media[]> {
    return await this.$api<Media[]>('/api/media/search', {
      baseURL: this.baseUrl,
      method: 'GET',
      query: {
        query,
        skip: params?.skip ?? 0,
        limit: params?.limit ?? 100,
      },
    });
  }

  /**
   * GET /api/media/recent
   * Получить последние добавленные медиа
   */
  async getRecent(limit = 10): Promise<Media[]> {
    return await this.$api<Media[]>('/api/media/recent', {
      baseURL: this.baseUrl,
      method: 'GET',
      query: { limit },
    });
  }

  /**
   * GET /api/media/{media_id}
   * Получить детальную информацию о медиа по ID.
   * Для фильма вернутся привязанные серии, для сериала — сезоны с сериями внутри.
   */
  async getById(mediaId: number): Promise<MediaDetail> {
    return await this.$api<MediaDetail>(`/api/media/${mediaId}`, {
      baseURL: this.baseUrl,
    });
  }

  /**
   * PUT /api/media/{media_id}
   * Обновить информацию о медиаресурсе
   */
  async update(mediaId: number, data: UpdateMediaDto): Promise<Media> {
    return await this.$api<Media>(`/api/media/${mediaId}`, {
      baseURL: this.baseUrl,
      method: 'PUT',
      body: data,
    });
  }

  /**
   * DELETE /api/media/{media_id}
   * Удалить медиаресурс (Возвращает 204 No Content)
   */
  async delete(mediaId: number): Promise<void> {
    await this.$api<void>(`/api/media/${mediaId}`, {
      baseURL: this.baseUrl,
      method: 'DELETE',
    });
  }

  // ==================== SEASONS ====================

  /**
   * POST /api/media/seasons/create
   * Создать новый сезон для сериала
   */
  async createSeason(data: CreateSeasonDto): Promise<Season> {
    return await this.$api<Season>('/api/media/seasons/create', {
      baseURL: this.baseUrl,
      method: 'POST',
      body: data,
    });
  }

  /**
   * GET /api/media/seasons/{season_id}
   * Получить сезон со всеми эпизодами
   */
  async getSeason(seasonId: number): Promise<SeasonWithEpisodes> {
    return await this.$api<SeasonWithEpisodes>(`/api/media/seasons/${seasonId}`, {
      baseURL: this.baseUrl,
    });
  }

  /**
   * PUT /api/media/seasons/{season_id}
   * Обновить информацию о сезоне
   */
  async updateSeason(seasonId: number, data: UpdateSeasonDto): Promise<Season> {
    return await this.$api<Season>(`/api/media/seasons/${seasonId}`, {
      baseURL: this.baseUrl,
      method: 'PUT',
      body: data,
    });
  }

  /**
   * DELETE /api/media/seasons/{season_id}
   * Удалить сезон (Возвращает 204 No Content)
   */
  async deleteSeason(seasonId: number): Promise<void> {
    await this.$api<void>(`/api/media/seasons/${seasonId}`, {
      baseURL: this.baseUrl,
      method: 'DELETE',
    });
  }

  /**
   * GET /api/media/{media_id}/seasons
   * Получить все сезоны медиаресурса
   */
  async getSeasonsByMedia(mediaId: number): Promise<Season[]> {
    return await this.$api<Season[]>(`/api/media/${mediaId}/seasons`, {
      baseURL: this.baseUrl,
    });
  }

  // ==================== EPISODES ====================

  /**
   * POST /api/media/episodes/create
   * Создать новый эпизод
   */
  async createEpisode(data: CreateEpisodeDto): Promise<Episode> {
    return await this.$api<Episode>('/api/media/episodes/create', {
      baseURL: this.baseUrl,
      method: 'POST',
      body: data,
    });
  }

  /**
   * GET /api/media/episodes/{episode_id}
   * Получить эпизод с информацией о родителях
   */
  async getEpisode(episodeId: number): Promise<Episode> {
    return await this.$api<Episode>(`/api/media/episodes/${episodeId}`, {
      baseURL: this.baseUrl,
    });
  }

  /**
   * PUT /api/media/episodes/{episode_id}
   * Обновить информацию об эпизоде
   */
  async updateEpisode(episodeId: number, data: UpdateEpisodeDto): Promise<Episode> {
    return await this.$api<Episode>(`/api/media/episodes/${episodeId}`, {
      baseURL: this.baseUrl,
      method: 'PUT',
      body: data,
    });
  }

  /**
   * DELETE /api/media/episodes/{episode_id}
   * Удалить эпизод (Возвращает 204 No Content)
   */
  async deleteEpisode(episodeId: number): Promise<void> {
    await this.$api<void>(`/api/media/episodes/${episodeId}`, {
      baseURL: this.baseUrl,
      method: 'DELETE',
    });
  }

  /**
   * GET /api/media/seasons/{season_id}/episodes
   * Получить все эпизоды сезона
   */
  async getEpisodesBySeason(seasonId: number): Promise<Episode[]> {
    return await this.$api<Episode[]>(`/api/media/seasons/${seasonId}/episodes`, {
      baseURL: this.baseUrl,
    });
  }

  // ==================== COMPOSITE HELPERS ====================
  // Инкапсулируют правильный порядок создания сущностей:
  // media → season (для сериала) → episodes

  /**
   * Создать фильм целиком: медиаресурс + один привязанный эпизод.
   *
   * Порядок вызовов:
   *   1. POST /api/media/create          (type = 'movie')
   *   2. POST /api/media/episodes/create (season_id = 0, media_id = созданный)
   */
  async createMovieWithEpisode(
    media: Omit<CreateMediaDto, 'type'>,
    episode: Omit<CreateEpisodeDto, 'media_id' | 'season_id'>
  ): Promise<{ media: Media; episode: Episode }> {
    const createdMedia = await this.create({ ...media, type: 'movie' });

    const createdEpisode = await this.createEpisode({
      ...episode,
      media_id: createdMedia.id,
      season_id: 0, // у фильма сезона нет
    });

    return { media: createdMedia, episode: createdEpisode };
  }

  /**
   * Создать сериал целиком: медиаресурс + сезон + список эпизодов.
   *
   * Порядок вызовов:
   *   1. POST /api/media/create          (type = 'tv_show')
   *   2. POST /api/media/seasons/create  (media_id = созданный)
   *   3. POST /api/media/episodes/create (для каждого эпизода, с season_id и media_id)
   */
  async createTvShowWithSeason(
    media: Omit<CreateMediaDto, 'type'>,
    season: Omit<CreateSeasonDto, 'media_id'>,
    episodes: Omit<CreateEpisodeDto, 'media_id' | 'season_id'>[]
  ): Promise<{ media: Media; season: Season; episodes: Episode[] }> {
    const createdMedia = await this.create({ ...media, type: 'tv_show' });

    const createdSeason = await this.createSeason({
      ...season,
      media_id: createdMedia.id,
    });

    const createdEpisodes = await Promise.all(
      episodes.map((ep) =>
        this.createEpisode({
          ...ep,
          media_id: createdMedia.id,
          season_id: createdSeason.id,
        })
      )
    );

    return {
      media: createdMedia,
      season: createdSeason,
      episodes: createdEpisodes,
    };
  }

  /**
   * Добавить сезон с эпизодами к уже существующему сериалу.
   *
   * Порядок вызовов:
   *   1. POST /api/media/seasons/create  (media_id = существующий)
   *   2. POST /api/media/episodes/create (для каждого эпизода)
   */
  async addSeasonWithEpisodes(
    mediaId: number,
    season: Omit<CreateSeasonDto, 'media_id'>,
    episodes: Omit<CreateEpisodeDto, 'media_id' | 'season_id'>[]
  ): Promise<{ season: Season; episodes: Episode[] }> {
    const createdSeason = await this.createSeason({
      ...season,
      media_id: mediaId,
    });

    const createdEpisodes = await Promise.all(
      episodes.map((ep) =>
        this.createEpisode({
          ...ep,
          media_id: mediaId,
          season_id: createdSeason.id,
        })
      )
    );

    return { season: createdSeason, episodes: createdEpisodes };
  }
}