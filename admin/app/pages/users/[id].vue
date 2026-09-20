<template>
  <GalssPanel>
    <!-- Кнопка назад -->
    <div class="navigation-bar">
      <NuxtLink to="/users" class="btn-back">← Назад</NuxtLink>
    </div>

    <!-- Основная форма-оболочка -->
    <BaseForm class="user-form-container">

      <!-- Состояние загрузки -->
      <div v-if="pending" class="loading-state">
        Загрузка данных пользователя...
      </div>

      <!-- Состояние ошибки -->
      <div v-else-if="error" class="error-state">
        <p>Произошла ошибка при загрузке: {{ error }}</p>
      </div>

      <!-- Контент, если данные успешно загружены -->
      <div v-else class="form-content">

        <!-- Заголовок -->
        <div class="form-header">
          <h1 class="page-title">Пользователь №{{ userId }}</h1>
        </div>

        <!-- Редактирование -->
        <div class="form-section">
          <div class="input-field-group">
            <label for="username" class="field-label">Имя пользователя</label>
            <input
              id="username"
              v-model="form.username"
              type="text"
              required
              class="custom-input"
              placeholder="Введите имя пользователя"
              :disabled="isProcessing"
            />
          </div>

          <div class="input-field-group">
            <label for="password" class="field-label">Новый пароль</label>
            <input
              id="password"
              v-model="form.password"
              type="password"
              class="custom-input"
              placeholder="Оставьте пустым, чтобы не менять"
              :disabled="isProcessing"
            />
          </div>

          <div class="input-field-group">
            <label for="role" class="field-label">Роль</label>
            <select
              id="role"
              v-model="form.role"
              class="custom-input custom-select"
              :disabled="isProcessing"
            >
              <option value="user">User</option>
              <option value="admin">Admin</option>
            </select>
          </div>

          <div class="input-field-group checkbox-field-group">
            <label class="checkbox-label">
              <input
                type="checkbox"
                v-model="form.is_active"
                class="custom-checkbox"
                :disabled="isProcessing"
              />
              Активен
            </label>
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
            <NuxtLink to="/users" class="btn-action btn-secondary">
              Отмена
            </NuxtLink>
          </div>
        </div>

        <!-- Разделитель -->
        <hr class="form-divider" />

        <!-- Кнопка удаления -->
        <div class="form-section">
          <button
            @click="handleDelete"
            class="btn-action btn-danger"
            :disabled="isProcessing"
          >
            {{ isProcessing ? 'Удаление...' : 'Удалить пользователя' }}
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
const adminUserService = useAdminUserService()

const userId = Number(route.params.id)

const form = reactive({
  username: '',
  password: '',
  role: 'user',
  is_active: true
})

const pending = ref(true)
const isProcessing = ref(false)
const error = ref<string | null>(null)

onMounted(async () => {
  try {
    const user = await adminUserService.getUserById(userId)
    form.username = user.username
    form.role = user.role || 'user'
    // form.is_active = user.is_active ?? true
  } catch (e: any) {
    error.value = e.message || 'Ошибка загрузки пользователя'
  } finally {
    pending.value = false
  }
})

const handleUpdate = async () => {
  try {
    isProcessing.value = true
    error.value = null

    const updateData: any = {
      username: form.username,
      role: form.role,
      is_active: form.is_active
    }

    if (form.password) {
      updateData.password = form.password
    }

    await adminUserService.patchUser(userId, updateData)

    useToastify(`Пользователь обновлён`, {
      type: "success",
      autoClose: 3000,
      theme: "auto"
    })

    router.push('/users')
  } catch (err: any) {
    error.value = err.message || 'Ошибка при сохранении'
    useToastify(`Ошибка ${err.status || ''}`, {
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
  if (!confirm('Вы уверены, что хотите удалить этого пользователя?')) return

  try {
    isProcessing.value = true
    await adminUserService.deleteUser(userId)
    router.push('/users')
  } catch (err: any) {
    useToastify(`Ошибка ${err.status || ''}`, {
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

.input-field-group {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.checkbox-field-group {
  flex-direction: row;
  align-items: center;
}

.field-label {
  color: rgba(255, 255, 255, 0.8);
  font-size: 14px;
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