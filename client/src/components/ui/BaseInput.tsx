import { forwardRef, useId } from 'react';
import type { InputHTMLAttributes, ReactNode } from 'react';
import { cx } from './cx';
import styles from './styles/BaseInput.module.scss';

export type InputSize = 'sm' | 'md' | 'lg';

export interface BaseInputProps
  extends Omit<InputHTMLAttributes<HTMLInputElement>, 'size'> {
  size?: InputSize;
  /** Подпись над полем. Если не нужна — передайте aria-label */
  label?: string;
  /** Иконка слева (например, лупа поиска) */
  leftIcon?: ReactNode;
  /** Элемент справа (иконка или кнопка очистки) */
  rightSlot?: ReactNode;
  /** Полностью скруглённая форма, как в поиске в шапке */
  pill?: boolean;
  /** Текст ошибки: подсвечивает поле и озвучивается скринридером */
  error?: string;
  /** Подсказка под полем */
  hint?: string;
  fullWidth?: boolean;
  /** Класс для внешней обёртки (className уходит на сам <input>) */
  wrapperClassName?: string;
}

const BaseInput = forwardRef<HTMLInputElement, BaseInputProps>(function BaseInput(
  {
    size = 'md',
    label,
    leftIcon,
    rightSlot,
    pill = false,
    error,
    hint,
    fullWidth = false,
    disabled,
    id,
    className,
    wrapperClassName,
    ...rest
  },
  ref,
) {
  const autoId = useId();
  const inputId = id ?? autoId;
  const helpId = error || hint ? `${inputId}-help` : undefined;

  return (
    <div className={cx(styles.field, fullWidth && styles.fullWidth, wrapperClassName)}>
      {label && (
        <label htmlFor={inputId} className={styles.label}>
          {label}
        </label>
      )}

      <div
        className={cx(
          styles.control,
          styles[size],
          pill && styles.pill,
          error && styles.hasError,
          disabled && styles.disabled,
        )}
      >
        {leftIcon && <span className={styles.icon}>{leftIcon}</span>}

        <input
          ref={ref}
          id={inputId}
          disabled={disabled}
          aria-invalid={error ? true : undefined}
          aria-describedby={helpId}
          className={cx(styles.input, className)}
          {...rest}
        />

        {rightSlot && <span className={styles.icon}>{rightSlot}</span>}
      </div>

      {(error || hint) && (
        <span
          id={helpId}
          className={cx(styles.help, error && styles.helpError)}
          role={error ? 'alert' : undefined}
        >
          {error ?? hint}
        </span>
      )}
    </div>
  );
});

export default BaseInput;
