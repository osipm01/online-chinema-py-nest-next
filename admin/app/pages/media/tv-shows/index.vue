<template>
  <GalssPanel>
    <div class="page-inner">
      <div class="navigation-bar">
        <BaseLink to="/media/tv-shows/create" variant="success">
          + Создать сериал
        </BaseLink>
      </div>

      <div class="form-header">
        <h1 class="page-title">Сериалы</h1>
      </div>

      <div class="filters-bar">
        <BaseInput
          v-model="searchQuery"
          label="Поиск"
          placeholder="Название сериала"
          class="filters-field"
          @enter="applyFilters"
        />

        <BaseSelect
          v-model="selectedCategoryId"
          label="Категория"
          class="filters-field"
        >
          <option :value="null">Все категории</option>
          <option
            v-for="category in categories"
            :key="category.id"
            :value="category.id"
          >
            {{ category.name }}
          </option>
        </BaseSelect>

        <div class="filters-actions">
          <BaseButton
            variant="success"
            size="sm"
            :disabled="pending"
            @click="applyFilters"
          >
            Применить
          </BaseButton>
          <BaseButton
            variant="secondary"
            size="sm"
            :disabled="pending"
            @click="resetFilters"
          >
            Сбросить
          </BaseButton>
        </div>
      </div>

      <div v-if="pending" class="loading-state">
        Загрузка списка сериалов...
      </div>

      <div v-else-if="error" class="error-state">
        Ошибка: {{ error }}
      </div>

      <div v-else-if="tvShows.length > 0" class="users-list-container">
        <div
          v-for="show in tvShows"
          :key="show.id"
          class="user-row-item"
        >
          <div class="user-info-block">
            <span class="user-name-text">{{ show.title }}</span>
            <span class="user-role-text">({{ show.type }})</span>
          </div>

          <div class="user-actions-block">
            <BaseLink
              :to="`/media/tv-shows/${show.id}`"
              variant="primary"
              size="sm"
            >
              Редактировать
            </BaseLink>
            <BaseLink
              :to="`/media/tv-shows/${show.id}/seasons`"
              variant="secondary"
              size="sm"
            >
              Сезоны
            </BaseLink>
            <BaseButton
              variant="danger"
              size="sm"
              :loading="isProcessing"
              @click="deleteShow(show.id)"
            >
              Удалить
            </BaseButton>
          </div>
        </div>
      </div>

      <div v-else class="empty-state-text">
        Список сериалов пуст.
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

const tvShows = ref<Media[]>([])
const categories = ref<Category[]>([])
const pending = ref(true)
const error = ref<string | null>(null)

const searchQuery = ref('')
const selectedCategoryId = ref<number | null>(null)

const fetchTvShows = async () => {
  pending.value = true
  error.value = null
  try {
    if (searchQuery.value.trim()) {
      const list = await mediaService.search(searchQuery.value.trim())
      tvShows.value = list.filter((m) => m.type === 'tv_show')
    } else if (selectedCategoryId.value !== null) {
      const list = await mediaService.getByCategory(selectedCategoryId.value)
      tvShows.value = list.filter((m) => m.type === 'tv_show')
    } else {
      tvShows.value = await mediaService.getTvShows()
    }
  } catch (e: any) {
    error.value = e.message || 'Ошибка при загрузке сериалов'
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

const applyFilters = () => fetchTvShows()

const resetFilters = () => {
  searchQuery.value = ''
  selectedCategoryId.value = null
  fetchTvShows()
}

const { isProcessing, execute: executeDelete } = useAsyncAction(
  (id: number) => mediaService.delete(id),
  {
    toast: {
      successMessage: 'Сериал удалён',
      errorMessage: (e) => `Ошибка ${e?.status || ''}`,
    },
    onSuccess: () => fetchTvShows(),
  }
)

const deleteShow = async (id: number) => {
  if (!confirm('Вы уверены, что хотите удалить этот сериал?')) return
  await executeDelete(id).catch(() => {})
}

onMounted(() => {
  fetchCategories()
  fetchTvShows()
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
</style>