// pages/AuthPage.tsx
'use client';

import { useState, type FormEvent } from 'react';
import { useRouter, useSearchParams } from 'next/navigation';
import { useAuthService, HttpError } from '../../services/authServise';
import BaseInput from '../../components/ui/BaseInput';
import BaseButton from '../../components/ui/BaseButton';
import BaseLink from '../../components/ui/BaseLink';
import styles from './AuthPage.module.scss';

type Mode = 'login' | 'register';

export default function AuthPage() {
  const auth = useAuthService();
  const router = useRouter();
  const searchParams = useSearchParams();

  // Куда вернуть пользователя после входа.
  // Приоритет: ?from=... → главная.
  const from = searchParams.get('from') || '/';

  const [mode, setMode] = useState<Mode>('login');
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [password2, setPassword2] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  function switchMode(next: Mode) {
    setMode(next);
    setError(null);
    setPassword('');
    setPassword2('');
  }

  async function handleSubmit(e: FormEvent) {
    e.preventDefault();
    setError(null);

    if (mode === 'register' && password !== password2) {
      setError('Пароли не совпадают');
      return;
    }

    setLoading(true);
    try {
      const result =
        mode === 'login'
          ? await auth.login({ username, password })
          : await auth.register({ username, password }); // роль не передаём

      console.log(
        mode === 'login' ? '✅ Успешный вход:' : '✅ Успешная регистрация:',
        result.user,
      );

      // Редирект туда, откуда пришёл пользователь.
      // replace — чтобы страница авторизации не оставалась в истории.
      router.replace(from);
    } catch (err) {
      if (err instanceof HttpError) {
        console.error('❌ Ошибка HTTP:', err.status, err.data);
        setError(err.message);
      } else {
        console.error('❌ Неизвестная ошибка:', err);
        setError('Что-то пошло не так');
      }
    } finally {
      setLoading(false);
    }
  }

  return (
    <main className={styles.page}>
      <div className={styles.glow} aria-hidden="true" />
      <div className={styles.glow2} aria-hidden="true" />

      <form
        onSubmit={handleSubmit}
        className={`${styles.card} ${mode === 'register' ? styles.cardRegister : ''}`}
        noValidate
      >
        <h1 className={styles.title} key={mode}>
          {mode === 'login' ? 'Вход' : 'Регистрация'}
        </h1>

        <p className={styles.subtitle}>
          {mode === 'login'
            ? 'Войдите, чтобы продолжить'
            : 'Создайте аккаунт за пару секунд'}
        </p>

        <div className={styles.fields}>
          <div className={styles.fieldWrap} style={{ animationDelay: '0.05s' }}>
            <BaseInput
              label="Имя пользователя"
              type="text"
              placeholder="Введите имя пользователя"
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              autoComplete="username"
              required
              fullWidth
            />
          </div>

          <div className={styles.fieldWrap} style={{ animationDelay: '0.1s' }}>
            <BaseInput
              label="Пароль"
              type="password"
              placeholder="Введите пароль"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              autoComplete={mode === 'login' ? 'current-password' : 'new-password'}
              required
              fullWidth
            />
          </div>

          {mode === 'register' && (
            <div className={styles.fieldWrap} style={{ animationDelay: '0.15s' }}>
              <BaseInput
                label="Повторите пароль"
                type="password"
                placeholder="Повторите пароль"
                value={password2}
                onChange={(e) => setPassword2(e.target.value)}
                autoComplete="new-password"
                required
                fullWidth
              />
            </div>
          )}
        </div>

        <div className={styles.submitWrap} style={{ animationDelay: '0.2s' }}>
          <BaseButton
            type="submit"
            variant="primary"
            size="lg"
            fullWidth
            loading={loading}
          >
            {mode === 'login' ? 'Войти' : 'Зарегистрироваться'}
          </BaseButton>
        </div>

        {error && (
          <p className={styles.error} role="alert">
            {error}
          </p>
        )}

        <p className={styles.switch} style={{ animationDelay: '0.25s' }}>
          {mode === 'login' ? (
            <>
              Нет аккаунта?{' '}
              <BaseLink
                as="button"
                type="button"
                onClick={() => switchMode('register')}
                className={styles.switchLink}
              >
                Зарегистрироваться
              </BaseLink>
            </>
          ) : (
            <>
              Уже есть аккаунт?{' '}
              <BaseLink
                as="button"
                type="button"
                onClick={() => switchMode('login')}
                className={styles.switchLink}
              >
                Войти
              </BaseLink>
            </>
          )}
        </p>

        <p className={styles.legal} style={{ animationDelay: '0.3s' }}>
          Продолжая, вы соглашаетесь с{' '}
          <BaseLink href="/terms">условиями</BaseLink> и{' '}
          <BaseLink href="/privacy">политикой конфиденциальности</BaseLink>.
        </p>
      </form>
    </main>
  );
}
