<template>
  <BaseForm class="user-form-container">
    <div v-if="pending" class="loading-state">
      Загрузка данных сериала...
    </div>

    <div v-else-if="loadError" class="error-state">
      <p>Произошла ошибка при загрузке: {{ loadError }}</p>
    </div>

    <div v-else class="form-content">
      <div class="form-section">
        <BaseInput
          v-model="form.title"
          label="Название"
          placeholder="Введите название сериала"
          :disabled="isProcessing"
          required
        />

        <BaseTextarea
          v-model="form.description"
          label="Описание"
          placeholder="Введите описание"
          :disabled="isProcessing"
          :rows="5"
          required
        />

        <BaseFormField label="Категории">
          <div class="checkbox-grid">
            <BaseCheckbox
              v-for="category in categories"
              :key="category.id"
              v-model="form.category_ids"
              :value="category.id"
              :label="category.name"
              :disabled="isProcessing"
            />
          </div>
        </BaseFormField>

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

      <hr class="form-divider" />

      <div class="form-section">
        <BaseButton
          variant="danger"
          :loading="isDeleting"
          loading-text="Удаление..."
          @click="handleDelete"
        >
          Удалить сериал
        </BaseButton>
      </div>

      <div v-if="error" class="error-state">{{ error }}</div>
    </div>
  </BaseForm>
</template>

<script setup lang="ts">
import { reactive, ref } from 'vue'
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
const loadError = ref<string | null>(null)

onMounted(async () => {
  const [catsResult, showResult] = await Promise.allSettled([
    categoryService.getAll(),
    mediaService.getById(showId)
  ])

  if (catsResult.status === 'fulfilled') {
    categories.value = catsResult.value
  } else {
    console.error('Ошибка загрузки категорий:', catsResult.reason)
  }

  if (showResult.status === 'fulfilled') {
    const show = showResult.value
    form.title = show.title
    form.description = show.description
    form.category_ids = (show.categories || [])
      .map((c: any) => c?.id)
      .filter((id: any): id is number => typeof id === 'number')
  } else {
    loadError.value = showResult.reason?.message || 'Ошибка загрузки сериала'
  }

  pending.value = false
})

const { isProcessing, error, execute: executeUpdate } = useAsyncAction(
  () => mediaService.update(showId, {
    title: form.title,
    description: form.description,
    category_ids: form.category_ids
  }),
  {
    toast: {
      successMessage: 'Сериал обновлён',
      errorMessage: (e) => e?.data?.detail || `Ошибка ${e?.status || ''}`,
    },
  }
)

const { isProcessing: isDeleting, execute: executeDelete } = useAsyncAction(
  () => mediaService.delete(showId),
  {
    toast: {
      successMessage: 'Сериал удалён',
      errorMessage: (e) => `Ошибка ${e?.status || ''}`,
    },
    onSuccess: () => router.push('/media/tv-shows'),
  }
)

const handleUpdate = () => executeUpdate().catch(() => {})

const handleDelete = async () => {
  if (!confirm('Вы уверены, что хотите удалить этот сериал?')) return
  await executeDelete().catch(() => {})
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

.action-bar {
  margin-top: 8px;
  display: flex;
  gap: 12px;
  align-items: center;
  flex-wrap: wrap;
}

.form-divider {
  border: 0;
  height: 1px;
  background: rgba(255, 255, 255, 0.15);
  margin: 8px 0;
}
</style>