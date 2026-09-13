<template>
  <Transition name="slide-fade" appear>
    <div class="recent_info_block">
      <h3>Панель управления</h3>
      
      <div class="dashboard-grid">
        <!-- Блок категорий -->
        <section class="dashboard-section">
          <h4>Категории</h4>
          
          <p v-if="categoriesPending" class="status-text">Загрузка категорий...</p>
          
          <p v-else-if="categoriesError" class="status-text error">
            Ошибка: {{ categoriesError.message }}
          </p>
          
          <ul v-else-if="categories && categories.length" class="glass-list">
            <li v-for="category in categories" :key="category.id" class="glass-item">
              <span class="icon">📁</span> {{ category.name }}
            </li>
          </ul>
          
          <p v-else class="status-text">Категории не найдены.</p>
        </section>

        <!-- Блок недавних медиа -->
        <section class="dashboard-section">
          <h4>Недавние медиа</h4>
          
          <p v-if="mediaPending" class="status-text">Загрузка медиа...</p>
          
          <p v-else-if="mediaError" class="status-text error">
            Ошибка: {{ mediaError.message }}
          </p>
          
          <div v-else-if="recentMedia && recentMedia.length" class="media-cards">
            <div v-for="media in recentMedia" :key="media.id" class="media-card">
              <div class="media-header">
                <span class="media-title">{{ media.title }}</span>
                <span class="media-badge" :class="media.type">{{ media.type }}</span>
              </div>
              <p v-if="media.description" class="media-desc">{{ media.description }}</p>
            </div>
          </div>
          
          <p v-else class="status-text">Медиа-ресурсы отсутствуют.</p>
        </section>
      </div>
    </div>
  </Transition>
</template>

<script setup lang="ts">
definePageMeta({
  middleware: 'auth',
  layout: 'default'
})

const { user } = useAuth()

const { 
  data: categories, 
  pending: categoriesPending, 
  error: categoriesError 
} = useFetch<any[]>('http://127.0.0.1:8000/api/categories/')

const { 
  data: recentMedia, 
  pending: mediaPending, 
  error: mediaError 
} = useFetch<any[]>('http://127.0.0.1:8000/api/media/recent', {
  query: { limit: 3 } // передаем стандартный лимит из вашей доки
})
</script>

<style scoped>
/* 1. Стилизация основного блока под Glassmorphism */
.recent_info_block {
  /* Занимает всю доступную ширину и высоту с учетом отступов родителя */
  width: 100%;
  height: calc(100vh - 40px); /* Вычитаем отступы сверху и снизу (по 20px) */
  
  /* Эффект матового стекла */
  background: rgba(255, 255, 255, 0.15);
  backdrop-filter: blur(12px);
  -webkit-backdrop-filter: blur(12px);
  
  /* Тонкая белая граница и скругление в стиле сайдбара */
  border: 1px solid rgba(255, 255, 255, 0.25);
  border-radius: 16px;
  
  /* Внутренние отступы для контента */
  padding: 24px;
  box-sizing: border-box;
  
  /* Цвет текста для лучшей читаемости на светлом фоне */
  color: #ffffff;
  text-shadow: 0 1px 2px rgba(0, 0, 0, 0.1);
}

/* Стили заголовка и контента */
.recent_info_block h3 {
  margin-top: 0;
  margin-bottom: 16px;
  font-size: 1.5rem;
  font-weight: 600;
  opacity: 0.9;
}

.info-content p {
  font-size: 1.2rem;
  margin-bottom: 8px;
  font-weight: 500;
}

.info-content span {
  font-size: 0.95rem;
  opacity: 0.8;
}

/* 2. Анимация плавного появления (slide-fade) */
.slide-fade-enter-active {
  transition: all 0.6s cubic-bezier(0.16, 1, 0.3, 1);
}

.slide-fade-leave-active {
  transition: all 0.4s cubic-bezier(0.7, 0, 0.84, 0);
}

/* Блок плавно проявляется и слегка приподнимается/сдвигается */
.slide-fade-enter-from {
  transform: translateY(20px) scale(0.98);
  opacity: 0;
}

.slide-fade-leave-to {
  transform: translateY(-20px);
  opacity: 0;
}
</style>
