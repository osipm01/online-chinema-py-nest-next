<template>
  <GalssPanel>
    <div class="navigation-bar">
      <NuxtLink :to="`/media/tv-shows/${showId}/seasons`" class="btn-back">← Назад к сезонам</NuxtLink>
    </div>

    <BaseForm class="user-form-container">
      <div v-if="pending" class="loading-state">
        Загрузка данных сезона...
      </div>

      <div v-else-if="error" class="error-state">
        <p>Произошла ошибка при загрузке: {{ error }}</p>
      </div>

      <div v-else class="form-content">
        <div class="form-header">
          <h1 class="page-title">
            Сезон {{ form.season_number }} — {{ form.title || 'Без названия' }}
          </h1>
        </div>

        <div class="form-section">
          <div class="input-field-group">
            <label for="season_number" class="field-label">Номер сезона</label>
            <input
              id="season_number"
              v-model.number="form.season_number"
              type="number"
              min="1"
              class="custom-input"
              :disabled="isProcessing"
            />
          </div>

          <div class="input-field-group">
            <label for="title" class="field-label">Название</label>
            <input
              id="title"
              v-model="form.title"
              type="text"
              class="custom-input"
              placeholder="Название сезона"
              :disabled="isProcessing"
            />
          </div>

          <div class="input-field-group">
            <label for="description" class="field-label">Описание</label>
            <textarea
              id="description"
              v-model="form.description"
              class="custom-input custom-textarea"
              placeholder="Описание сезона"
              :disabled="isProcessing"
            ></textarea>
          </div>

          <div class="input-field-group">
            <label for="poster_url" class="field-label">Poster URL</label>
            <input
              id="poster_url"
              v-model="form.poster_url"
              type="text"
              class="custom-input"
              placeholder="https://..."
              :disabled="isProcessing"
            />
          </div>

          <div class="action-bar">
            <button
              type="button"
              class="btn-action btn-success"
              :disabled="isProcessing"
              @click="handleUpdate"
            >
              {{ isProcessing ? 'Сохранение...' : 'Сохранить изменения' }}
            </button>
            <NuxtLink :to="`/media/tv-shows/${showId}/seasons`" class="btn-action btn-secondary">
              Отмена
            </NuxtLink>
          </div>
        </div>

        <!-- Эпизоды -->
        <div class="episodes-section">
          <div class="episodes-header">
            <h2 class="section-title">Эпизоды</h2>
            <NuxtLink
              :to="`/media/tv-shows/${showId}/seasons/${seasonId}/episodes/create`"
              class="btn-action btn-secondary btn-small"
            >
              + Добавить эпизод
            </NuxtLink>
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
                <NuxtLink
                  :to="`/media/tv-shows/${showId}/seasons/${seasonId}/episodes/${episode.id}`"
                  class="btn-action btn-primary btn-small"
                >
                  Редактировать
                </NuxtLink>
                <button
                  class="btn-action btn-danger btn-small"
                  :disabled="isProcessing"
                  @click="deleteEpisode(episode.id)"
                >
                  Удалить
                </button>
              </div>
            </div>
          </div>
        </div>

        <hr class="form-divider" />

        <div class="form-section">
          <button
            @click="handleDeleteSeason"
            class="btn-action btn-danger"
            :disabled="isProcessing"
          >
            {{ isProcessing ? 'Удаление...' : 'Удалить сезон' }}
          </button>
        </div>
      </div>
    </BaseForm>
  </GalssPanel>
</template>

<script setup lang="ts">
import { ref, reactive } from 'vue'
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
const isProcessing = ref(false)
const error = ref<string | null>(null)

onMounted(async () => {
  try {
    const season = await mediaService.getSeason(seasonId)
    form.season_number = season.season_number
    form.title = season.title
    form.description = season.description
    form.poster_url = season.poster_url
    episodes.value = season.episodes || []
  } catch (e: any) {
    error.value = e.message || 'Ошибка загрузки сезона'
  } finally {
    pending.value = false
  }
})

const handleUpdate = async () => {
  try {
    isProcessing.value = true
    error.value = null

    await mediaService.updateSeason(seasonId, {
      season_number: form.season_number,
      title: form.title,
      description: form.description,
      poster_url: form.poster_url
    })

    useToastify('Сезон обновлён', {
      type: 'success',
      autoClose: 3000,
      theme: 'auto'
    })
  } catch (err: any) {
    error.value = err.message || 'Ошибка при сохранении'
    useToastify(`Ошибка ${err.status || ''}`, {
      type: 'error',
      autoClose: 3000,
      theme: 'auto'
    })
    console.error(err)
  } finally {
    isProcessing.value = false
  }
}

const deleteEpisode = async (episodeId: number) => {
  if (!confirm('Удалить этот эпизод?')) return

  try {
    isProcessing.value = true
    await mediaService.deleteEpisode(episodeId)
    episodes.value = episodes.value.filter((e) => e.id !== episodeId)
    useToastify('Эпизод удалён', {
      type: 'success',
      autoClose: 3000,
      theme: 'auto'
    })
  } catch (err: any) {
    useToastify(`Ошибка ${err.status || ''}`, {
      type: 'error',
      autoClose: 3000,
      theme: 'auto'
    })
    console.error(err)
  } finally {
    isProcessing.value = false
  }
}

const handleDeleteSeason = async () => {
  if (!confirm('Удалить этот сезон со всеми эпизодами?')) return

  try {
    isProcessing.value = true
    await mediaService.deleteSeason(seasonId)
    router.push(`/media/tv-shows/${showId}/seasons`)
  } catch (err: any) {
    useToastify(`Ошибка ${err.status || ''}`, {
      type: 'error',
      autoClose: 3000,
      theme: 'auto'
    })
    console.error(err)
  } finally {
    isProcessing.value = false
  }
}
</script>

<style scoped>
.navigation-bar {
  margin-bottom: 16px;
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

.form-content {
  display: flex;
  flex-direction: column;
  gap: 24px;
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

.form-section {
  display: flex;
  flex-direction: column;
  gap: 16px;
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

.custom-textarea {
  min-height: 100px;
  resize: vertical;
  font-family: inherit;
}

.custom-input:disabled {
  background: rgba(255, 255, 255, 0.5);
  cursor: not-allowed;
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
  font-size: 18px;
  font-weight: 600;
  margin: 0;
}

.empty-state-text {
  color: rgba(255, 255, 255, 0.5);
  font-style: italic;
  font-size: 13px;
  padding: 6px 0;
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

.btn-action {
  padding: 12px 24px;
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

.btn-success {
  background-color: #2ec4b6;
  color: white;
  width: max-content;
}

.btn-danger {
  background-color: #e71d36;
  color: white;
}

.btn-primary {
  background-color: #007a;
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

.form-divider {
  border: 0;
  height: 1px;
  background: rgba(255, 255, 255, 0.15);
  margin: 8px 0;
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
</style>