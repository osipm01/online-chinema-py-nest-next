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

    /* Анимация для внутренних элементов (только конечная точка) */
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

        /* ХАРДКОД НАЧАЛЬНОГО СОСТОЯНИЯ: жестко скрываем форму ДО старта анимации */
        opacity: 0;
        transform: scale(0.9) translateY(20px);

        /* Подключение анимации появления формы */
        animation: formAppear 0.8s cubic-bezier(0.25, 1, 0.5, 1) forwards;
    }

    /* Общие правила анимации для всех внутренних элементов */
    form h2, input, button {
        /* ХАРДКОД НАЧАЛЬНОГО СОСТОЯНИЯ: скрываем элементы ДО старта анимации */
        opacity: 0;
        transform: translateX(-30px);
        
        animation: itemAppear 0.6s cubic-bezier(0.34, 1.56, 0.64, 1) forwards;
    }

    /* Поочередная задержка появления (каскад) */
    form h2 {
        animation-delay: 0.2s;
    }
    input:nth-of-type(1) {
        animation-delay: 0.35s;
    }
    input:nth-of-type(2) {
        animation-delay: 0.5s;
    }
    button {
        animation-delay: 0.65s;
    }

    /* Заголовок "Вход" */
    form h2, form .title {
        margin: 0 0 10px 0;
        color: #ffffff;
        font-size: 24px;
        font-weight: 600;
        letter-spacing: 0.5px;
    }

    /* Современные поля ввода */
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
        /* Изменено: Убрали transform из общего transition, чтобы свойства ховера/фокуса не конфликтовали с первоначальным вылетом */
        transition: background 0.3s ease, border-color 0.3s ease, box-shadow 0.3s ease;
    }

    /* Анимация при клике на инпут */
    input:focus {
        background: #ffffff;
        border-color: #22C1C3;
        box-shadow: 0 0 0 4px rgba(34, 193, 195, 0.25);
    }

    /* Стильная кнопка */
    button, input[type="submit"] {
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
        /* Изменено: Убрали transform из общего transition */
        transition: background 0.3s ease, color 0.3s ease, box-shadow 0.3s ease;
    }

    /* Анимация кнопки при наведении */
    button:hover, input[type="submit"]:hover {
        background: #22C1C3;
        color: #ffffff;
        /* !important гарантирует, что ховер применится корректно поверх завершенной анимации */
        transform: translateY(-2px) !important;
        box-shadow: 0 6px 20px rgba(34, 193, 195, 0.4);
    }

    /* Анимация при нажатии на кнопку */
    button:active, input[type="submit"]:active {
        transform: translateY(0) !important;
    }

    /* Красивый цвет для плейсхолдеров (текста-подсказки) */
    input::placeholder {
        color: #999;
    }
</style>




<template>
  <div class="containner_login">
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
      <button type="submit">Войти</button>
    </form>
  </div>
</template>

<script setup>
    import { reactive } from 'vue'

    definePageMeta({
        layout: false 
    })

    const { setAuthTest } = useAuth()

    const loginData = reactive({
        username: '',
        password: ''
    })

    const handleLogin = () => {
    
        console.log('Данные для входа:', loginData)

        return navigateTo('/')
        // Пример отправки данных на сервер:
        // const response = await $fetch('/api/login', { method: 'POST', body: loginData })
    }
</script>
