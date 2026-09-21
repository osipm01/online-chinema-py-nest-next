<template>
  <GalssPanel>
    <div class="navigation-bar">
      <NuxtLink
        :to="`/media/tv-shows/${showId}/seasons/${seasonId}`"
        class="btn-back"
      >
        ← Назад к сезону
      </NuxtLink>
    </div>

    <BaseForm class="user-form-container">
      <div v-if="pending" class="loading-state">
        Загрузка данных эпизода...
      </div>

      <div v-else-if="error" class="error-state">
        <p>Произошла ошибка при загрузке: {{ error }}</p>
      </div>

      <div v-else class="form-content">
        <div class="form-header">
          <h1 class="page-title">Эпизод №{{ episodeId }}</h1>
        </div>

        <div class="form-section">
          <div class="input-field-group">
            <label for="title" class="field-label">Название</label>
            <input
              id="title"
              v-model="form.title"
              type="text"
              required
              class="custom-input"
              placeholder="Название эпизода"
              :disabled="isProcessing"
            />
          </div>

          <div class="input-field-group">
            <label for="duration" class="field-label">Длительность (мин)</label>
            <input
              id="duration"
              v-model.number="form.duration"
              type="number"
              min="0"
              class="custom-input"
              :disabled="isProcessing"
            />
          </div>

          <div class="input-field-group">
            <label for="hls_link" class="field-label">HLS ссылка</label>
            <input
              id="hls_link"
              v-model="form.hls_link"
              type="text"
              class="custom-input"
              placeholder="https://..."
              :disabled="isProcessing"
            />
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
            <NuxtLink
              :to="`/media/tv-shows/${showId}/seasons/${seasonId}`"
              class="btn-action btn-secondary"
            >
              Отмена
            </NuxtLink>
          </div>
        </div>

        <hr class="form-divider" />

        <div class="form-section">
          <button
            @click="handleDelete"
            class="btn-action btn-danger"
            :disabled="isProcessing"
          >
            {{ isProcessing ? 'Удаление...' : 'Удалить эпизод' }}
          </button>
        </div>
      </div>
    </BaseForm>
  </GalssPanel>
</template>

<script setup lang="ts">
import { ref, reactive } from 'vue'

definePageMeta({
  middleware: 'auth',
  layout: 'default'
})

const route = useRoute()
const router = useRouter()
const mediaService = useMedia()

const showId = Number(route.params.id)
const seasonId = Number(route.params.seasonId)
const episodeId = Number(route.params.episodeId)

const form = reactive({
  title: '',
  duration: 0,
  hls_link: '',
  poster_url: ''
})

const pending = ref(true)
const isProcessing = ref(false)
const error = ref<string | null>(null)

onMounted(async () => {
  try {
    const episode = await mediaService.getEpisode(episodeId)
    form.title = episode.title
    form.duration = episode.duration
    form.hls_link = episode.hls_link
    form.poster_url = episode.poster_url
  } catch (e: any) {
    error.value = e.message || 'Ошибка загрузки эпизода'
  } finally {
    pending.value = false
  }
})

const handleUpdate = async () => {
  try {
    isProcessing.value = true
    error.value = null

    await mediaService.updateEpisode(episodeId, {
      title: form.title,
      duration: form.duration,
      hls_link: form.hls_link,
      poster_url: form.poster_url
    })

    useToastify('Эпизод обновлён', {
      type: 'success',
      autoClose: 3000,
      theme: 'auto'
    })

    router.push(`/tv-shows/${showId}/seasons/${seasonId}`)
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

const handleDelete = async () => {
  if (!confirm('Удалить этот эпизод?')) return

  try {
    isProcessing.value = true
    await mediaService.deleteEpisode(episodeId)
    router.push(`/tv-shows/${showId}/seasons/${seasonId}`)
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

.custom-input:disabled {
  background: rgba(255, 255, 255, 0.5);
  cursor: not-allowed;
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
  transition: opacity 0.2s, transform 0.1s;
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

.btn-success {
  background-color: #2ec4b6;
  color: white;
  width: max-content;
}

.btn-danger {
  background-color: #e71d36;
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