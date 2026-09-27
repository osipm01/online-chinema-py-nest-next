'use client'

import { useMemo } from 'react'
import { CategoryService } from '@/services/сategoryService'

/**
 * Инстанс CategoryService для работы с категориями.
 * Все запросы идут на /api/proxy/categories/...
 */
export function useCategory() {
  return useMemo(() => new CategoryService(), [])
}
