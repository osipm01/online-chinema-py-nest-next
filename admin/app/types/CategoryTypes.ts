export interface Category {
  id: number;
  name: string;
  poster_url: string;
}

export interface CategoryWithCount extends Category {
  media_count: number;
}

export interface CategoryWithMedia extends Category {
  media: any[]; // Замените any[] на ваш интерфейс Media[], если он есть
}

export interface CreateCategoryDto {
  name: string;
  poster_url: string;
}

export interface UpdateCategoryDto {
  name: string;
}

export interface ValidationErrorDetail {
  loc: (string | number)[];
  msg: string;
  type: string;
  input: string;
  ctx?: Record<string, any>;
}

export interface ValidationError {
  detail: ValidationErrorDetail[];
}
