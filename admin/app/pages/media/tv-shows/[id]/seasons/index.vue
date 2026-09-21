<template>
  <GalssPanel>
    <div class="page-inner">
      <div class="navigation-bar">
        <NuxtLink :to="`/meida/tv-shows/${showId}`" class="btn-back">← К сериалу</NuxtLink>
      </div>

      <div class="form-header">
        <h1 class="page-title">Сезоны сериала №{{ showId }}</h1>
        <NuxtLink :to="`/media/tv-shows/${showId}/seasons/create`" class="btn-action btn-success btn-small">
          + Добавить сезон
        </NuxtLink>
      </div>

      <div v-if="pending" class="loading-state">
        Загрузка сезонов...
      </div>

      <div v-else-if="error" class="error-state">
        Ошибка: {{ error }}
      </div>

      <div v-else-if="seasons && seasons.length > 0" class="users-list-container">
        <div
          v-for="season in seasons"
          :key="season.id"
          class="user-row-item"
        >
          <div class="user-info-block">
            <span class="user-name-text">
              Сезон {{ season.season_number }}: {{ season.title || 'Без названия' }}
            </span>
          </div>

          <div class="user-actions-block">
            <NuxtLink
              :to="`/media/tv-shows/${showId}/seasons/${season.id}`"
              class="btn-action btn-primary btn-small"
            >
              Открыть
            </NuxtLink>
            <button
              class="btn-action btn-danger btn-small"
              :disabled="isProcessing"
              @click="deleteSeason(season.id)"
            >
              Удалить
            </button>
          </div>
        </div>
      </div>

      <div v-else class="empty-state-text">
        Сезоны не добавлены.
      </div>
    </div>
  </GalssPanel>
</template>

<script setup lang="ts">
import type { Season } from '~/types/MediaTypes'

definePageMeta({
  middleware: 'auth',
  layout: 'default'
})

const route = useRoute()
const mediaService = useMedia()

const showId = Number(route.params.id)

const seasons = ref<Season[]>([])
const pending = ref(true)
const error = ref<string | null>(null)
const isProcessing = ref(false)

const fetchSeasons = async () => {
  pending.value = true
  error.value = null
  try {
    seasons.value = await mediaService.getSeasonsByMedia(showId)
  } catch (e: any) {
    error.value = e.message || 'Ошибка при загрузке сезонов'
  } finally {
    pending.value = false
  }
}

const deleteSeason = async (id: number) => {
  if (!confirm('Вы уверены, что хотите удалить этот сезон?')) return

  try {
    isProcessing.value = true
    await mediaService.deleteSeason(id)
    await fetchSeasons()
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
  fetchSeasons()
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

.user-actions-block {
  display: flex;
  gap: 8px;
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
</style>