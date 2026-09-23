'use client';

import { ThemeProvider as NextThemesProvider } from 'next-themes';
import { ReactNode } from 'react';

export function ThemeProvider({ children }: { children: ReactNode }) {
  return (
    <NextThemesProvider
      attribute="class"          // Указываем, что меняем именно класс
      defaultTheme="dark"        // По умолчанию макет из макета — темный
      value={{
        light: 'light-theme',    // Название класса для светлой темы из SCSS
        dark: 'dark-theme'       // (Опционально) класс для темной темы
      }}
    >
      {children}
    </NextThemesProvider>
  );
}
