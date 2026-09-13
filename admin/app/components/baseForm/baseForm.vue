<template>
  <!-- Обернули в Transition для контроля анимации во Vue -->
  <Transition name="water-float" appear>
    <div class="form-shell" v-if="show">
      <!-- Шапка формы -->
      <header class="form-header">
        <h2 class="form-title">
          <slot name="title">Название формы</slot>
        </h2>
        <p v-if="$slots.subtitle" class="form-subtitle">
          <slot name="subtitle"></slot>
        </p>
      </header>

      <!-- Основной контент -->
      <div class="form-content">
        <slot></slot>
      </div>

      <!-- Подвал с кнопками -->
      <footer class="form-footer">
        <button 
          type="submit" 
          class="btn btn-primary" 
          @click="$emit('submit')"
        >
          <slot name="submit-text">Сохранить</slot>
        </button>
      </footer>
    </div>
  </Transition>
</template>

<script setup>
defineProps({
  show: {
    type: Boolean,
    default: true
  }
})

defineEmits(['submit', 'cancel'])
</script>

<style scoped>

.water-float-enter-from {
  opacity: 0;
  transform: translateY(60px) scale(0.92); /* Опущена вниз и слегка уменьшена */
  filter: blur(15px); /* Полностью размыта, как в воде */
}

/* Процесс анимации */
.water-float-enter-active {
  /* Использование кубической безье (cubic-bezier) дает плавный толчок в конце, 
     будто оболочка слегка «выпрыгивает» на поверхность и покачивается */
  transition: 
    opacity 0.8s ease-out, 
    transform 0.9s cubic-bezier(0.16, 1, 0.3, 1), 
    filter 0.7s ease-out;
}

/* Конечное состояние (на поверхности) */
.water-float-enter-to {
  opacity: 1;
  transform: translateY(0) scale(1);
  filter: blur(0px); /* Четкий фокус */
}

/* Анимация исчезновения (если форма закрывается) */
.water-float-leave-active {
  transition: all 0.5s ease-in;
}
.water-float-leave-to {
  opacity: 0;
  transform: translateY(20px) scale(0.96);
  filter: blur(8px);
}

/* --- СТИЛИ ОБОЛОЧКИ (GLASSMORPHISM) --- */
.form-shell {
  width: 100%;
  max-width: 650px;
  background: rgba(255, 255, 255, 0.07);
  backdrop-filter: blur(20px);
  -webkit-backdrop-filter: blur(20px);
  border: 1px solid rgba(255, 255, 255, 0.15);
  border-radius: 16px;
  padding: 32px;
  box-shadow: 0 12px 40px 0 rgba(0, 0, 0, 0.12); /* Увеличили тень для объема */
  color: #ffffff;
  box-sizing: border-box;
  will-change: transform, opacity, filter; /* Подсказка браузеру для плавной работы */
}

.form-header {
  margin-bottom: 28px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
  padding-bottom: 16px;
}

.form-title {
  margin: 0;
  font-size: 1.5rem;
  font-weight: 600;
  letter-spacing: -0.5px;
}

.form-subtitle {
  margin: 6px 0 0 0;
  font-size: 0.85rem;
  color: rgba(255, 255, 255, 0.6);
}

.form-content {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

/* Наследование стилей для внутренних элементов формы */
:deep(.form-group) {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

:deep(.form-label) {
  font-size: 0.9rem;
  font-weight: 500;
  color: rgba(255, 255, 255, 0.85);
}

:deep(.form-input) {
  background: rgba(255, 255, 255, 0.08);
  border: 1px solid rgba(255, 255, 255, 0.2);
  border-radius: 8px;
  padding: 12px 16px;
  color: #ffffff;
  font-size: 0.95rem;
  outline: none;
  transition: all 0.2s ease;
  font-family: inherit;
}

:deep(.form-input::placeholder) {
  color: rgba(255, 255, 255, 0.35);
}

:deep(.form-input:focus) {
  background: rgba(255, 255, 255, 0.15);
  border-color: rgba(255, 255, 255, 0.5);
  box-shadow: 0 0 0 3px rgba(255, 255, 255, 0.1);
}

.form-footer {
  margin-top: 32px;
  padding-top: 20px;
  border-top: 1px solid rgba(255, 255, 255, 0.1);
  display: flex;
  justify-content: flex-end;
  gap: 12px;
}

.btn {
  padding: 10px 20px;
  border-radius: 8px;
  font-size: 0.9rem;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s ease;
  border: none;
}

.btn-secondary {
  background: transparent;
  color: rgba(255, 255, 255, 0.8);
  border: 1px solid rgba(255, 255, 255, 0.2);
}

.btn-secondary:hover {
  background: rgba(255, 255, 255, 0.08);
  color: #ffffff;
}

.btn-primary {
  background: #ffffff;
  color: #1a1a1a;
  font-weight: 600;
}

.btn-primary:hover {
  background: rgba(255, 255, 255, 0.9);
  transform: translateY(-1px);
}

.btn-primary:active {
  transform: translateY(0);
}
</style>
