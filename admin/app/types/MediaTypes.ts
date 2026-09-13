export type MediaType = 'movie' | 'tv_show';

// ---------- Media ----------

export interface Media {
  id: number;
  title: string;
  description: string;
  type: MediaType;
}

export interface MediaDetail extends Media {
  categories: unknown[];
  seasons: Season[];
  episodes: Episode[];
}

export interface CreateMediaDto {
  title: string;
  description: string;
  type: MediaType;
  category_ids?: number[];
}

export interface UpdateMediaDto {
  title?: string;
  description?: string;
  type?: MediaType;
  category_ids?: number[];
}

// ---------- Season ----------

export interface Season {
  id: number;
  season_number: number;
  title: string;
  description: string;
  poster_url: string;
  media_id: number;
}

export interface SeasonWithEpisodes extends Season {
  episodes: Episode[];
}

export interface CreateSeasonDto {
  season_number: number;
  title: string;
  description: string;
  poster_url: string;
  media_id: number;
}

export interface UpdateSeasonDto {
  season_number?: number;
  title?: string;
  description?: string;
  poster_url?: string;
}

// ---------- Episode ----------

export interface Episode {
  id: number;
  title: string;
  duration: number;
  hls_link: string;
  poster_url: string;
  season_id: number;
  media_id: number;
}

export interface CreateEpisodeDto {
  title: string;
  duration: number;
  hls_link: string;
  poster_url: string;
  season_id: number;
  media_id: number;
}

export interface UpdateEpisodeDto {
  title?: string;
  duration?: number;
  hls_link?: string;
  poster_url?: string;
  season_id?: number;
  media_id?: number;
}