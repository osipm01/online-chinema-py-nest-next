<template>
  <div class="containner_login">
    <form @submit.prevent="handleSubmit">
      <h2>Вход</h2>

      <BaseInput
        v-model="loginData.username"
        placeholder="Введите логин"
        :disabled="isProcessing"
        class="login-input"
      />

      <BaseInput
        v-model="loginData.password"
        type="password"
        placeholder="Введите пароль"
        :disabled="isProcessing"
        class="login-input"
      />

      <BaseButton
        native-type="submit"
        :loading="isProcessing"
        loading-text="Входим..."
        class="login_btn"
      >
        Войти
      </BaseButton>

      <p v-if="error" class="error">{{ error }}</p>
    </form>
  </div>
</template>

<script setup lang="ts">
import { reactive } from 'vue'

definePageMeta({
  layout: false,
})

const { login } = useAuth()

const loginData = reactive({
  username: '',
  password: '',
})

const { isProcessing, error, execute } = useAsyncAction(
  () => login(loginData.username, loginData.password),
  {
    toast: { silent: true },
    onSuccess: () => navigateTo('/'),
  }
)

const handleSubmit = async () => {
  try {
    await execute()
  } catch (e: any) {
    // Перезаписываем error читаемым текстом под DRF-ответы
    error.value =
      e?.data?.detail ||
      e?.data?.username?.[0] ||
      e?.data?.password?.[0] ||
      'Не удалось войти. Проверьте логин и пароль.'
  }
}
</script>

<style>
.containner_login {
  display: flex;
  justify-content: center;
  align-items: center;
  max-width: 100vw;
  height: 100vh;
  background: linear-gradient(48deg, rgba(34, 193, 195, 1) 0%, rgba(144, 190, 120, 1) 50%, rgba(253, 187, 45, 1) 100%);
  font-family: 'Poppins', sans-serif;
  overflow: hidden;
}

@keyframes formAppear {
  100% { opacity: 1; transform: scale(1) translateY(0); }
}

@keyframes itemAppear {
  100% { opacity: 1; transform: translateX(0); }
}

.containner_login form {
  display: flex;
  flex-direction: column;
  gap: 16px;
  width: 100%;
  max-width: 400px;
  background: rgba(255, 255, 255, 0.15);
  backdrop-filter: blur(10px);
  -webkit-backdrop-filter: blur(10px);
  border-radius: 16px;
  border: 1px solid rgba(255, 255, 255, 0.3);
  padding: 35px;
  box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.15);
  box-sizing: border-box;

  opacity: 0;
  transform: scale(0.9) translateY(20px);
  animation: formAppear 0.8s cubic-bezier(0.25, 1, 0.5, 1) forwards;
}

.containner_login form h2,
.containner_login :deep(.login-input),
.containner_login :deep(.login_btn) {
  opacity: 0;
  transform: translateX(-30px);
  animation: itemAppear 0.6s cubic-bezier(0.34, 1.56, 0.64, 1) forwards;
}

.containner_login form h2 { animation-delay: 0.2s; }
.containner_login :deep(.login-input):nth-of-type(1) { animation-delay: 0.35s; }
.containner_login :deep(.login-input):nth-of-type(2) { animation-delay: 0.5s; }
.containner_login :deep(.login_btn) { animation-delay: 0.65s; }

.containner_login form h2 {
  margin: 0 0 10px 0;
  color: #ffffff;
  font-size: 24px;
  font-weight: 600;
  letter-spacing: 0.5px;
}

/* Переопределяем поля BaseInput внутри логина */
.containner_login :deep(.login-input .custom-input) {
  background: rgba(255, 255, 255, 0.9);
  border: 1px solid transparent;
  transition: background 0.3s ease, border-color 0.3s ease, box-shadow 0.3s ease;
}

.containner_login :deep(.login-input .custom-input:focus) {
  background: #ffffff;
  border-color: #22C1C3;
  box-shadow: 0 0 0 4px rgba(34, 193, 195, 0.25);
}

/* Скрываем label-обёртку, если она пустая */
.containner_login :deep(.login-input .field-label) {
  display: none;
}

/* Кнопка логина */
.containner_login :deep(.login_btn.btn-action) {
  width: 100%;
  padding: 14px;
  margin-top: 10px;
  background: #ffffff;
  color: #22C1C3;
  border-radius: 8px;
  font-size: 15px;
  font-weight: 600;
  box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1);
  transition: background 0.3s ease, color 0.3s ease, box-shadow 0.3s ease, transform 0.3s ease;
}

.containner_login :deep(.login_btn.btn-action:hover:not(:disabled)) {
  background: #22C1C3;
  color: #ffffff;
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(34, 193, 195, 0.4);
}

.containner_login :deep(.login_btn.btn-action:active:not(:disabled)) {
  transform: translateY(0);
}

.containner_login .error {
  color: #fff;
  background: rgba(220, 53, 69, 0.85);
  padding: 10px 14px;
  border-radius: 8px;
  font-size: 13px;
  margin: 0;
  text-align: center;
}
</style>