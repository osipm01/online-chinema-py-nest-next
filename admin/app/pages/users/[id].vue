<style lang="css" scoped>
.form_container {
    display: flex;
    flex-direction: column;
    gap: 15px;
    max-width: 400px;
    margin: 0 auto;
}
</style>

<template>
    <GalssPanel>
        <div class="form_container">
            <h2>Редактировать пользователя</h2>
            
            <div v-if="pending">Загрузка...</div>
            
            <template v-else>
                <UiInput v-model="form.username" placeholder="Имя пользователя" />
                <UiInput v-model="form.password" type="password" placeholder="Новый пароль (оставьте пустым, чтобы не менять)" />
                
                <label>Роль:</label>
                <select v-model="form.role" class="ui-select">
                    <option value="user">User</option>
                    <option value="admin">Admin</option>
                </select>

                <label>
                    <input type="checkbox" v-model="form.is_active" />
                    Активен
                </label>

                <div style="display: flex; gap: 10px; margin-top: 10px;">
                    <UiButton @click="submit" :disabled="loading">
                        {{ loading ? 'Сохранение...' : 'Сохранить' }}
                    </UiButton>
                    <NuxtLink to="/users">
                        <UiButton variant="secondary">Отмена</UiButton>
                    </NuxtLink>
                </div>
                
                <div v-if="error" style="color: red;">{{ error }}</div>
            </template>
        </div>
    </GalssPanel>
</template>

<script setup lang="ts">
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
    password: '', // Пустое поле означает "не менять"
    role: 'user',
    is_active: true
})

const pending = ref(true)
const loading = ref(false)
const error = ref<string | null>(null)

// Загрузка данных пользователя
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

const submit = async () => {
    loading.value = true
    error.value = null
    
    // Формируем DTO, исключая пустой пароль
    const updateData: any = {
        username: form.username,
        role: form.role,
        is_active: form.is_active
    }
    
    if (form.password) {
        updateData.password = form.password
    }
    
    try {
        await adminUserService.patchUser(userId, updateData)
        router.push('/users')
    } catch (e: any) {
        error.value = e.message || 'Ошибка при сохранении'
    } finally {
        loading.value = false
    }
}
</script>