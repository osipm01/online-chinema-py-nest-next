<template>
  <GlassPanel>
    <!-- Кнопка возврата к списку -->
    <div class="navigation-bar">
      <NuxtLink to="/media/categories" class="btn-back">← Назад к списку</NuxtLink>
    </div>

    <!-- Общая форма-оболочка интерфейса -->
    <BaseForm class="category-form-container">
      <div class="form-content">
        
        <!-- Заголовок страницы -->
        <div class="form-header">
          <h1 class="page-title">Создание новой категории</h1>
        </div>

        <!-- Поля формы -->
        <form @submit.prevent="handleCreate" class="form-section">
          
          <!-- Название категории -->
          <div class="input-field-group">
            <label for="name" class="field-label">Название категории</label>
            <input 
              id="name" 
              v-model="createForm.name" 
              type="text" 
              required
              class="custom-input"
              placeholder="Например: Ужастики, Комедии..."
            />
          </div>

          <!-- Ссылка на постер -->
          <div class="input-field-group">
            <label for="poster_url" class="field-label">Ссылка на постер (Poster URL)</label>
            <input 
              id="poster_url" 
              v-model="createForm.poster_url" 
              type="url" 
              required
              class="custom-input"
              placeholder="https://example.com"
            />
          </div>
          
          <!-- Кнопка отправки формы -->
          <div class="action-bar">
            <button type="submit" class="btn-action btn-success" :disabled="isProcessing">
              {{ isProcessing ? 'Создание...' : 'Создать категорию' }}
            </button>
          </div>

        </form>

      </div>
    </BaseForm>
  </GlassPanel>
</template>

<script setup lang="ts">
import { ref, reactive } from 'vue'

definePageMeta({
  middleware: 'auth',
  layout: 'default'
})

const router = useRouter()
const categoryApi = useCategory()

// Вспомогательное состояние для UI (блокировка отправки при запросе)
const isProcessing = ref(false)

// Реактивный объект формы строго по интерфейсу CreateCategoryDto
const createForm = reactive({
  name: '',
  poster_url: ''
})

// Обработчик создания категории
const handleCreate = async () => {
  try {
    isProcessing.value = true
    
    // Вызов метода create из вашего API-клиента
    await categoryApi.create({
      name: createForm.name,
      poster_url: createForm.poster_url
    })

      useToastify(`Успешер ${createForm.name}`, {
        type: "error",
        autoClose: 3000,
        theme: "auto"
      })
    
    // Перенаправляем пользователя обратно в список категорий после успеха
    router.push('/categories')
  } catch (err: any) {
      useToastify(`Ошибка ${err.status}`, {
        type: "error",
        autoClose: 3000,
        theme: "auto"
      })
    console.error('Ошибка при создании категории:', err)
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

/* Кастомные инпуты под стеклянный стиль интерфейса */
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

.action-bar {
  margin-top: 8px;
}

/* Кнопки и экшены */
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
</style>
