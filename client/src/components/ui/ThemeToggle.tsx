// components/ThemeToggle/ThemeToggle.tsx
'use client';

import { useTheme } from 'next-themes';
import { useEffect, useState } from 'react';
import { Sun, Moon } from 'lucide-react';
import styles from './ThemeToggle.module.scss';

export function ThemeToggle() {
  const { theme, setTheme } = useTheme();
  const [mounted, setMounted] = useState(false);

  // Предотвращаем ошибку гидратации (SSR)
  useEffect(() => {
    setMounted(true);
  }, []);

  if (!mounted) {
    // Рендерим пустую заглушку той же формы, чтобы шапка не «прыгала» при загрузке
    return <div className={styles.placeholder} />;
  }

  const isLight = theme === 'light';

  return (
    <button
      onClick={() => setTheme(isLight ? 'dark' : 'light')}
      className={styles.toggleBtn}
      aria-label="Переключить тему оформления"
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
