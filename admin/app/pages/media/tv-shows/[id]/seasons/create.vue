<template>
  <BaseForm class="user-form-container">
    <div class="form-content">
      <div class="form-header">
        <h2 class="section-title">Новый сезон</h2>
      </div>

      <form @submit.prevent="handleSubmit" class="form-section">
        <BaseInput
          v-model="form.season_number"
          type="number"
          label="Номер сезона"
          :min="1"
          :disabled="isProcessing"
          required
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
            native-type="submit"
            variant="success"
            :loading="isProcessing"
            loading-text="Создание..."
          >
            Создать сезон
          </BaseButton>
          <BaseLink
            :to="`/media/tv-shows/${showId}/seasons`"
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

const form = reactive({
  season_number: 1,
  title: '',
  description: '',
  poster_url: ''
})

const { isProcessing, error, execute } = useAsyncAction(
  () => mediaService.createSeason({
    season_number: form.season_number,
    title: form.title,
    description: form.description,
    poster_url: form.poster_url,
    media_id: showId
  }),
  {
    toast: {
      successMessage: 'Сезон создан',
      errorMessage: (e) => e?.data?.detail || `Ошибка ${e?.status || ''}`,
    },
    onSuccess: () => router.push(`/media/tv-shows/${showId}/seasons`),
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
  font-size: 18px;
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