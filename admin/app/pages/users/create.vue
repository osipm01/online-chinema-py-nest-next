<template>
    <GalssPanel>
        <div class="form_container_">
            <h2 class="form_title">Создать пользователя</h2>

            <div class="form_field">
                <label class="form_label" for="username">Имя пользователя</label>
                <input
                    id="username"
                    v-model="form.username"
                    type="text"
                    class="form_input"
                    placeholder="Введите имя пользователя"
                    :disabled="loading"
                />
            </div>

            <div class="form_field">
                <label class="form_label" for="password">Пароль</label>
                <input
                    id="password"
                    v-model="form.password"
                    type="password"
                    class="form_input"
                    placeholder="Введите пароль"
                    :disabled="loading"
                />
            </div>

            <div class="form_field">
                <label class="form_label" for="role">Роль</label>
                <select
                    id="role"
                    v-model="form.role"
                    class="form_input form_select"
                    :disabled="loading"
                >
                    <option value="user">User</option>
                    <option value="admin">Admin</option>
                </select>
            </div>

            <div class="form_actions">
                <button
                    type="button"
                    class="btn btn_primary"
                    :disabled="loading"
                    @click="submit"
                >
                    {{ loading ? 'Создание...' : 'Создать' }}
                </button>

                <NuxtLink to="/users" class="btn btn_secondary">
                    Отмена
                </NuxtLink>
            </div>

            <div v-if="error" class="form_error">{{ error }}</div>
        </div>
    </GalssPanel>
</template>

<script setup lang="ts">
definePageMeta({
    middleware: 'auth',
    layout: 'default',
})

const adminUserService = useAdminUserService()
const router = useRouter()

const form = reactive({
    username: '',
    password: '',
    role: 'user',
})

const loading = ref(false)
const error = ref<string | null>(null)

const submit = async () => {
    if (!form.username || !form.password) {
        error.value = 'Заполните все поля'
        return
    }

    loading.value = true
    error.value = null

    try {
        await adminUserService.createUser(form)
        router.push('/users')
    } catch (e: any) {
        error.value = e.message || 'Ошибка при создании'
    } finally {
        loading.value = false
    }
}
</script>

<style lang="css" scoped>
.form_container_ {
    display: flex;
    flex-direction: column;
    gap: 18px;
    width: 100%;
    max-width: 420px;
    margin: 0 auto;
    padding: 32px;
    background: rgba(255, 255, 255, 0.96);
    border-radius: 16px;
    box-shadow: 0 10px 40px rgba(0, 0, 0, 0.18);
    box-sizing: border-box;
    color: #222;
}

.form_title {
    margin: 0 0 4px 0;
    font-size: 22px;
    font-weight: 600;
    text-align: center;
    color: #1a1a1a;
}

.form_field {
    display: flex;
    flex-direction: column;
    gap: 6px;
}

.form_label {
    font-size: 13px;
    font-weight: 500;
    color: #555;
}

.form_input {
    width: 100%;
    padding: 12px 14px;
    border-radius: 8px;
    border: 1px solid #dcdcdc;
    background: #ffffff;
    font-size: 14px;
    color: #222;
    outline: none;
    box-sizing: border-box;
    transition: border-color 0.2s ease, box-shadow 0.2s ease;
}

.form_input::placeholder {
    color: #aaa;
}

.form_input:focus {
    border-color: #22C1C3;
    box-shadow: 0 0 0 3px rgba(34, 193, 195, 0.2);
}

.form_input:disabled {
    background: #f5f5f5;
    cursor: not-allowed;
}

/* Кастомная стрелка у select */
.form_select {
    appearance: none;
    -webkit-appearance: none;
    background-image: url("data:image/svg+xml;charset=UTF-8,%3csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24' fill='none' stroke='%23555' stroke-width='2' stroke-linecap='round' stroke-linejoin='round'%3e%3cpolyline points='6 9 12 15 18 9'%3e%3c/polyline%3e%3c/svg%3e");
    background-repeat: no-repeat;
    background-position: right 12px center;
    background-size: 16px;
    padding-right: 38px;
    cursor: pointer;
}

.form_actions {
    display: flex;
    gap: 12px;
    margin-top: 6px;
}

.btn {
    flex: 1;
    display: inline-flex;
    align-items: center;
    justify-content: center;
    padding: 12px 16px;
    border-radius: 8px;
    font-size: 14px;
    font-weight: 600;
    text-decoration: none;
    cursor: pointer;
    border: 1px solid transparent;
    transition: background 0.2s ease, color 0.2s ease, box-shadow 0.2s ease, transform 0.15s ease;
    box-sizing: border-box;
}

.btn_primary {
    background: #22C1C3;
    color: #ffffff;
    box-shadow: 0 4px 14px rgba(34, 193, 195, 0.35);
}

.btn_primary:hover:not(:disabled) {
    background: #1aa9ab;
    transform: translateY(-1px);
    box-shadow: 0 6px 18px rgba(34, 193, 195, 0.45);
}

.btn_primary:active:not(:disabled) {
    transform: translateY(0);
}

.btn_primary:disabled {
    opacity: 0.6;
    cursor: not-allowed;
    box-shadow: none;
}

.btn_secondary {
    background: #ffffff;
    color: #444;
    border-color: #dcdcdc;
}

.btn_secondary:hover {
    background: #f2f2f2;
    color: #222;
}

.form_error {
    margin-top: 4px;
    padding: 10px 14px;
    border-radius: 8px;
    background: rgba(220, 53, 69, 0.1);
    color: #c0392b;
    border: 1px solid rgba(220, 53, 69, 0.3);
    font-size: 13px;
    text-align: center;
}
</style>