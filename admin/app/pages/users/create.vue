<template>
  <GalssPanel>
    <!-- Кнопка возврата к списку -->
    <div class="navigation-bar">
      <NuxtLink to="/users" class="btn-back">← Назад к списку</NuxtLink>
    </div>

    <!-- Общая форма-оболочка интерфейса -->
    <BaseForm class="user-form-container">
      <div class="form-content">

        <!-- Заголовок страницы -->
        <div class="form-header">
          <h1 class="page-title">Создание нового пользователя</h1>
        </div>

        <!-- Поля формы -->
        <form @submit.prevent="handleCreate" class="form-section">

          <!-- Имя пользователя -->
          <div class="input-field-group">
            <label for="username" class="field-label">Имя пользователя</label>
            <input
              id="username"
              v-model="createForm.username"
              type="text"
              required
              class="custom-input"
              placeholder="Введите имя пользователя"
              :disabled="isProcessing"
            />
          </div>

          <!-- Пароль -->
          <div class="input-field-group">
            <label for="password" class="field-label">Пароль</label>
            <input
              id="password"
              v-model="createForm.password"
              type="password"
              required
              class="custom-input"
              placeholder="Введите пароль"
              :disabled="isProcessing"
            />
          </div>

          <!-- Роль -->
          <div class="input-field-group">
            <label for="role" class="field-label">Роль</label>
            <select
              id="role"
              v-model="createForm.role"
              class="custom-input custom-select"
              :disabled="isProcessing"
            >
              <option value="user">User</option>
              <option value="admin">Admin</option>
            </select>
          </div>

          <!-- Кнопка отправки формы -->
          <div class="action-bar">
            <button type="submit" class="btn-action btn-success" :disabled="isProcessing">
              {{ isProcessing ? 'Создание...' : 'Создать пользователя' }}
            </button>
            <NuxtLink to="/users" class="btn-action btn-secondary">
              Отмена
            </NuxtLink>
          </div>

        </form>

        <!-- Сообщение об ошибке -->
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

const router = useRouter()
const adminUserService = useAdminUserService()

const isProcessing = ref(false)
const errorMessage = ref<string | null>(null)

const createForm = reactive({
  username: '',
  password: '',
  role: 'user'
})

const handleCreate = async () => {
  if (!createForm.username || !createForm.password) {
    errorMessage.value = 'Заполните все поля'
    return
  }

  try {
    isProcessing.value = true
    errorMessage.value = null

    await adminUserService.createUser({
      username: createForm.username,
      password: createForm.password,
      role: createForm.role
    })

    useToastify(`Пользователь ${createForm.username} создан`, {
      type: "success",
      autoClose: 3000,
      theme: "auto"
    })

    router.push('/users')
  } catch (err: any) {
    errorMessage.value = err.message || 'Ошибка при создании'
    useToastify(`Ошибка ${err.status || ''}`, {
      type: "error",
      autoClose: 3000,
      theme: "auto"
    })
    console.error('Ошибка при создании пользователя:', err)
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

.custom-input:disabled {
  background: rgba(255, 255, 255, 0.5);
  cursor: not-allowed;
}

.custom-select {
  appearance: none;
  -webkit-appearance: none;
  background-image: url("data:image/svg+xml;charset=UTF-8,%3csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24' fill='none' stroke='%23555' stroke-width='2' stroke-linecap='round' stroke-linejoin='round'%3e%3cpolyline points='6 9 12 15 18 9'%3e%3c/polyline%3e%3c/svg%3e");
  background-repeat: no-repeat;
  background-position: right 12px center;
  background-size: 16px;
  padding-right: 38px;
  cursor: pointer;
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