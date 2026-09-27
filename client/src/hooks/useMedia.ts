'use client'

import { useMemo } from 'react'
import { MediaService } from '@/services/mediaService'

/**
 * Возвращает инстанс MediaService, привязанный к BFF-прокси.
 * Все запросы идут на /api/proxy/media/..., токен — из httpOnly cookie.
 */
export function useMedia() {
  return useMemo(() => new MediaService(), [])
}
