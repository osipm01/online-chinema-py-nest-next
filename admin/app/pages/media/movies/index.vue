

<template>
    <GalssPanel>
         <NuxtLink to="/categories" class="nav-link">
            <span>О нас</span>
        </NuxtLink>
    </GalssPanel>
</template>

<script setup lang="ts">
definePageMeta({
  middleware: 'auth',
  layout: 'default'
})

</script>