<template>
  <BaseForm class="user-form-container">
    <div v-if="pending" class="loading-state">Загрузка данных сезона...</div>

    <div v-else-if="loadError" class="error-state">
      <p>Произошла ошибка при загрузке: {{ loadError }}</p>
    </div>

    <div v-else class="form-content">
      <div class="form-section">
        <BaseInput
          v-model="form.season_number"
          type="number"
          label="Номер сезона"
          :min="1"
          :disabled="isProcessing"
        />
        <BaseInput
          v-model="form.title"
          label="Название"
          placeholder="Название сезона"
          :disabled="isProcessing"
        />
        <BaseTextarea
          v-model="form.description"
          label="Описание"
          placeholder="Описание сезона"
          :disabled="isProcessing"
          :rows="4"
        />
        <BaseInput
          v-model="form.poster_url"
          label="Poster URL"
          placeholder="https://..."
          :disabled="isProcessing"
        />

        <div class="action-bar">
          <BaseButton
            variant="success"
            :loading="isProcessing"
            loading-text="Сохранение..."
            @click="handleUpdate"
          >
            Сохранить изменения
          </BaseButton>
        </div>
      </div>

      <div class="episodes-section">
        <div class="episodes-header">
          <h3 class="section-title">Эпизоды</h3>
          <BaseLink
            :to="`/media/tv-shows/${showId}/seasons/${seasonId}/episodes/create`"
            variant="secondary"
            size="sm"
          >
            + Добавить эпизод
          </BaseLink>
        </div>

        <div v-if="episodes.length === 0" class="empty-state-text">
          Эпизоды не добавлены.
        </div>

        <div v-else class="users-list-container">
          <div
            v-for="episode in episodes"
            :key="episode.id"
            class="user-row-item"
          >
            <div class="user-info-block">
              <span class="user-name-text">{{ episode.title }}</span>
              <span class="user-role-text">({{ episode.duration }} мин)</span>
            </div>

            <div class="user-actions-block">
              <BaseLink
                :to="`/media/tv-shows/${showId}/seasons/${seasonId}/episodes/${episode.id}`"
                variant="primary"
                size="sm"
              >
                Редактировать
              </BaseLink>
              <BaseButton
                variant="danger"
                size="sm"
                :loading="isDeletingEpisode"
                @click="deleteEpisode(episode.id)"
              >
                Удалить
              </BaseButton>
            </div>
          </div>
        </div>
      </div>

      <hr class="form-divider" />

      <div class="form-section">
        <BaseButton
          variant="danger"
          :loading="isDeletingSeason"
          loading-text="Удаление..."
          @click="handleDeleteSeason"
        >
          Удалить сезон
        </BaseButton>
      </div>

      <div v-if="error" class="error-state">{{ error }}</div>
    </div>
  </BaseForm>
</template>

<script setup lang="ts">
import { reactive, ref } from 'vue'
import type { Episode } from '~/types/MediaTypes'

definePageMeta({
  middleware: 'auth',
  layout: 'default'
})

const route = useRoute()
const router = useRouter()
const mediaService = useMedia()

const showId = Number(route.params.id)
const seasonId = Number(route.params.seasonId)

const form = reactive({
  season_number: 1,
  title: '',
  description: '',
  poster_url: ''
})

const episodes = ref<Episode[]>([])
const pending = ref(true)
const loadError = ref<string | null>(null)

onMounted(async () => {
  try {
    const season = await mediaService.getSeason(seasonId)
    form.season_number = season.season_number
    form.title = season.title
    form.description = season.description
    form.poster_url = season.poster_url
    episodes.value = season.episodes || []
  } catch (e: any) {
    loadError.value = e.message || 'Ошибка загрузки сезона'
  } finally {
    pending.value = false
  }
})

const { isProcessing, error, execute: executeUpdate } = useAsyncAction(
  () => mediaService.updateSeason(seasonId, {
    season_number: form.season_number,
    title: form.title,
    description: form.description,
    poster_url: form.poster_url
  }),
  {
    toast: {
      successMessage: 'Сезон обновлён',
      errorMessage: (e) => e?.data?.detail || `Ошибка ${e?.status || ''}`,
    },
  }
)

const { isProcessing: isDeletingEpisode, execute: executeDeleteEpisode } = useAsyncAction(
  (episodeId: number) => mediaService.deleteEpisode(episodeId),
  {
    toast: {
      successMessage: 'Эпизод удалён',
      errorMessage: (e) => `Ошибка ${e?.status || ''}`,
    },
  }
)

const { isProcessing: isDeletingSeason, execute: executeDeleteSeason } = useAsyncAction(
  () => mediaService.deleteSeason(seasonId),
  {
    toast: {
      successMessage: 'Сезон удалён',
      errorMessage: (e) => `Ошибка ${e?.status || ''}`,
    },
    onSuccess: () => router.push(`/media/tv-shows/${showId}/seasons`),
  }
)

const handleUpdate = () => executeUpdate().catch(() => {})

const deleteEpisode = async (episodeId: number) => {
  if (!confirm('Удалить этот эпизод?')) return
  try {
    await executeDeleteEpisode(episodeId)
    episodes.value = episodes.value.filter((e) => e.id !== episodeId)
  } catch {
    // toast уже показан
  }
}

const handleDeleteSeason = async () => {
  if (!confirm('Удалить этот сезон со всеми эпизодами?')) return
  await executeDeleteSeason().catch(() => {})
}
</script>

<style scoped>
.form-content {
  display: flex;
  flex-direction: column;
  gap: 24px;
}

.form-section {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.episodes-section {
  display: flex;
  flex-direction: column;
  gap: 12px;
  padding: 16px;
  border: 1px solid rgba(255, 255, 255, 0.15);
  border-radius: 12px;
  background: rgba(255, 255, 255, 0.04);
}

.episodes-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.section-title {
  color: #ffffff;
  font-size: 16px;
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

.action-bar {
  margin-top: 8px;
  display: flex;
  gap: 12px;
  align-items: center;
}

.form-divider {
  border: 0;
  height: 1px;
  background: rgba(255, 255, 255, 0.15);
  margin: 8px 0;
}
</style>