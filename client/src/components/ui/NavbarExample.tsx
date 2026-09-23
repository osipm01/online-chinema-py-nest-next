// Пример: шапка со скриншота на базе трёх компонентов
import BaseButton from './BaseButton';
import BaseInput from './BaseInput';
import BaseLink from './BaseLink';

const SearchIcon = () => (
  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round">
    <circle cx="11" cy="11" r="7" /><path d="m20 20-3.5-3.5" />
  </svg>
);

const BellIcon = () => (
  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round">
    <path d="M6 9a6 6 0 1 1 12 0c0 6 2 7 2 7H4s2-1 2-7Z" /><path d="M10 20a2 2 0 0 0 4 0" />
  </svg>
);

export default function NavbarExample() {
  return (
    <header style={{ display: 'flex', alignItems: 'center', gap: 8, padding: 12 }}>
      <nav style={{ display: 'flex', gap: 4, flex: 1 }}>
        <BaseLink href="/" active>Главная</BaseLink>
        <BaseLink href="/movies">Фильмы</BaseLink>
        <BaseLink href="/series">Сериалы</BaseLink>
        <BaseLink href="/collections">Подборки</BaseLink>
        <BaseLink href="/new">Новинки</BaseLink>
      </nav>

      <BaseInput
        pill
        type="search"
        aria-label="Поиск"
        placeholder="Поиск фильмов и сериалов"
        leftIcon={<SearchIcon />}
        wrapperClassName="search"
      />

      <BaseButton variant="outline" iconOnly aria-label="Уведомления" leftIcon={<BellIcon />} />
    </header>
  );
}
