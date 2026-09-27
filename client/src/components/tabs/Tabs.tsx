'use client';

import type { ReactNode } from 'react';
import { cx } from '../ui/cx';
import styles from './Tabs.module.scss';

export interface TabItem {
  key: string;
  label: ReactNode;
  icon?: ReactNode;
  disabled?: boolean;
}

interface TabsProps {
  items: TabItem[];
  activeKey: string;
  onChange: (key: string) => void;
  className?: string;
  'aria-label'?: string;
}

export function Tabs({
  items,
  activeKey,
  onChange,
  className,
  'aria-label': ariaLabel,
}: TabsProps) {
  return (
    <div role="tablist" aria-label={ariaLabel} className={cx(styles.tabs, className)}>
      {items.map((item) => {
        const active = item.key === activeKey;
        return (
          <button
            key={item.key}
            type="button"
            role="tab"
            id={`tab-${item.key}`}
            aria-selected={active}
            aria-controls={`panel-${item.key}`}
            disabled={item.disabled}
            tabIndex={active ? 0 : -1}
            className={cx(
              styles.tab,
              active && styles.active,
              item.disabled && styles.disabled,
            )}
            onClick={() => onChange(item.key)}
          >
            {item.icon && <span className={styles.icon}>{item.icon}</span>}
            <span className={styles.label}>{item.label}</span>
          </button>
        );
      })}
    </div>
  );
}
