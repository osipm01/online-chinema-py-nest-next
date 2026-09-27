export interface Category {
  id: number
  name: string
  description?: string | null
}

export interface CategoryWithCount extends Category {
  mediaCount: number
}

export interface CategoryWithMedia extends Category {
  media: Array<{ id: number; url: string; type: string }>
}

export type TokenGetter = () => string | null
