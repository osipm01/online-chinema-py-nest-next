'use client';

import { useEffect, useState } from 'react';
import Link from 'next/link';
import BaseNav, { NavItem } from './BaseNav';
import { cx } from './cx';
import styles from './styles/Header.module.scss';
import { usePathname } from 'next/navigation';
import {
  useAuthStore,
  selectUser,
  selectIsAuthenticated,
  selectUserName,
} from '@/store/authStore';

const NAV_ITEMS: NavItem[] = [
  { key: 'home', label: 'Главная', href: '/' },
  { key: 'movies', label: 'Фильмы', href: '/movies' },
  { key: 'series', label: 'Сериалы', href: '/series' },
  { key: 'profile', label: 'Профиль', href: '/profile' },
];

const AUTH_ITEM: NavItem[] = [
  { key: 'auth', label: 'Войти', href: '/auth' },
];

// Утилита: получить инициалы из имени пользователя
const getInitials = (name: string) =>
  name
    .split(' ')
    .filter(Boolean)
    .slice(0, 2)
    .map((w) => w[0]?.toUpperCase() ?? '')
    .join('');

export const Header = () => {
  const [isScrolled, setIsScrolled] = useState(false);
  const pathname = usePathname();

  // Данные из стора
  const user = useAuthStore(selectUser);
  const isAuthenticated = useAuthStore(selectIsAuthenticated);
  const userName = useAuthStore(selectUserName);
  const isBootstrapping = useAuthStore((s) => s.isBootstrapping);

  useEffect(() => {
    const handleScroll = () => setIsScrolled(window.scrollY > 20);
    window.addEventListener('scroll', handleScroll);
    return () => window.removeEventListener('scroll', handleScroll);
  }, []);

  return (
    <header className={cx(styles.headerWrapper, isScrolled && styles.scrolled)}>
      <div className={styles.container}>

        {/* --- ЛЕВАЯ ЧАСТЬ --- */}
        <div className={styles.leftSection}>
          <Link href="/" className={styles.logo}>
            Cinema<span>.</span>
          </Link>

          <BaseNav
            items={NAV_ITEMS}
            activeKey={pathname}
            orientation="horizontal"
            size="sm"
            label="Основная навигация"
          />
        </div>

        {/* --- ПРАВАЯ ЧАСТЬ --- */}
        <div className={styles.rightSection}>
          {isBootstrapping ? (
            // Пока не знаем статус — показываем skeleton, чтобы не мигало
            <div className={styles.profileStub} aria-hidden="true">
              <div className={styles.avatar} />
            </div>
          ) : isAuthenticated && user ? (
            <Link href="/profile" className={styles.profileStub}>
              <div className={styles.avatar}>
                {getInitials(userName) || 'U'}
              </div>
              <span className={styles.userName}>{userName}</span>
            </Link>
          ) : (
            // Гостю показываем кнопку "Войти"
            <BaseNav
              items={AUTH_ITEM}
              activeKey={pathname}
              orientation="horizontal"
              size="sm"
              label="Авторизация"
            />
          )}
        </div>
      </div>
    </header>
  );
};
