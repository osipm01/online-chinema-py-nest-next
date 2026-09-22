<template>
  <div class="season-wrapper">
    <div class="season-header">
      <h2 class="season-title">
        Сезон {{ season?.season_number ?? '…' }} — {{ season?.title || 'Без названия' }}
      </h2>
    </div>

    <NuxtPage />
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import type { Season } from '~/types/MediaTypes'

definePageMeta({
  middleware: 'auth',
  layout: 'default'
})

const route = useRoute()
const mediaService = useMedia()

const seasonId = Number(route.params.seasonId)
const season = ref<Season | null>(null)

onMounted(async () => {
  try {
    season.value = await mediaService.getSeason(seasonId)
  } catch (e) {
    console.error('Ошибка загрузки сезона:', e)
  }
})
</script>

<style scoped>
.season-wrapper {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.season-header {
  margin-bottom: 8px;
}

.season-title {
  color: #ffffff;
  font-size: 18px;
  font-weight: 600;
  margin: 0;
}
</style>