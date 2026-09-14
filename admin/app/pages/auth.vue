<template>
  <div class="containner_login">
    <!-- Убедитесь, что handleLogin вызывается асинхронно через .prevent -->
    <form @submit.prevent="handleLogin">
      <h2>Вход</h2>
      <input
        v-model="loginData.username"
        type="text"
        placeholder="Введите логин"
      />

      <input
        v-model="loginData.password"
        type="password"
        placeholder="Введите пароль"
      />
      <button class="login_btn" type="submit">Войти</button>
    </form>
  </div>
</template>

<script setup>
    import { reactive } from 'vue'

    definePageMeta({
        layout: false
    })

    // Берем метод авторизации
    const { setAuthTest } = useAuth()

    const loginData = reactive({
        username: '',
        password: ''
    })

    const handleLogin = async () => {
        console.log('Данные для входа:', loginData)
        console.log("in")

        setAuthTest()

        return await navigateTo('/')
    }
</script>

<style>
    /* Центрирующий контейнер */
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
        100% {
            opacity: 1;
            transform: scale(1) translateY(0);
        }
    }

    /* Анимация для внутренних элементов */
    @keyframes itemAppear {
        100% {
            opacity: 1;
            transform: translateX(0);
        }
    }

    /* Красивая стеклянная форма */
    form {
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

    /* Исправлено: добавили .login_btn вместо login_btn */
    form h2, input, .login_btn {
        opacity: 0;
        transform: translateX(-30px);
        animation: itemAppear 0.6s cubic-bezier(0.34, 1.56, 0.64, 1) forwards;
    }

    /* Поочередная задержка появления */
    form h2 {
        animation-delay: 0.2s;
    }
    input:nth-of-type(1) {
        animation-delay: 0.35s;
    }
    input:nth-of-type(2) {
        animation-delay: 0.5s;
    }
    /* Исправлено: точка для класса */
    .login_btn {
        animation-delay: 0.65s;
    }

    form h2, form .title {
        margin: 0 0 10px 0;
        color: #ffffff;
        font-size: 24px;
        font-weight: 600;
        letter-spacing: 0.5px;
    }

    input {
        width: 100%;
        padding: 12px 16px;
        background: rgba(255, 255, 255, 0.9);
        border: 1px solid transparent;
        border-radius: 8px;
        font-size: 14px;
        color: #333;
        outline: none;
        box-sizing: border-box;
        transition: background 0.3s ease, border-color 0.3s ease, box-shadow 0.3s ease;
    }

    input:focus {
        background: #ffffff;
        border-color: #22C1C3;
        box-shadow: 0 0 0 4px rgba(34, 193, 195, 0.25);
    }

    /* Исправлено: точка для класса */
    .login_btn, input[type="submit"] {
        width: 100%;
        padding: 14px;
        margin-top: 10px;
        background: #ffffff;
        color: #22C1C3;
        border: none;
        border-radius: 8px;
        font-size: 15px;
        font-weight: 600;
        cursor: pointer;
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1);
        transition: background 0.3s ease, color 0.3s ease, box-shadow 0.3s ease;
    }

    /* Исправлено: точка для класса */
    .login_btn:hover, input[type="submit"]:hover {
        background: #22C1C3;
        color: #ffffff;
        transform: translateY(-2px) !important;
        box-shadow: 0 6px 20px rgba(34, 193, 195, 0.4);
    }

    /* Исправлено: точка для класса */
    .login_btn:active, input[type="submit"]:active {
        transform: translateY(0) !important;
    }

    input::placeholder {
        color: #999;
    }
</style>
