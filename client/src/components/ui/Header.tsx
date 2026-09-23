'use client';

import { useEffect, useState } from 'react';
import Link from 'next/link';
import BaseNav, { NavItem } from './BaseNav';
import { cx } from './cx';
import styles from './styles/Header.module.scss';

// Пункты меню.
// Важно: BaseNav использует activeKey для подсветки.
const NAV_ITEMS: NavItem[] = [
  { key: 'home', label: 'Главная', href: '/' },
  { key: 'movies', label: 'Фильмы', href: '/movies' },
  { key: 'series', label: 'Сериалы', href: '/series' },
  { key: 'collections', label: 'Коллекции', href: '/collections' },
];

// Данные пользователя (пока хардкод)
const MOCK_USER = {
  name: 'Александр',
  initials: 'АС',
  isLoggedIn: true, // Попробуй поменять на false, чтобы увидеть кнопку "Войти"
};

// ==========================================================================
// КОМПОНЕНТ HEADER
// ==========================================================================

export const Header = () => {
  const [isScrolled, setIsScrolled] = useState(false);

  // Эффект для отслеживания скролла
  useEffect(() => {
    const handleScroll = () => {
      // Если прокрутили больше 20px, включаем режим "compact"
      // Это активирует класс .scrolled в SCSS
      setIsScrolled(window.scrollY > 20);
    };

    // Слушаем событие
    window.addEventListener('scroll', handleScroll);

    // Очистка при размонтировании
    return () => window.removeEventListener('scroll', handleScroll);
  }, []);

  return (
    // cx - это твоя утилита для склейки классов (аналог clsx)
    <header className={cx(styles.headerWrapper, isScrolled && styles.scrolled)}>
      <div className={styles.container}>

        {/* --- ЛЕВАЯ ЧАСТЬ --- */}
        <div className={styles.leftSection}>
          <Link href="/" className={styles.logo}>
            Cinema<span>.</span>
          </Link>

          {/*
            Используем BaseNav.
            orientation="horizontal" - для хедера.
            size="sm" - компактный размер.
          */}
          <BaseNav
            items={NAV_ITEMS}
            activeKey="home" // TODO: Заменить на usePathname() из next/navigation
            orientation="horizontal"
            size="sm"
            label="Основная навигация"
          />
        </div>

        {/* --- ПРАВАЯ ЧАСТЬ --- */}
        <div className={styles.rightSection}>
          {MOCK_USER.isLoggedIn ? (
            // Профиль (Заглушка)
            <div className={styles.profileStub}>
              <div className={styles.avatar}>
                {MOCK_USER.initials}
              </div>
              <span className={styles.userName}>
                {MOCK_USER.name}
              </span>
            </div>
          ) : (
            // Кнопка входа
            <button className={styles.loginBtn}>
              Войти
            </button>
          )}
        </div>

      </div>
    </header>
  );
};
