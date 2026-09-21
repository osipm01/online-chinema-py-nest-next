<template>
  <GalssPanel>
    <div class="navigation-bar">
      <NuxtLink to="/media/tv-shows" class="btn-back">← Назад</NuxtLink>
    </div>

    <BaseForm class="user-form-container">
      <div v-if="pending" class="loading-state">
        Загрузка данных сериала...
      </div>

      <div v-else-if="error" class="error-state">
        <p>Произошла ошибка при загрузке: {{ error }}</p>
      </div>

      <div v-else class="form-content">
        <div class="form-header">
          <h1 class="page-title">Сериал №{{ showId }}</h1>
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
              placeholder="Введите название сериала"
              :disabled="isProcessing"
            />
          </div>

          <div class="input-field-group">
            <label for="description" class="field-label">Описание</label>
            <textarea
              id="description"
              v-model="form.description"
              required
              class="custom-input custom-textarea"
              placeholder="Введите описание"
              :disabled="isProcessing"
            ></textarea>
          </div>

          <div class="input-field-group">
            <label class="field-label">Категории</label>
            <div class="checkbox-grid">
              <label
                v-for="category in categories"
                :key="category.id"
                class="checkbox-label"
              >
                <input
                  type="checkbox"
                  class="custom-checkbox"
                  :value="category.id"
                  v-model="form.category_ids"
                  :disabled="isProcessing"
                />
                {{ category.name }}
              </label>
            </div>
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
              Управление сезонами
            </NuxtLink>
            <NuxtLink to="/media/tv-shows" class="btn-action btn-secondary">
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
            {{ isProcessing ? 'Удаление...' : 'Удалить сериал' }}
          </button>
        </div>
      </div>
    </BaseForm>
  </GalssPanel>
</template>

<script setup lang="ts">
import { ref, reactive } from 'vue'
import type { Category } from '~/types/CategoryTypes'

definePageMeta({
  middleware: 'auth',
  layout: 'default'
})

const route = useRoute()
const router = useRouter()
const mediaService = useMedia()
const categoryService = useCategory()

const showId = Number(route.params.id)

const form = reactive({
  title: '',
  description: '',
  category_ids: [] as number[]
})

const categories = ref<Category[]>([])
const pending = ref(true)
const isProcessing = ref(false)
const error = ref<string | null>(null)

const fetchCategories = async () => {
  try {
    categories.value = await categoryService.getAll()
  } catch (e) {
    console.error('Ошибка загрузки категорий:', e)
  }
}

onMounted(async () => {
  fetchCategories()
  try {
    const show = await mediaService.getById(showId)
    form.title = show.title
    form.description = show.description
    form.category_ids = (show.categories || [])
      .map((c: any) => c?.id)
      .filter((id: any): id is number => typeof id === 'number')
  } catch (e: any) {
    error.value = e.message || 'Ошибка загрузки сериала'
  } finally {
    pending.value = false
  }
})

const handleUpdate = async () => {
  try {
    isProcessing.value = true
    error.value = null

    await mediaService.update(showId, {
      title: form.title,
      description: form.description,
      category_ids: form.category_ids
    })

    useToastify('Сериал обновлён', {
      type: 'success',
      autoClose: 3000,
      theme: 'auto'
    })

    router.push('/tv-shows')
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
  if (!confirm('Вы уверены, что хотите удалить этот сериал?')) return

  try {
    isProcessing.value = true
    await mediaService.delete(showId)
    router.push('/tv-shows')
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

.checkbox-grid {
  display: flex;
  flex-wrap: wrap;
  gap: 12px 20px;
}

.checkbox-label {
  display: flex;
  align-items: center;
  gap: 8px;
  color: rgba(255, 255, 255, 0.8);
  font-size: 14px;
  cursor: pointer;
  user-select: none;
}

.custom-checkbox {
  width: 18px;
  height: 18px;
  accent-color: #2ec4b6;
  cursor: pointer;
}

.action-bar {
  margin-top: 8px;
  display: flex;
  gap: 12px;
  align-items: center;
  flex-wrap: wrap;
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