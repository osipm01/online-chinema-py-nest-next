'use client';

import React from 'react';
import useEmblaCarousel from 'embla-carousel-react';
import { EmblaOptionsType } from 'embla-carousel';
import styles from './Carousel.module.scss';

// dragFree даёт инерционный скролл; loop с ним обычно не нужен
const OPTIONS: EmblaOptionsType = {
  dragFree: true,
  containScroll: 'trimSnaps',
};

export default function Carousel() {
  const [emblaRef] = useEmblaCarousel(OPTIONS);

  const slides = [1, 2, 3, 4, 5, 6, 7, 8];

  return (
    <div className={styles.carousel} ref={emblaRef}>
      <div className={styles.container}>
        {slides.map((index) => (
          <div key={index} className={styles.slide}>
            Слайд {index}
          </div>
        ))}
      </div>
    </div>
  );
}
