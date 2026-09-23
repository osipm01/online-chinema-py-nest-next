import type { ComponentPropsWithoutRef, ElementType, ReactNode } from 'react';
import { cx } from './cx';
import styles from './styles/BaseLink.module.scss';

export type LinkVariant = 'nav' | 'text';

type OwnProps<E extends ElementType> = {
  /**
   * Рендерящий компонент. По умолчанию <a>.
   * Для роутера: <BaseLink as={NavLink} to="/movies">Фильмы</BaseLink>
   */
  as?: E;
  /** nav — пилюля для меню; text — обычная ссылка в тексте */
  variant?: LinkVariant;
  /** Текущий пункт меню */
  active?: boolean;
  leftIcon?: ReactNode;
  children?: ReactNode;
};

export type BaseLinkProps<E extends ElementType = 'a'> = OwnProps<E> &
  Omit<ComponentPropsWithoutRef<E>, keyof OwnProps<E>>;

export default function BaseLink<E extends ElementType = 'a'>({
  as,
  variant = 'nav',
  active = false,
  leftIcon,
  className,
  children,
  ...rest
}: BaseLinkProps<E> & { className?: string }) {
  const Component: ElementType = as ?? 'a';

  // Для обычного <a> с внешним адресом — безопасное открытие в новой вкладке
  const extra: Record<string, unknown> = {};
  const href = (rest as { href?: unknown }).href;
  if (
    Component === 'a' &&
    typeof href === 'string' &&
    /^https?:\/\//.test(href) &&
    !(rest as { target?: unknown }).target
  ) {
    extra.target = '_blank';
    extra.rel = 'noopener noreferrer';
  }

  return (
    <Component
      className={cx(styles.link, styles[variant], active && styles.active, className)}
      aria-current={active ? 'page' : undefined}
      {...extra}
      {...rest}
    >
      {leftIcon && <span className={styles.icon}>{leftIcon}</span>}
      {children}
    </Component>
  );
}
