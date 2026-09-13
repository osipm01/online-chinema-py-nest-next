
<style lang="css">

.tolls_containner{
    width: 100%;
    height: 100%;
    display: flex;
    flex-direction: column;
    gap: 10px;
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