'use client'

import { useEffect, useState } from 'react'
import { useMedia } from '@/hooks/useMedia'
import type { Media } from '@/types/mediaTypes'

export default function Home() {
  const media = useMedia()
  const [tvShows, setTvShows] = useState<Media[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    let cancelled = false

    async function loadTvShows() {
      try {
        setLoading(true)
        setError(null)
        const data = await media.getTvShows({ skip: 0, limit: 100 })
        if (!cancelled) setTvShows(data)
      } catch (err) {
        if (!cancelled) {
          setError(err instanceof Error ? err.message : 'Не удалось загрузить сериалы')
        }
      } finally {
        if (!cancelled) setLoading(false)
      }
    }

    loadTvShows()
    return () => {
      cancelled = true
    }
  }, [media])

  return (
    <div className="py-20 px-20">
      <h1 className="text-2xl font-bold mb-6">Сериалы</h1>

      {loading && <p className="text-gray-500">Загрузка...</p>}

      {error && <p className="text-red-500">Ошибка: {error}</p>}

      {!loading && !error && tvShows.length === 0 && (
        <p className="text-gray-500">Сериалы не найдены</p>
      )}

      {!loading && !error && tvShows.length > 0 && (
        <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-5 gap-6">
          {tvShows.map((show) => (
            <article
              key={show.id}
              className="rounded-lg border border-gray-200 overflow-hidden hover:shadow-lg transition-shadow"
            >
              <div className="aspect-[2/3] bg-gray-100 flex items-center justify-center">
                {/* У Media нет poster_url, поэтому плейсхолдер */}
                <span className="text-gray-400 text-sm">Нет постера</span>
              </div>
              <div className="p-3">
                <h2 className="font-semibold text-sm line-clamp-2" title={show.title}>
                  {show.title}
                </h2>
                <p className="text-xs text-gray-500 mt-1 line-clamp-3">
                  {show.description}
                </p>
              </div>
            </article>
          ))}
        </div>
      )}
    </div>
  )
}
