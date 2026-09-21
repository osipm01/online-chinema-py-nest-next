<style lang="css" scoped>
.tolls_containner {
  width: 100%;
  height: 100%;
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.section-title {
  color: rgba(255, 255, 255, 0.5);
  font-size: 12px;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.5px;
  margin: 12px 0 4px 0;
}

.nav-link {
  display: flex;
  align-items: center;
  padding: 10px 14px;
  background: rgba(255, 255, 255, 0.08);
  border: 1px solid rgba(255, 255, 255, 0.12);
  border-radius: 8px;
  color: rgba(255, 255, 255, 0.9);
  text-decoration: none;
  font-size: 14px;
  transition: background 0.2s ease, transform 0.1s;
}

.nav-link:hover {
  background: rgba(255, 255, 255, 0.15);
}

.nav-link:active {
  transform: scale(0.98);
}

.nav-hint {
  color: rgba(255, 255, 255, 0.4);
  font-size: 12px;
  font-style: italic;
  padding: 4px 2px;
}
</style>

<template>
  <GalssPanel>
    <div class="tolls_containner">
      <NuxtLink to="/media/categories" class="nav-link">
        <span>Категории</span>
      </NuxtLink>

      <NuxtLink to="/media/movies" class="nav-link">
        <span>Фильмы</span>
      </NuxtLink>

      <NuxtLink to="/media/tv-shows" class="nav-link">
        <span>Сериалы</span>
      </NuxtLink>
    </div>
  </GalssPanel>
</template>

<script setup lang="ts">
definePageMeta({
  middleware: 'auth',
  layout: 'default'
})
</script>