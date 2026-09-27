'use client';

import { useTheme } from 'next-themes';
import { Sun, Moon } from 'lucide-react';
import styles from './styles/ThemeToggle.module.scss';

export function ThemeToggle() {
  const { resolvedTheme, setTheme } = useTheme();

  // До гидратации next-themes не знает тему — рендерим заглушку
  // той же формы, чтобы шапка не «прыгала» и не было hydration mismatch.
  if (!resolvedTheme) {
    return <div className={styles.placeholder} />;
  }

  const isLight = resolvedTheme === 'light';

  return (
    <button
      type="button"
      onClick={() => setTheme(isLight ? 'dark' : 'light')}
      className={styles.toggleBtn}
      aria-label={isLight ? 'Включить тёмную тему' : 'Включить светлую тему'}
      aria-pressed={isLight}
    >
      <div className={`${styles.iconWrapper} ${isLight ? styles.rotate : ''}`}>
        {isLight ? (
          <Sun size={20} className={styles.iconSun} />
        ) : (
          <Moon size={20} className={styles.iconMoon} />
        )}
      </div>
    </button>
  );
}
