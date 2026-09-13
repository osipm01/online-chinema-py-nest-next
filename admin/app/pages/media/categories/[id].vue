<template>
  <GlassPanel>
    <!-- Кнопка назад вынесена над формой -->
    <div class="navigation-bar">
      <NuxtLink to="/media/categories" class="btn-back">← Назад</NuxtLink>
    </div>

    <!-- Основная форма-оболочка интерфейса -->
    <BaseForm class="category-form-container">
      
      <!-- Состояние загрузки и ошибок -->
      <div v-if="status === 'pending'" class="loading-state">
        Загрузка данных категории...
      </div>

      <div v-else-if="error" class="error-state">
        <p>Произошла ошибка при загрузке: {{ error.message }}</p>
      </div>

      <!-- Контент, если данные успешно загружены -->
      <div v-else-if="category" class="form-content">
        
        <!-- Заголовок и кнопка удаления -->
        <div class="form-header">
          <h1 class="page-title">Категория №{{ categoryId }}</h1>
          <button @click="handleDelete" class="btn-action btn-danger" :disabled="isProcessing">
            {{ isProcessing ? 'Удаление...' : 'Удалить категорию' }}
          </button>
        </div>

        <!-- Редактирование названия -->
        <div class="form-section">
          <div class="input-field-group">
            <label for="name" class="field-label">Название категории</label>
            <input 
              id="name" 
              v-model="editForm.name" 
              type="text" 
              required
              class="custom-input"
              placeholder="Введите название"
            />
          </div>
          
          <button @click="handleUpdate" class="btn-action btn-success" :disabled="isProcessing">
            {{ isProcessing ? 'Сохранение...' : 'Сохранить изменения' }}
          </button>
        </div>

        <!-- Разделитель -->
        <hr class="form-divider" />

        <!-- Блок управления медиа -->
        <div class="form-section media-section">
          <h2 class="section-title">Привязанные медиафайлы</h2>
          
          <!-- Инпут привязки медиа -->
          <div class="media-attach-bar">
            <input 
              v-model.number="newMediaId" 
              type="number" 
              class="custom-input input-short"
              placeholder="ID медиафайла" 
              min="1"
            />
            <button @click="handleAddMedia" :disabled="!newMediaId || isProcessing" class="btn-action btn-primary">
              Привязать медиа
            </button>
          </div>

          <!-- Список текущих медиафайлов -->
          <div v-if="statusMedia === 'pending'" class="loading-state-sub">Загрузка медиа...</div>
          
          <ul v-else-if="categoryMedia?.media && categoryMedia.media.length > 0" class="media-list-container">
            <li v-for="item in categoryMedia.media" :key="item.id" class="media-row-item">
              <span class="media-info-text">ID: {{ item.id }} — {{ item.name || 'Медиафайл' }}</span>
              <button @click="handleRemoveMedia(item.id)" class="btn-action btn-warning" :disabled="isProcessing">
                Отвязать
              </button>
            </li>
          </ul>
          
          <p v-else class="empty-media-text">К этой категории пока не привязано ни одного медиафайла.</p>
        </div>

      </div>
    </BaseForm>
  </GlassPanel>
</template>

<script setup lang="ts">
import { ref, reactive, watch } from 'vue'

definePageMeta({
  middleware: 'auth',
  layout: 'default'
})

const route = useRoute()
const router = useRouter()
const categoryApi = useCategory()

const categoryId = Number(route.params.id)
const isProcessing = ref(false)
const newMediaId = ref<number | null>(null)

const editForm = reactive({
  name: ''
})

// Получение данных
const { data: category, status, error, refresh: refreshCategory } = await useAsyncData(
  `category-${categoryId}`,
  () => categoryApi.getById(categoryId)
)

if (category.value) {
  editForm.name = category.value.name
}

watch(category, (newVal) => {
  if (newVal) editForm.name = newVal.name
})

const { data: categoryMedia, status: statusMedia, refresh: refreshMedia } = await useAsyncData(
  `category-media-${categoryId}`,
  () => categoryApi.getMedia(categoryId)
)

// Обработчики действий
const handleUpdate = async () => {
  try {
    isProcessing.value = true
    await categoryApi.update(categoryId, { name: editForm.name })
    await refreshCategory()
  } catch (err: any) {
    useToastify(`Ошибка ${err.status}`, {
        type: "error",
        autoClose: 3000,
        theme: "auto"
      })
    console.error(err)
  } finally {
    isProcessing.value = false
  }
}

const handleDelete = async () => {
  if (!confirm('Вы уверены, что хотите удалить эту категорию?')) return
  try {
    isProcessing.value = true
    await categoryApi.delete(categoryId)
    router.push('/categories')
  } catch (err: any) {
    useToastify(`Ошибка ${err.status}`, {
        type: "error",
        autoClose: 3000,
        theme: "auto"
      })
    console.error(err)
  } finally {
    isProcessing.value = false
  }
}

const handleAddMedia = async () => {
  if (!newMediaId.value) return
  try {
    isProcessing.value = true
    await categoryApi.addMedia(categoryId, newMediaId.value)
    newMediaId.value = null
    await refreshMedia()
  } catch (err: any) {
    useToastify(`Ошибка ${err.status}`, {
        type: "error",
        autoClose: 3000,
        theme: "auto"
      })
    console.error(err)
  } finally {
    isProcessing.value = false
  }
}

const handleRemoveMedia = async (mediaId: number) => {
  if (!confirm('Отвязать этот медиафайл от категории?')) return
  try {
    isProcessing.value = true
    await categoryApi.removeMedia(categoryId, mediaId)
    await refreshMedia()
  } catch (err: any) {
    useToastify(`Ошибка ${err.status}`, {
        type: "error",
        autoClose: 3000,
        theme: "auto"
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

/* Кастомные инпуты под стеклянный стиль */
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

.input-short {
  max-width: 200px;
}

/* Кнопки и экшены */
.btn-action {
  padding: 10px 20px;
  border-radius: 8px;
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  border: none;
  transition: opacity 0.2s, transform 0.1s;
  display: inline-flex;
  align-items: center;
  justify-content: center;
}

.btn-action:active {
  transform: scale(0.98);
}

.btn-action:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.btn-success { background-color: #2ec4b6; color: white; width: max-content; }
.btn-danger { background-color: #e71d36; color: white; }
.btn-primary { background-color: #007a; color: white; }
.btn-warning { background-color: #ff9f1c; color: white; padding: 6px 12px; font-size: 13px; }

/* Линия разделения секций */
.form-divider {
  border: 0;
  height: 1px;
  background: rgba(255, 255, 255, 0.15);
  margin: 8px 0;
}

/* Секция медиафайлов */
.section-title {
  color: #ffffff;
  font-size: 18px;
  font-weight: 500;
  margin: 0;
}

.media-attach-bar {
  display: flex;
  gap: 12px;
}

.media-list-container {
  list-style: none;
  padding: 0;
  margin: 8px 0 0 0;
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.media-row-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 16px;
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 8px;
}

.media-info-text {
  color: rgba(255, 255, 255, 0.9);
  font-size: 14px;
}

.empty-media-text {
  color: rgba(255, 255, 255, 0.5);
  font-style: italic;
  font-size: 14px;
}

.loading-state, .error-state {
  color: #ffffff;
  padding: 20px 0;
  text-align: center;
}
</style>
