// pages/AuthPage.tsx
'use client'
import { useState, type FormEvent } from 'react'
import { useAuthService, HttpError } from '../../services/authServise'
import type { IUser } from '../../types/authTypes'

type Mode = 'login' | 'register'

export default function AuthPage() {
  const auth = useAuthService()

  const [mode, setMode] = useState<Mode>('login')
  const [username, setUsername] = useState('')
  const [password, setPassword] = useState('')
  const [password2, setPassword2] = useState('')
  const [role, setRole] = useState('user')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [user, setUser] = useState<IUser | null>(null)

  function switchMode(next: Mode) {
    setMode(next)
    setError(null)
    setPassword('')
    setPassword2('')
  }

  async function handleSubmit(e: FormEvent) {
    e.preventDefault()
    setError(null)

    if (mode === 'register' && password !== password2) {
      setError('Пароли не совпадают')
      return
    }

    setLoading(true)
    try {
      const result =
        mode === 'login'
          ? await auth.login({ username, password })
          : await auth.register({ username, password, role })

      console.log(
        mode === 'login' ? '✅ Успешный вход:' : '✅ Успешная регистрация:',
        result.user
      )
      setUser(result.user)
      setPassword('')
      setPassword2('')
    } catch (err) {
      if (err instanceof HttpError) {
        console.error('❌ Ошибка HTTP:', err.status, err.data)
        setError(err.message)
      } else {
        console.error('❌ Неизвестная ошибка:', err)
        setError('Что-то пошло не так')
      }
    } finally {
      setLoading(false)
    }
  }

  return (
    <form onSubmit={handleSubmit} style={{ maxWidth: 320, margin: '40px auto' }}>
      <h2>{mode === 'login' ? 'Вход' : 'Регистрация'}</h2>

      <div style={{ marginBottom: 12 }}>
        <input
          type="text"
          placeholder="Имя пользователя"
          value={username}
          onChange={(e) => setUsername(e.target.value)}
          required
          style={{ width: '100%', padding: 8 }}
        />
      </div>

      <div style={{ marginBottom: 12 }}>
        <input
          type="password"
          placeholder="Пароль"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
          required
          style={{ width: '100%', padding: 8 }}
        />
      </div>

      {mode === 'register' && (
        <>
          <div style={{ marginBottom: 12 }}>
            <input
              type="password"
              placeholder="Повторите пароль"
              value={password2}
              onChange={(e) => setPassword2(e.target.value)}
              required
              style={{ width: '100%', padding: 8 }}
            />
          </div>

          <div style={{ marginBottom: 12 }}>
            <select
              value={role}
              onChange={(e) => setRole(e.target.value)}
              style={{ width: '100%', padding: 8 }}
            >
              <option value="user">Пользователь</option>
              <option value="admin">Администратор</option>
            </select>
          </div>
        </>
      )}

      <button type="submit" disabled={loading} style={{ width: '100%', padding: 10 }}>
        {loading
          ? mode === 'login'
            ? 'Вход...'
            : 'Регистрация...'
          : mode === 'login'
            ? 'Войти'
            : 'Зарегистрироваться'}
      </button>

      <p style={{ marginTop: 12, textAlign: 'center', fontSize: 14 }}>
        {mode === 'login' ? (
          <>
            Нет аккаунта?{' '}
            <button
              type="button"
              onClick={() => switchMode('register')}
              style={{ background: 'none', border: 'none', color: '#06f', cursor: 'pointer', padding: 0 }}
            >
              Зарегистрироваться
            </button>
          </>
        ) : (
          <>
            Уже есть аккаунт?{' '}
            <button
              type="button"
              onClick={() => switchMode('login')}
              style={{ background: 'none', border: 'none', color: '#06f', cursor: 'pointer', padding: 0 }}
            >
              Войти
            </button>
          </>
        )}
      </p>

      {error && <p style={{ color: 'red', marginTop: 12 }}>{error}</p>}

      {user && (
        <p style={{ color: 'green', marginTop: 12 }}>
          Привет, {user.username} (роль: {user.role})
        </p>
      )}
    </form>
  )
}
