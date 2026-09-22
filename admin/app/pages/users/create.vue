<template>
  <GalssPanel>
    <BaseBackLink to="/users" label="← Назад к списку" />

    <BaseForm class="user-form-container">
      <div class="form-content">
        <div class="form-header">
          <h1 class="page-title">Создание нового пользователя</h1>
        </div>

        <form @submit.prevent="handleSubmit" class="form-section">
          <BaseInput
            v-model="createForm.username"
            label="Имя пользователя"
            placeholder="Введите имя пользователя"
            :disabled="isProcessing"
            required
          />

          <BaseInput
            v-model="createForm.password"
            type="password"
            label="Пароль"
            placeholder="Введите пароль"
            :disabled="isProcessing"
            required
          />

          <BaseSelect
            v-model="createForm.role"
            label="Роль"
            :disabled="isProcessing"
          >
            <option value="user">User</option>
            <option value="admin">Admin</option>
          </BaseSelect>

          <div class="action-bar">
            <BaseButton
              native-type="submit"
              variant="success"
              :loading="isProcessing"
              loading-text="Создание..."
            >
              Создать пользователя
            </BaseButton>
            <BaseLink to="/users" variant="secondary">
              Отмена
            </BaseLink>
          </div>
        </form>

        <div v-if="validationError" class="error-state">
          {{ validationError }}
        </div>
        <div v-else-if="error" class="error-state">
          {{ error }}
        </div>
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

const router = useRouter()
const adminUserService = useAdminUserService()

const createForm = reactive({
  username: '',
  password: '',
  role: 'user'
})

const validationError = ref<string | null>(null)

const { isProcessing, error, execute } = useAsyncAction(
  () => adminUserService.createUser({
    username: createForm.username,
    password: createForm.password,
    role: createForm.role
  }),
  {
    toast: {
      successMessage: () => `Пользователь ${createForm.username} создан`,
      errorMessage: (e: any) => e?.data?.detail || `Ошибка ${e?.status || ''}`,
    },
    onSuccess: () => router.push('/users'),
  }
)

const handleSubmit = () => {
  validationError.value = null
  if (!createForm.username || !createForm.password) {
    validationError.value = 'Заполните все поля'
    return
  }
  execute().catch(() => {})
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
  gap: 20px;
}

.action-bar {
  margin-top: 8px;
  display: flex;
  gap: 12px;
  align-items: center;
}
</style>