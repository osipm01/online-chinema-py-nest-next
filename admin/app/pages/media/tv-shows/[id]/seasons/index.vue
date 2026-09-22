<template>
  <div class="page-inner">
    <div class="form-header">
      <h2 class="section-title">Сезоны</h2>
      <BaseLink
        :to="`/media/tv-shows/${showId}/seasons/create`"
        variant="success"
        size="sm"
      >
        + Добавить сезон
      </BaseLink>
    </div>

    <div v-if="pending" class="loading-state">Загрузка сезонов...</div>

    <div v-else-if="error" class="error-state">Ошибка: {{ error }}</div>

    <div v-else-if="seasons.length > 0" class="users-list-container">
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
          <BaseLink
            :to="`/media/tv-shows/${showId}/seasons/${season.id}`"
            variant="primary"
            size="sm"
          >
            Открыть
          </BaseLink>
          <BaseButton
            variant="danger"
            size="sm"
            :loading="isProcessing"
            @click="deleteSeason(season.id)"
          >
            Удалить
          </BaseButton>
        </div>
      </div>
    </div>

    <div v-else class="empty-state-text">Сезоны не добавлены.</div>
  </div>
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

const { isProcessing, execute: executeDelete } = useAsyncAction(
  (id: number) => mediaService.deleteSeason(id),
  {
    toast: {
      successMessage: 'Сезон удалён',
      errorMessage: (e) => `Ошибка ${e?.status || ''}`,
    },
    onSuccess: () => fetchSeasons(),
  }
)

const deleteSeason = async (id: number) => {
  if (!confirm('Вы уверены, что хотите удалить этот сезон?')) return
  await executeDelete(id).catch(() => {})
}

onMounted(fetchSeasons)
</script>

<style scoped>
.page-inner {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.form-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.section-title {
  color: #ffffff;
  font-size: 18px;
  font-weight: 600;
  margin: 0;
}

.users-list-container {
  display: flex;
  flex-direction: column;
  gap: 8px;
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
</style>