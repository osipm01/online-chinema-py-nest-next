<template>
  <GalssPanel>
    <div class="navigation-bar">
      <NuxtLink :to="`/media/tv-shows/${showId}/seasons`" class="btn-back">← Назад к сезонам</NuxtLink>
    </div>

    <BaseForm class="user-form-container">
      <div class="form-content">
        <div class="form-header">
          <h1 class="page-title">Новый сезон</h1>
        </div>

        <form @submit.prevent="handleCreate" class="form-section">
          <div class="input-field-group">
            <label for="season_number" class="field-label">Номер сезона</label>
            <input
              id="season_number"
              v-model.number="form.season_number"
              type="number"
              min="1"
              required
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
            <button type="submit" class="btn-action btn-success" :disabled="isProcessing">
              {{ isProcessing ? 'Создание...' : 'Создать сезон' }}
            </button>
            <NuxtLink :to="`/media/tv-shows/${showId}/seasons`" class="btn-action btn-secondary">
              Отмена
            </NuxtLink>
          </div>
        </form>

        <div v-if="errorMessage" class="error-state">
          {{ errorMessage }}
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

const isProcessing = ref(false)
const errorMessage = ref<string | null>(null)

const form = reactive({
  season_number: 1,
  title: '',
  description: '',
  poster_url: ''
})

const handleCreate = async () => {
  try {
    isProcessing.value = true
    errorMessage.value = null

    await mediaService.createSeason({
      season_number: form.season_number,
      title: form.title,
      description: form.description,
      poster_url: form.poster_url,
      media_id: showId
    })

    useToastify('Сезон создан', {
      type: 'success',
      autoClose: 3000,
      theme: 'auto'
    })

    router.push(`/media/tv-shows/${showId}/seasons`)
  } catch (err: any) {
    errorMessage.value = err.message || 'Ошибка при создании'
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
  gap: 20px;
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

.btn-secondary {
  background-color: rgba(255, 255, 255, 0.15);
  color: #ffffff;
  border: 1px solid rgba(255, 255, 255, 0.3);
}

.btn-secondary:hover {
  background-color: rgba(255, 255, 255, 0.25);
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