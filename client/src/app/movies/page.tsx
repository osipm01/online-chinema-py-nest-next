'use client'

import { useEffect, useState } from 'react'
import { useMedia } from '@/hooks/useMedia'
import type { Media } from '@/types/mediaTypes'

export default function Movies() {
  const media = useMedia()
  const [movies, setMovies] = useState<Media[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    let cancelled = false

    async function loadMovies() {
      try {
        setLoading(true)
        setError(null)
        const data = await media.getMovies({ skip: 0, limit: 100 })
        if (!cancelled) setMovies(data)
      } catch (err) {
        if (!cancelled) {
          setError(err instanceof Error ? err.message : 'Не удалось загрузить фильмы')
        }
      } finally {
        if (!cancelled) setLoading(false)
      }
    }

    loadMovies()
    return () => {
      cancelled = true
    }
  }, [media])

  if (loading) {
    return (
      <main className="p-8">
        <h1 className="text-2xl font-bold mb-4">Фильмы</h1>
        <p className="text-gray-500">Загрузка...</p>
      </main>
    )
  }

  if (error) {
    return (
      <main className="p-8">
        <h1 className="text-2xl font-bold mb-4">Фильмы</h1>
        <p className="text-red-500">Ошибка: {error}</p>
      </main>
    )
  }

  if (movies.length === 0) {
    return (
      <main className="p-8">
        <h1 className="text-2xl font-bold mb-4">Фильмы</h1>
        <p className="text-gray-500">Фильмы не найдены</p>
      </main>
    )
  }

  return (
    <main className="p-8">
      <h1 className="text-2xl font-bold mb-6">Фильмы</h1>
      <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-5 gap-6">
        {movies.map((movie) => (
          <article
            key={movie.id}
            className="rounded-lg border border-gray-200 overflow-hidden hover:shadow-lg transition-shadow"
          >
            <div className="aspect-[2/3] bg-gray-100 flex items-center justify-center">
              {/* У Media нет poster_url, поэтому плейсхолдер */}
              <span className="text-gray-400 text-sm">Нет постера</span>
            </div>
            <div className="p-3">
              <h2 className="font-semibold text-sm line-clamp-2" title={movie.title}>
                {movie.title}
              </h2>
              <p className="text-xs text-gray-500 mt-1 line-clamp-3">
                {movie.description}
              </p>
            </div>
          </article>
        ))}
      </div>
    </main>
  )
}
