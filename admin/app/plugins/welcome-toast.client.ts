export default defineNuxtPlugin(() => {
  // Код сработает один раз при инициализации приложения в браузере
  useToastify("Добро Пожаловать!", {
    type: "info",
    autoClose: 3000,
    theme: "auto"
  })
})