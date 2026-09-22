<template>
  <GalssPanel>
    <BaseBackLink to="/media/tv-shows" label="← К списку сериалов" />

    <div class="show-header">
      <h1 class="page-title">
        {{ show?.title || `Сериал №${showId}` }}
      </h1>
    </div>

    <nav class="show-tabs">
      <NuxtLink
        :to="`/media/tv-shows/${showId}`"
        class="tab-link"
        active-class="tab-link--active"
      >
        Данные
      </NuxtLink>
      <NuxtLink
        :to="`/media/tv-shows/${showId}/seasons`"
        class="tab-link"
        active-class="tab-link--active"
      >
        Сезоны
      </NuxtLink>
    </nav>

    <!-- Сюда рендерятся дочерние роуты -->
    <NuxtPage />
  </GalssPanel>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import type { Media } from '~/types/MediaTypes'

definePageMeta({
  middleware: 'auth',
  layout: 'default'
})

const route = useRoute()
const mediaService = useMedia()

const showId = Number(route.params.id)
const show = ref<Media | null>(null)

onMounted(async () => {
  try {
    show.value = await mediaService.getById(showId)
  } catch (e) {
    console.error('Ошибка загрузки сериала:', e)
  }
})
</script>

<style scoped>
.show-header {
  margin-bottom: 16px;
}

.page-title {
  color: #ffffff;
  font-size: 24px;
  font-weight: 600;
  margin: 0;
}

.show-tabs {
  display: flex;
  gap: 4px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.15);
  margin-bottom: 20px;
}

.tab-link {
  padding: 10px 16px;
  color: rgba(255, 255, 255, 0.6);
  text-decoration: none;
  font-size: 14px;
  border-bottom: 2px solid transparent;
  transition: color 0.2s, border-color 0.2s;
}

.tab-link:hover {
  color: rgba(255, 255, 255, 0.9);
}

.tab-link--active {
  color: #2ec4b6;
  border-bottom-color: #2ec4b6;
}
</style>