<template>
  <GalssPanel>

      <NuxtLink 
        :to="`/media/categories/create`"
      >
        создать категорию
      </NuxtLink>


    <div v-if="status === 'pending'" class="">
      Загрузка списка категорий...
    </div>

    <div v-else-if="error" class="">
      Ошибка: {{ error.message }}
    </div>

    <!-- Список категорий в виде ссылок -->
    <div v-else-if="categories && categories.length > 0" class="f">
      <NuxtLink 
        v-for="category in categories" 
        :key="category.id" 
        :to="`/media/categories/${category.id}`"
        class=""
      >
        {{ category.name }}
      </NuxtLink>
    </div>

    <!-- Если на сервере нет ни одной категории -->
    <div v-else class="py-2 text-zinc-500 text-sm">
      Список категорий пуст.
    </div>
  </GalssPanel>
</template>

<script setup lang="ts">
const categoryApi = useCategory();

// Получаем данные с сервера
const { data: categories, status, error } = await useAsyncData('categories-list', () => 
  categoryApi.getAll()
)
</script>
