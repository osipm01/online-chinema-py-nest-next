<script setup lang="ts">
import { ref } from 'vue'

// Создаем реактивную переменную. 
// По умолчанию будет использоваться лейаут 'default' (или укажите свой)
const layout = ref<'default' | 'custom'>('default')
</script>

<template>
  <NuxtNotify />
  <NuxtLayout>
    <NuxtPage />
  </NuxtLayout>
</template>
