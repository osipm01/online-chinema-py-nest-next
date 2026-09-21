<template>
  <GalssPanel>
    <div class="page-inner">
      <!-- Кнопка создания -->
      <div class="navigation-bar">
        <NuxtLink to="/media/movies/create" class="btn-back">+ Создать фильм</NuxtLink>
      </div>

      <!-- Заголовок -->
      <div class="form-header">
        <h1 class="page-title">Фильмы</h1>
      </div>

      <!-- Фильтры -->
      <div class="filters-bar">
        <div class="input-field-group filters-field">
          <label class="field-label" for="search">Поиск</label>
          <input
            id="search"
            v-model="searchQuery"
            type="text"
            class="custom-input"
            placeholder="Название фильма"
            @keyup.enter="applyFilters"
          />
        </div>

        <div class="input-field-group filters-field">
          <label class="field-label" for="category">Категория</label>
          <select
            id="category"
            v-model="selectedCategoryId"
            class="custom-input custom-select"
          >
            <option :value="null">Все категории</option>
            <option
              v-for="category in categories"
              :key="category.id"
              :value="category.id"
            >
              {{ category.name }}
            </option>
          </select>
        </div>

        <div class="filters-actions">
          <button
            type="button"
            class="btn-action btn-success btn-small"
            :disabled="pending"
            @click="applyFilters"
          >
            Применить
          </button>
          <button
            type="button"
            class="btn-action btn-secondary btn-small"
            :disabled="pending"
            @click="resetFilters"
          >
            Сбросить
          </button>
        </div>
      </div>

      <!-- Состояние загрузки -->
      <div v-if="pending" class="loading-state">
        Загрузка списка фильмов...
      </div>

      <!-- Состояние ошибки -->
      <div v-else-if="error" class="error-state">
        Ошибка: {{ error }}
      </div>

      <!-- Список фильмов -->
      <div v-else-if="movies && movies.length > 0" class="users-list-container">
        <div
          v-for="movie in movies"
          :key="movie.id"
          class="user-row-item"
        >
          <div class="user-info-block">
            <span class="user-name-text">{{ movie.title }}</span>
            <span class="user-role-text">({{ movie.type }})</span>
          </div>

          <div class="user-actions-block">
            <NuxtLink :to="`/media/movies/${movie.id}`" class="btn-action btn-primary btn-small">
              Редактировать
            </NuxtLink>
            <button
              class="btn-action btn-danger btn-small"
              :disabled="isProcessing"
              @click="deleteMovie(movie.id)"
            >
              Удалить
            </button>
          </div>
        </div>
      </div>

      <!-- Пустой список -->
      <div v-else class="empty-state-text">
        Список фильмов пуст.
      </div>
    </div>
  </GalssPanel>
</template>

<script setup lang="ts">
import type { Media } from '~/types/MediaTypes'
import type { Category } from '~/types/CategoryTypes'

definePageMeta({
  middleware: 'auth',
  layout: 'default'
})

const mediaService = useMedia()
const categoryService = useCategory()

const movies = ref<Media[]>([])
const categories = ref<Category[]>([])
const pending = ref(true)
const error = ref<string | null>(null)
const isProcessing = ref(false)

const searchQuery = ref('')
const selectedCategoryId = ref<number | null>(null)

const fetchMovies = async () => {
  pending.value = true
  error.value = null
  try {
    if (searchQuery.value.trim()) {
      movies.value = await mediaService.search(searchQuery.value.trim())
    } else if (selectedCategoryId.value !== null) {
      const list = await mediaService.getByCategory(selectedCategoryId.value)
      movies.value = list.filter((m) => m.type === 'movie')
    } else {
      movies.value = await mediaService.getMovies()
    }
  } catch (e: any) {
    error.value = e.message || 'Ошибка при загрузке фильмов'
  } finally {
    pending.value = false
  }
}

const fetchCategories = async () => {
  try {
    categories.value = await categoryService.getAll()
  } catch (e) {
    console.error('Ошибка загрузки категорий:', e)
  }
}

const applyFilters = () => {
  fetchMovies()
}

const resetFilters = () => {
  searchQuery.value = ''
  selectedCategoryId.value = null
  fetchMovies()
}

const deleteMovie = async (id: number) => {
  if (!confirm('Вы уверены, что хотите удалить этот фильм?')) return

  try {
    isProcessing.value = true
    await mediaService.delete(id)
    await fetchMovies()
  } catch (e: any) {
    useToastify(`Ошибка ${e.status || ''}`, {
      type: 'error',
      autoClose: 3000,
      theme: 'auto'
    })
    console.error(e)
  } finally {
    isProcessing.value = false
  }
}

