<template>
  <GalssPanel>
    <div class="page-inner">
      <!-- Кнопка создания -->
      <div class="navigation-bar">
        <BaseLink to="/users/create" variant="success">
          + Создать пользователя
        </BaseLink>
      </div>

      <div class="form-header">
        <h1 class="page-title">Пользователи</h1>
      </div>

      <div v-if="pending" class="loading-state">
        Загрузка списка пользователей...
      </div>

      <div v-else-if="error" class="error-state">
        Ошибка: {{ error }}
      </div>

      <div v-else-if="users.length > 0" class="users-list-container">
        <div
          v-for="user in users"
          :key="user.id"
          class="user-row-item"
        >
          <div class="user-info-block">
            <span class="user-name-text">{{ user.username }}</span>
            <span class="user-role-text">({{ user.role || 'user' }})</span>
          </div>

          <div class="user-actions-block">
            <BaseLink
              :to="`/users/${user.id}`"
              variant="primary"
              size="sm"
            >
              Редактировать
            </BaseLink>
            <BaseButton
              variant="danger"
              size="sm"
              :loading="isProcessing"
              @click="deleteUser(user.id)"
            >
              Удалить
            </BaseButton>
          </div>
        </div>
      </div>

      <div v-else class="empty-state-text">
        Список пользователей пуст.
      </div>
    </div>
  </GalssPanel>
</template>

<script setup lang="ts">
import type { IUser } from '~/types/AuthTypes'

definePageMeta({
  middleware: 'auth',
  layout: 'default'
})

const adminUserService = useAdminUserService()
const users = ref<IUser[]>([])
const pending = ref(true)
const error = ref<string | null>(null)

const fetchUsers = async () => {
  pending.value = true
  error.value = null
  try {
    users.value = await adminUserService.getAllUsers()
  } catch (e: any) {
    error.value = e.message || 'Ошибка при загрузке пользователей'
  } finally {
    pending.value = false
  }
}

const { isProcessing, execute: executeDelete } = useAsyncAction(
  (id: number) => adminUserService.deleteUser(id),
  {
    toast: {
      successMessage: 'Пользователь удалён',
      errorMessage: (e: any) => `Ошибка ${e?.status || ''}`,
    },
    onSuccess: () => fetchUsers(),
  }
)

const deleteUser = async (id: number) => {
  if (!confirm('Вы уверены, что хотите удалить этого пользователя?')) return
  await executeDelete(id).catch(() => {})
}

onMounted(fetchUsers)
</script>

<style scoped>
.page-inner {
  display: flex;
  flex-direction: column;
  gap: 24px;
  width: 100%;
  max-width: 900px;
  margin: 0 auto;
  box-sizing: border-box;
}

.navigation-bar {
  display: flex;
  justify-content: flex-start;
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

.users-list-container {
  display: flex;
  flex-direction: column;
  gap: 8px;
  width: 100%;
}

.user-row-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 16px;
  background: rgba(255, 255, 255, 0.08);
  border: 1px solid rgba(255, 255, 255, 0.12);
  border-radius: 8px;
  transition: background 0.2s ease;
}

.user-row-item:hover {
  background: rgba(255, 255, 255, 0.12);
}

.user-info-block {
  display: flex;
  align-items: center;
  gap: 8px;
}

.user-name-text {
  color: rgba(255, 255, 255, 0.95);
  font-size: 14px;
  font-weight: 600;
}

.user-role-text {
  color: rgba(255, 255, 255, 0.6);
  font-size: 13px;
}

.user-actions-block {
  display: flex;
  gap: 8px;
}
</style>