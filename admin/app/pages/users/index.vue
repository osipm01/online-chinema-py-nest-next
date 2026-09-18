<style lang="css" scoped>
.users_container {
    width: 100%;
    height: 100%;
    display: flex;
    flex-direction: column;
    gap: 10px;
}

.user_row {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 10px;
    border-bottom: 1px solid rgba(255, 255, 255, 0.1);
}

.actions {
    display: flex;
    gap: 10px;
}

.error {
    color: #ff6b6b;
}
</style>

<template>
    <GalssPanel>
        <div class="users_container">
            <div class="header" style="display: flex; justify-content: space-between; margin-bottom: 20px;">
                <h2>Пользователи</h2>
                <NuxtLink to="/users/create">
                    <UiButton>Создать пользователя</UiButton>
                </NuxtLink>
            </div>

            <div v-if="pending">Загрузка...</div>
            <div v-else-if="error" class="error">{{ error }}</div>
            
            <div v-else>
                <div v-for="user in users" :key="user.id" class="user_row">
                    <div>
                        <strong>{{ user.username }}</strong>
                        <span style="margin-left: 10px; opacity: 0.7;">({{ user.role || 'user' }})</span>
                        <!-- <span v-if="!user.is_active" style="color: #ff6b6b; margin-left: 10px;">[Заблокирован]</span> -->
                    </div>
                    
                    <div class="actions">
                        <NuxtLink :to="`/users/${user.id}`">
                            <UiButton size="small">Редактировать</UiButton>
                        </NuxtLink>
                        <UiButton size="small" variant="danger" @click="deleteUser(user.id)">
                            Удалить
                        </UiButton>
                    </div>
                </div>
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

const deleteUser = async (id: number) => {
    if (!confirm('Вы уверены, что хотите удалить этого пользователя?')) return
    
    try {
        await adminUserService.deleteUser(id)
        await fetchUsers() // Обновить список
    } catch (e: any) {
        alert(e.message || 'Ошибка при удалении')
    }
}

onMounted(() => {
    fetchUsers()
})
</script>