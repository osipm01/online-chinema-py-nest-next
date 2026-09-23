import type { ComponentPropsWithoutRef, ElementType, ReactNode } from 'react';
import { cx } from './cx';
import styles from './styles/BaseNav.module.scss';

export type NavOrientation = 'horizontal' | 'vertical';
export type NavSize = 'sm' | 'md' | 'lg';

export interface NavItem<E extends ElementType = 'a'> {
  /** Уникальный ключ пункта (сравнивается с activeKey) */
  key: string;
  /** Текст пункта */
  label: ReactNode;
  /** Иконка слева */
  icon?: ReactNode;
  /** Адрес */
  href?: string;
  /** Компонент-обёртка для конкретного пункта (например, NavLink) */
  as?: E;
  /** Дополнительные пропсы пункта (to, replace, end и т.п.) */
  linkProps?: Record<string, unknown>;
  /** Отключённый пункт */
  disabled?: boolean;
}

type OwnProps<E extends ElementType> = {
  /** Список пунктов */
  items: NavItem[];
  /** Текущий активный ключ (например, из pathname) */
  activeKey?: string;
  /** Ориентация: горизонтальное меню в шапке или вертикальное в сайдбаре */
  orientation?: NavOrientation;
  /** Размер пилюль */
  size?: NavSize;
  /** Общий `as` для всех пунктов, если не задан в item */
  as?: E;
  /** Обёртка-семантика: nav (по умолчанию) или div */
  asElement?: 'nav' | 'div';
  /** aria-label для навигации (нужно, если несколько <nav> на странице) */
  label?: string;
  className?: string;
};

export type BaseNavProps<E extends ElementType = 'a'> = OwnProps<E> &
  Omit<ComponentPropsWithoutRef<'nav'>, keyof OwnProps<E>>;

export default function BaseNav<E extends ElementType = 'a'>({
  items,
  activeKey,
  orientation = 'horizontal',
  size = 'md',
  as,
  asElement = 'nav',
  label,
  className,
  ...rest
}: BaseNavProps<E>) {
  const Wrapper: ElementType = asElement;

  return (
    <Wrapper
      aria-label={label}
      className={cx(styles.nav, styles[orientation], styles[size], className)}
      {...rest}
    >
      {items.map((item) => {
        const isActive = activeKey === item.key;

        // Отключённый пункт — не кликается, озвучивается как disabled
        if (item.disabled) {
          return (
            <span
              key={item.key}
              className={cx(styles.item, styles.disabled)}
              aria-disabled="true"
            >
              {item.icon && <span className={styles.icon}>{item.icon}</span>}
              {item.label}
            </span>
          );
        }

        const Component: ElementType = item.as ?? as ?? 'a';

        // Для внешних ссылок — безопасное открытие в новой вкладке
        const extra: Record<string, unknown> = {};
        if (
          Component === 'a' &&
          typeof item.href === 'string' &&
          /^https?:\/\//.test(item.href) &&
          !(item.linkProps as { target?: unknown } | undefined)?.target
        ) {
          extra.target = '_blank';
          extra.rel = 'noopener noreferrer';
        }

        return (
          <Component
            key={item.key}
            href={item.href}
            className={cx(styles.item, isActive && styles.active)}
            aria-current={isActive ? 'page' : undefined}
            {...extra}
            {...item.linkProps}
          >
            {item.icon && <span className={styles.icon}>{item.icon}</span>}
            {item.label}
          </Component>
        );
      })}
    </Wrapper>
  );
}
