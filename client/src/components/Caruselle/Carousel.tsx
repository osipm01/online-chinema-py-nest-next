'use client';

import React, { useEffect, useState } from 'react';
import useEmblaCarousel from 'embla-carousel-react';
import { EmblaOptionsType } from 'embla-carousel';
import { useMedia } from '@/hooks/useMedia';
import type { Media } from '@/types/MediaTypes';
import styles from './Carousel.module.scss';

const OPTIONS: EmblaOptionsType = {
  dragFree: true,
  containScroll: 'trimSnaps',
};

export default function Carousel() {
  const mediaService = useMedia();
  const [emblaRef] = useEmblaCarousel(OPTIONS);

  const [items, setItems] = useState<Media[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let cancelled = false;

    (async () => {
      try {
        setLoading(true);
        setError(null);
        const data = await mediaService.getRecent(10);
        if (!cancelled) setItems(data);
      } catch (e) {
        if (!cancelled) {
          setError(e instanceof Error ? e.message : 'Не удалось загрузить');
        }
      } finally {
        if (!cancelled) setLoading(false);
      }
    })();

    return () => {
      cancelled = true;
    };
  }, [mediaService]);

  if (loading) {
    return <div className={styles.state}>Загрузка…</div>;
  }

  if (error) {
    return <div className={styles.state}>Ошибка: {error}</div>;
  }

  if (items.length === 0) {
    return <div className={styles.state}>Пока нет новинок</div>;
  }

  return (
    <div className={styles.carousel} ref={emblaRef}>
      <div className={styles.container}>
        {items.map((item) => (
          <div key={item.id} className={styles.slide}>
            <div className={styles.slideInner}>
              <span className={styles.title}>{item.title}</span>
              {item.description && (
                <p className={styles.description}>{item.description}</p>
              )}
              <span className={styles.type}>
                {item.type === 'movie' ? 'Фильм' : 'Сериал'}
              </span>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
