<template>
  <BaseForm class="user-form-container">
    <div class="form-content">
      <div class="form-header">
        <h3 class="section-title">Новый эпизод</h3>
      </div>

      <form @submit.prevent="handleSubmit" class="form-section">
        <BaseInput
          v-model="form.title"
          label="Название"
          placeholder="Название эпизода"
          :disabled="isProcessing"
          required
        />

        <BaseInput
          v-model="form.duration"
          type="number"
          label="Длительность (мин)"
          :min="0"
          :disabled="isProcessing"
        />

        <BaseInput
          v-model="form.hls_link"
          label="HLS ссылка"
          placeholder="https://..."
          :disabled="isProcessing"
        />

        <BaseInput
          v-model="form.poster_url"
          label="Poster URL"
          placeholder="https://..."
          :disabled="isProcessing"
        />

        <div class="action-bar">
          <BaseButton
            native-type="submit"
            variant="success"
            :loading="isProcessing"
            loading-text="Создание..."
          >
            Создать эпизод
          </BaseButton>
          <BaseLink
            :to="`/media/tv-shows/${showId}/seasons/${seasonId}`"
            variant="secondary"
          >
            Отмена
          </BaseLink>
        </div>
      </form>

      <div v-if="error" class="error-state">{{ error }}</div>
    </div>
  </BaseForm>
</template>

<script setup lang="ts">
import { reactive } from 'vue'

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
  title: '',
  duration: 0,
  hls_link: '',
  poster_url: ''
})

const { isProcessing, error, execute } = useAsyncAction(
  () => mediaService.createEpisode({
    title: form.title,
    duration: form.duration,
    hls_link: form.hls_link,
    poster_url: form.poster_url,
    season_id: seasonId,
    media_id: showId
  }),
  {
    toast: {
      successMessage: 'Эпизод создан',
      errorMessage: (e) => e?.data?.detail || `Ошибка ${e?.status || ''}`,
    },
    onSuccess: () => router.push(`/media/tv-shows/${showId}/seasons/${seasonId}`),
  }
)

const handleSubmit = () => execute().catch(() => {})
</script>

<style scoped>
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

.section-title {
  color: #ffffff;
  font-size: 16px;
  font-weight: 600;
  margin: 0;
}

.form-section {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.action-bar {
  margin-top: 8px;
  display: flex;
  gap: 12px;
  align-items: center;
}
</style>