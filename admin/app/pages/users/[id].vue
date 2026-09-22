<template>
  <GalssPanel>
    <BaseBackLink to="/users" />

    <BaseForm class="user-form-container">
      <!-- Загрузка -->
      <div v-if="pending" class="loading-state">
        Загрузка данных пользователя...
      </div>

      <!-- Ошибка загрузки -->
      <div v-else-if="loadError" class="error-state">
        <p>Произошла ошибка при загрузке: {{ loadError }}</p>
      </div>

      <!-- Контент -->
      <div v-else class="form-content">
        <div class="form-header">
          <h1 class="page-title">Пользователь №{{ userId }}</h1>
        </div>

        <div class="form-section">
          <BaseInput
            v-model="form.username"
            label="Имя пользователя"
            placeholder="Введите имя пользователя"
            :disabled="isProcessing"
            required
          />

          <BaseInput
            v-model="form.password"
            type="password"
            label="Новый пароль"
            placeholder="Оставьте пустым, чтобы не менять"
            :disabled="isProcessing"
          />

          <BaseSelect
            v-model="form.role"
            label="Роль"
            :disabled="isProcessing"
          >
            <option value="user">User</option>
            <option value="admin">Admin</option>
          </BaseSelect>

          <BaseCheckbox
            v-model="form.is_active"
            label="Активен"
            :disabled="isProcessing"
          />

          <div class="action-bar">
            <BaseButton
              variant="success"
              :loading="isProcessing"
              loading-text="Сохранение..."
              @click="handleUpdate"
            >
              Сохранить изменения
            </BaseButton>
            <BaseLink to="/users" variant="secondary">
              Отмена
            </BaseLink>
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
            Удалить пользователя
          </BaseButton>
        </div>

        <div v-if="error" class="error-state">{{ error }}</div>
      </div>
    </BaseForm>
  </GalssPanel>
</template>

<script setup lang="ts">
import { reactive, ref } from 'vue'

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
const loadError = ref<string | null>(null)

onMounted(async () => {
  try {
    const user = await adminUserService.getUserById(userId)
    form.username = user.username
    form.role = user.role || 'user'
    // form.is_active = user.is_active ?? true
  } catch (e: any) {
    loadError.value = e.message || 'Ошибка загрузки пользователя'
  } finally {
    pending.value = false
  }
})

const { isProcessing, error, execute: executeUpdate } = useAsyncAction(
  () => {
    const updateData: Record<string, unknown> = {
      username: form.username,
      role: form.role,
      is_active: form.is_active
    }
    if (form.password) updateData.password = form.password
    return adminUserService.patchUser(userId, updateData)
  },
  {
    toast: {
      successMessage: 'Пользователь обновлён',
      errorMessage: (e: any) => e?.data?.detail || `Ошибка ${e?.status || ''}`,
    },
    onSuccess: () => router.push('/users'),
  }
)

const { isProcessing: isDeleting, execute: executeDelete } = useAsyncAction(
  () => adminUserService.deleteUser(userId),
  {
    toast: {
      successMessage: 'Пользователь удалён',
      errorMessage: (e: any) => `Ошибка ${e?.status || ''}`,
    },
    onSuccess: () => router.push('/users'),
  }
)

const handleUpdate = () => executeUpdate().catch(() => {})

const handleDelete = async () => {
  if (!confirm('Вы уверены, что хотите удалить этого пользователя?')) return
  await executeDelete().catch(() => {})
}
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

.action-bar {
  margin-top: 8px;
  display: flex;
  gap: 12px;
  align-items: center;
}
</style>