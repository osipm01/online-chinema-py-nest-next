'use client';

import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import { useTheme } from 'next-themes';
import { User, Lock, Palette, LogOut, ShieldCheck } from 'lucide-react';

import BaseButton from '@/components/ui/BaseButton';
import BaseInput from '@/components/ui/BaseInput';
import { Tabs, type TabItem } from '@/components/tabs/Tabs';
import { ThemeToggle } from '@/components/ui/ThemeToggle';
import { useAuthStore, selectUser } from '@/store/authStore';
import { getAuthService, HttpError } from '@/services/authServise';

import styles from './ProfilePage.module.scss';

type TabKey = 'general' | 'security' | 'appearance';

const TAB_ITEMS: TabItem[] = [
  { key: 'general', label: 'Профиль', icon: <User size={16} /> },
  { key: 'security', label: 'Безопасность', icon: <Lock size={16} /> },
  { key: 'appearance', label: 'Оформление', icon: <Palette size={16} /> },
];

export default function ProfilePage() {
  const router = useRouter();
  const user = useAuthStore(selectUser);
  const clearAuth = useAuthStore((s) => s.clearAuth);
  const [tab, setTab] = useState<TabKey>('general');

  const [, forceUpdate] = useState(0);

  useEffect(() => {
    console.log("upd page");
    forceUpdate((n) => n + 1);
  }, [user]);

  const handleLogout = async () => {
    try {
      await getAuthService().logout();
    } catch {
      /* ignore */
    } finally {
      clearAuth();
      router.push('/login');
    }
  };

  if (!user) {
    return (
      <main className={styles.page}>
        <div className={styles.empty}>Вы не авторизованы.</div>
      </main>
    );
  }

  return (
    <main className={styles.page}>
      <header className={styles.header}>
        <div className={styles.identity}>
          <div className={styles.avatar} aria-hidden="true">
            {user.username.charAt(0).toUpperCase()}
          </div>
          <div className={styles.identityText}>
            <h1 className={styles.username}>{user.username}</h1>
            <p className={styles.meta}>
              ID: <span className={styles.mono}>{user.id}</span>
              <span className={styles.dot}>·</span>
              Роль: <span className={styles.badge}>{user.role}</span>
            </p>
          </div>
        </div>

        <BaseButton
          variant="outline"
          leftIcon={<LogOut size={18} />}
          onClick={handleLogout}
        >
          Выйти
        </BaseButton>
      </header>

      <Tabs
        items={TAB_ITEMS}
        activeKey={tab}
        onChange={(k) => setTab(k as TabKey)}
        aria-label="Разделы профиля"
      />

      <section
        className={styles.content}
        role="tabpanel"
        id={`panel-${tab}`}
        aria-labelledby={`tab-${tab}`}
      >
        {tab === 'general' && <GeneralSection />}
        {tab === 'security' && <SecuritySection />}
        {tab === 'appearance' && <AppearanceSection />}
      </section>
    </main>
  );
}

/* ---------- Профиль ---------- */

function GeneralSection() {
  const user = useAuthStore(selectUser);

  // 👇 Форс-обновление и здесь — если данные приходят асинхронно
  const [, forceUpdate] = useState(0);
  useEffect(() => {
    forceUpdate((n) => n + 1);
  }, [user]);

  if (!user) return null;

  return (
    <div className={styles.card}>
      <h2 className={styles.cardTitle}>Профиль</h2>
      <p className={styles.cardHint}>
        Основная информация об аккаунте. Изменение имени и роли пока недоступно.
      </p>

      <div className={styles.grid}>
        <BaseInput label="Имя пользователя" value={user.username} readOnly fullWidth />
        <BaseInput label="ID" value={String(user.id)} readOnly fullWidth />
        <BaseInput label="Роль" value={user.role} readOnly fullWidth />
      </div>
    </div>
  );
}

/* ---------- Безопасность ---------- */