onMounted(() => {
  fetchCategories()
  fetchMovies()
})
</script>

<style scoped>
.page-inner {
  display: flex;
  flex-direction: column;
  gap: 24px;
  width: 100%;
  max-width: 900px;
  margin: 0 auto;
  box-sizing: border-box;
}

.navigation-bar {
  display: flex;
  justify-content: flex-start;
}

.btn-back {
  color: rgba(255, 255, 255, 0.7);
  text-decoration: none;
  font-size: 14px;
  transition: color 0.2s;
}

.btn-back:hover {
  color: #ffffff;
}

.form-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.page-title {
  color: #ffffff;
  font-size: 24px;
  font-weight: 600;
  margin: 0;
}

.filters-bar {
  display: flex;
  gap: 12px;
  align-items: flex-end;
  flex-wrap: wrap;
}

.filters-field {
  flex: 1 1 200px;
}

.filters-actions {
  display: flex;
  gap: 8px;
  align-items: center;
}

.loading-state {
  color: #ffffff;
  padding: 20px 0;
  text-align: center;
}

.error-state {
  color: #ff6b6b;
  padding: 12px 16px;
  border-radius: 8px;
  background: rgba(255, 107, 107, 0.1);
  border: 1px solid rgba(255, 107, 107, 0.3);
  font-size: 14px;
  text-align: center;
}

.empty-state-text {
  color: rgba(255, 255, 255, 0.5);
  font-style: italic;
  font-size: 14px;
  text-align: center;
  padding: 20px 0;
}

.users-list-container {
  display: flex;
  flex-direction: column;
  gap: 8px;
  width: 100%;
}

.user-row-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 16px;
  background: rgba(255, 255, 255, 0.08);
  border: 1px solid rgba(255, 255, 255, 0.12);
  border-radius: 8px;
  transition: background 0.2s ease;
}

.user-row-item:hover {
  background: rgba(255, 255, 255, 0.12);
}

.user-info-block {
  display: flex;
  align-items: center;
  gap: 8px;
}

.user-name-text {
  color: rgba(255, 255, 255, 0.95);
  font-size: 14px;
  font-weight: 600;
}

.user-role-text {
  color: rgba(255, 255, 255, 0.6);
  font-size: 13px;
}

.user-actions-block {
  display: flex;
  gap: 8px;
}

.input-field-group {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.field-label {
  color: rgba(255, 255, 255, 0.8);
  font-size: 14px;
}

.custom-input {
  width: 100%;
  padding: 12px 16px;
  background: rgba(255, 255, 255, 1);
  border: 1px solid rgba(255, 255, 255, 0.2);
  border-radius: 8px;
  color: #333333;
  font-size: 14px;
  outline: none;
  box-sizing: border-box;
}

.custom-select {
  appearance: none;
  -webkit-appearance: none;
  background-image: url("data:image/svg+xml;charset=UTF-8,%3csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24' fill='none' stroke='%23555' stroke-width='2' stroke-linecap='round' stroke-linejoin='round'%3e%3cpolyline points='6 9 12 15 18 9'%3e%3c/polyline%3e%3c/svg%3e");
  background-repeat: no-repeat;
  background-position: right 12px center;
  background-size: 16px;
  padding-right: 38px;
  cursor: pointer;
}

.btn-action {
  padding: 10px 20px;
  border-radius: 8px;
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  border: none;
  transition: opacity 0.2s, transform 0.1s, background 0.2s;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  text-decoration: none;
}

.btn-action:active {
  transform: scale(0.98);
}

.btn-action:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.btn-small {
  padding: 6px 12px;
  font-size: 13px;
}

.btn-primary {
  background-color: #007a;
  color: white;
}

.btn-primary:hover {
  background-color: #00609a;
}

.btn-danger {
  background-color: #e71d36;
  color: white;
}

.btn-danger:hover {
  background-color: #c9182d;
}

.btn-success {
  background-color: #2ec4b6;
  color: white;
}

.btn-secondary {
  background-color: rgba(255, 255, 255, 0.15);
  color: #ffffff;
  border: 1px solid rgba(255, 255, 255, 0.3);
}

.btn-secondary:hover {
  background-color: rgba(255, 255, 255, 0.25);
}
</style>