function SecuritySection() {
  const service = getAuthService();

  const [oldPassword, setOldPassword] = useState('');
  const [newPassword, setNewPassword] = useState('');
  const [confirm, setConfirm] = useState('');

  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);

  const onSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    setSuccess(null);

    if (newPassword.length < 6) {
      setError('Новый пароль должен быть не короче 6 символов');
      return;
    }
    if (newPassword !== confirm) {
      setError('Пароли не совпадают');
      return;
    }

    setLoading(true);
    try {
      const res = await service.changePassword({
        old_password: oldPassword,
        new_password: newPassword,
      });
      setSuccess(res.detail || 'Пароль успешно изменён');
      setOldPassword('');
      setNewPassword('');
      setConfirm('');
    } catch (err) {
      if (err instanceof HttpError) {
        const detail =
          typeof err.data === 'object' && err.data && 'detail' in err.data
            ? String((err.data as { detail: unknown }).detail)
            : err.message;
        setError(detail);
      } else {
        setError('Не удалось изменить пароль');
      }
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className={styles.card}>
      <h2 className={styles.cardTitle}>Смена пароля</h2>
      <p className={styles.cardHint}>После смены пароля потребуется войти заново.</p>

      <form className={styles.form} onSubmit={onSubmit}>
        <BaseInput
          label="Текущий пароль"
          type="password"
          autoComplete="current-password"
          value={oldPassword}
          onChange={(e) => setOldPassword(e.target.value)}
          leftIcon={<Lock size={16} />}
          fullWidth
          required
        />
        <BaseInput
          label="Новый пароль"
          type="password"
          autoComplete="new-password"
          value={newPassword}
          onChange={(e) => setNewPassword(e.target.value)}
          leftIcon={<ShieldCheck size={16} />}
          fullWidth
          required
        />
        <BaseInput
          label="Повторите новый пароль"
          type="password"
          autoComplete="new-password"
          value={confirm}
          onChange={(e) => setConfirm(e.target.value)}
          fullWidth
          required
          error={confirm && confirm !== newPassword ? 'Пароли не совпадают' : undefined}
        />

        {error && <div className={styles.alertError}>{error}</div>}
        {success && <div className={styles.alertSuccess}>{success}</div>}

        <div className={styles.actions}>
          <BaseButton type="submit" loading={loading}>
            Сохранить
          </BaseButton>
        </div>
      </form>
    </div>
  );
}

/* ---------- Оформление ---------- */

function AppearanceSection() {
  const { theme, setTheme, resolvedTheme } = useTheme();
  const [mounted, setMounted] = useState(false);
  useEffect(() => setMounted(true), []);

  if (!mounted) {
    return (
      <div className={styles.card}>
        <h2 className={styles.cardTitle}>Оформление</h2>
        <div className={styles.themeGrid}>
          <div className={styles.themeSkeleton} />
          <div className={styles.themeSkeleton} />
        </div>
      </div>
    );
  }

  const options: Array<{ key: 'light' | 'dark'; label: string }> = [
    { key: 'dark', label: 'Тёмная' },
    { key: 'light', label: 'Светлая' },
  ];

  return (
    <div className={styles.card}>
      <h2 className={styles.cardTitle}>Оформление</h2>
      <p className={styles.cardHint}>
        Выберите тему интерфейса. Текущая:{' '}
        <b>{resolvedTheme === 'light' ? 'светлая' : 'тёмная'}</b>.
      </p>

      <div className={styles.themeGrid}>
        {options.map((opt) => {
          const active = theme === opt.key;
          return (
            <button
              key={opt.key}
              type="button"
              className={`${styles.themeOption} ${active ? styles.themeOptionActive : ''}`}
              onClick={() => setTheme(opt.key)}
              aria-pressed={active}
            >
              <div
                className={`${styles.themePreview} ${styles[`preview_${opt.key}`]}`}
                aria-hidden="true"
              />
              <span className={styles.themeLabel}>{opt.label}</span>
            </button>
          );
        })}
      </div>

      <div className={styles.inlineRow}>
        <span className={styles.inlineLabel}>Быстрое переключение:</span>
        <ThemeToggle />
      </div>
    </div>
  );
}
