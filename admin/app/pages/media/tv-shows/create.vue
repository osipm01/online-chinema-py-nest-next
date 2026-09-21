<template>
  <GalssPanel>
    <div class="navigation-bar">
      <NuxtLink to="/media/tv-shows" class="btn-back">← Назад к списку</NuxtLink>
    </div>

    <BaseForm class="user-form-container">
      <div class="form-content">
        <div class="form-header">
          <h1 class="page-title">Создание нового сериала</h1>
        </div>

        <form @submit.prevent="handleCreate" class="form-section">
          <!-- Данные сериала -->
          <div class="input-field-group">
            <label for="title" class="field-label">Название сериала</label>
            <input
              id="title"
              v-model="createForm.title"
              type="text"
              required
              class="custom-input"
              placeholder="Введите название сериала"
              :disabled="isProcessing"
            />
          </div>

          <div class="input-field-group">
            <label for="description" class="field-label">Описание</label>
            <textarea
              id="description"
              v-model="createForm.description"
              required
              class="custom-input custom-textarea"
              placeholder="Введите описание"
              :disabled="isProcessing"
            ></textarea>
          </div>

          <div class="input-field-group">
            <label class="field-label">Категории</label>
            <div class="checkbox-grid">
              <label
                v-for="category in categories"
                :key="category.id"
                class="checkbox-label"
              >
                <input
                  type="checkbox"
                  class="custom-checkbox"
                  :value="category.id"
                  v-model="createForm.category_ids"
                  :disabled="isProcessing"
                />
                {{ category.name }}
              </label>
            </div>
          </div>

          <!-- Сезоны -->
          <div class="seasons-block">
            <div class="seasons-header">
              <h2 class="section-title">Сезоны</h2>
              <button
                type="button"
                class="btn-action btn-secondary btn-small"
                :disabled="isProcessing"
                @click="addSeason"
              >
                + Добавить сезон
              </button>
            </div>

            <div v-if="seasons.length === 0" class="empty-state-text">
              Сезоны не добавлены.
            </div>

            <div
              v-for="(season, seasonIndex) in seasons"
              :key="seasonIndex"
              class="season-card"
            >
              <div class="season-card-header">
                <span class="season-card-title">Сезон {{ seasonIndex + 1 }}</span>
                <button
                  type="button"
                  class="btn-action btn-danger btn-small"
                  :disabled="isProcessing"
                  @click="removeSeason(seasonIndex)"
                >
                  Удалить сезон
                </button>
              </div>

              <div class="season-fields-grid">
                <div class="input-field-group">
                  <label class="field-label">Номер сезона</label>
                  <input
                    v-model.number="season.season_number"
                    type="number"
                    min="1"
                    class="custom-input"
                    :disabled="isProcessing"
                  />
                </div>

                <div class="input-field-group">
                  <label class="field-label">Название</label>
                  <input
                    v-model="season.title"
                    type="text"
                    class="custom-input"
                    placeholder="Название сезона"
                    :disabled="isProcessing"
                  />
                </div>

                <div class="input-field-group">
                  <label class="field-label">Poster URL</label>
                  <input
                    v-model="season.poster_url"
                    type="text"
                    class="custom-input"
                    placeholder="https://..."
                    :disabled="isProcessing"
                  />
                </div>

                <div class="input-field-group input-field-group--full">
                  <label class="field-label">Описание</label>
                  <textarea
                    v-model="season.description"
                    class="custom-input custom-textarea"
                    placeholder="Описание сезона"
                    :disabled="isProcessing"
                  ></textarea>
                </div>
              </div>

              <!-- Эпизоды сезона -->
              <div class="episodes-block">
                <div class="episodes-header">
                  <span class="episodes-title">Эпизоды</span>
                  <button
                    type="button"
                    class="btn-action btn-secondary btn-small"
                    :disabled="isProcessing"
                    @click="addEpisode(seasonIndex)"
                  >
                    + Добавить эпизод
                  </button>
                </div>

                <div v-if="season.episodes.length === 0" class="empty-state-text">
                  Эпизоды не добавлены.
                </div>

                <div
                  v-for="(episode, episodeIndex) in season.episodes"
                  :key="episodeIndex"
                  class="episode-card"
                >
                  <div class="episode-card-header">
                    <span class="episode-card-title">Эпизод {{ episodeIndex + 1 }}</span>
                    <button
                      type="button"
                      class="btn-action btn-danger btn-small"
                      :disabled="isProcessing"
                      @click="removeEpisode(seasonIndex, episodeIndex)"
                    >
                      Удалить
                    </button>
                  </div>

                  <div class="season-fields-grid">
                    <div class="input-field-group">
                      <label class="field-label">Название</label>
                      <input
                        v-model="episode.title"
                        type="text"
                        class="custom-input"
                        placeholder="Название эпизода"
                        :disabled="isProcessing"
                      />
                    </div>

                    <div class="input-field-group">
                      <label class="field-label">Длительность (мин)</label>
                      <input
                        v-model.number="episode.duration"
                        type="number"
                        min="0"
                        class="custom-input"
                        :disabled="isProcessing"
                      />
                    </div>

                    <div class="input-field-group">
                      <label class="field-label">HLS ссылка</label>
                      <input
                        v-model="episode.hls_link"
                        type="text"
                        class="custom-input"
                        placeholder="https://..."
                        :disabled="isProcessing"
                      />
                    </div>

                    <div class="input-field-group">
                      <label class="field-label">Poster URL</label>
                      <input
                        v-model="episode.poster_url"
                        type="text"
                        class="custom-input"
                        placeholder="https://..."
                        :disabled="isProcessing"
                      />
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>

          <div class="action-bar">
            <button type="submit" class="btn-action btn-success" :disabled="isProcessing">
              {{ isProcessing ? 'Создание...' : 'Создать сериал' }}
            </button>
            <NuxtLink to="/tv-shows" class="btn-action btn-secondary">
              Отмена
            </NuxtLink>
          </div>
        </form>

        <div v-if="errorMessage" class="error-state">
          {{ errorMessage }}
        </div>
      </div>
    </BaseForm>
  </GalssPanel>
</template>

<script setup lang="ts">
import { ref, reactive } from 'vue'
import type { Category } from '~/types/CategoryTypes'
import type { CreateEpisodeDto } from '~/types/MediaTypes'

definePageMeta({
  middleware: 'auth',
  layout: 'default'
})

const router = useRouter()
const mediaService = useMedia()
const categoryService = useCategory()

const isProcessing = ref(false)
const errorMessage = ref<string | null>(null)
const categories = ref<Category[]>([])

interface EpisodeDraft {
  title: string
  duration: number
  hls_link: string
  poster_url: string
}

interface SeasonDraft {
  season_number: number
  title: string
  description: string
  poster_url: string
  episodes: EpisodeDraft[]
}

const createForm = reactive({
  title: '',
  description: '',
  category_ids: [] as number[]
})

const seasons = ref<SeasonDraft[]>([])

const createEmptyEpisode = (): EpisodeDraft => ({
  title: '',
  duration: 0,
  hls_link: '',
  poster_url: ''
})

const createEmptySeason = (): SeasonDraft => ({
  season_number: seasons.value.length + 1,
  title: '',
  description: '',
  poster_url: '',
  episodes: []
})

const addSeason = () => {
  seasons.value.push(createEmptySeason())
}

const removeSeason = (index: number) => {
  seasons.value.splice(index, 1)
}

const addEpisode = (seasonIndex: number) => {
  seasons.value[seasonIndex].episodes.push(createEmptyEpisode())
}

const removeEpisode = (seasonIndex: number, episodeIndex: number) => {
  seasons.value[seasonIndex].episodes.splice(episodeIndex, 1)
}

const fetchCategories = async () => {
  try {
    categories.value = await categoryService.getAll()
  } catch (e) {
    console.error('Ошибка загрузки категорий:', e)
  }
}

const handleCreate = async () => {
  if (!createForm.title || !createForm.description) {
    errorMessage.value = 'Заполните название и описание сериала'
    return
  }

  try {
    isProcessing.value = true
    errorMessage.value = null

    // 1. Создаём media (tv_show)
    const createdMedia = await mediaService.create({
      title: createForm.title,
      description: createForm.description,
      type: 'tv_show',
      category_ids: createForm.category_ids
    })

    // 2. Последовательно создаём сезоны и их эпизоды
    for (const season of seasons.value) {
      const { season: createdSeason } = await mediaService.addSeasonWithEpisodes(
        createdMedia.id,
        {
          season_number: season.season_number,
          title: season.title,
          description: season.description,
          poster_url: season.poster_url
        },
        season.episodes.map<Omit<CreateEpisodeDto, 'media_id' | 'season_id'>>((ep) => ({
          title: ep.title,
          duration: ep.duration,
          hls_link: ep.hls_link,
          poster_url: ep.poster_url
        }))
      )
      console.log('Создан сезон:', createdSeason.id)
    }

    useToastify(`Сериал «${createForm.title}» создан`, {
      type: 'success',
      autoClose: 3000,
      theme: 'auto'
    })

    router.push('/media/tv-shows')
  } catch (err: any) {
    errorMessage.value = err.message || 'Ошибка при создании'
    useToastify(`Ошибка ${err.status || ''}`, {
      type: 'error',
      autoClose: 3000,
      theme: 'auto'
    })
    console.error('Ошибка при создании сериала:', err)
  } finally {
    isProcessing.value = false
  }
}

onMounted(() => {
  fetchCategories()
})
</script>

<style scoped>
.navigation-bar {
  margin-bottom: 16px;
}

.btn-back {
  color: rgba(255, 255, 255, 0.7);
  text-decoration: none;
  font-size: 14px;
  transition: color 0.2s;
}

.btn-back:hover {
  color: #ffffff;
}

.form-content {
  display: flex;
  flex-direction: column;
  gap: 24px;
}

.form-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.page-title {
  color: #ffffff;
  font-size: 24px;
  font-weight: 600;
  margin: 0;
}

.form-section {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.input-field-group {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.input-field-group--full {
  grid-column: 1 / -1;
}

.field-label {
  color: rgba(255, 255, 255, 0.8);
  font-size: 14px;
}

.custom-input {
  width: 100%;
  padding: 12px 16px;
  background: rgba(255, 255, 255, 1);
  border: 1px solid rgba(255, 255, 255, 0.2);
  border-radius: 8px;
  color: #333333;
  font-size: 14px;
  outline: none;
  box-sizing: border-box;
}

.custom-textarea {
  min-height: 80px;
  resize: vertical;
  font-family: inherit;
}

.custom-input:disabled {
  background: rgba(255, 255, 255, 0.5);
  cursor: not-allowed;
}

.checkbox-grid {
  display: flex;
  flex-wrap: wrap;
  gap: 12px 20px;
}

.checkbox-label {
  display: flex;
  align-items: center;
  gap: 8px;
  color: rgba(255, 255, 255, 0.8);
  font-size: 14px;
  cursor: pointer;
  user-select: none;
}

.custom-checkbox {
  width: 18px;
  height: 18px;
  accent-color: #2ec4b6;
  cursor: pointer;
}

.seasons-block {
  display: flex;
  flex-direction: column;
  gap: 16px;
  padding: 16px;
  border: 1px solid rgba(255, 255, 255, 0.15);
  border-radius: 12px;
  background: rgba(255, 255, 255, 0.04);
}

.seasons-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.section-title {
  color: #ffffff;
  font-size: 18px;
  font-weight: 600;
  margin: 0;
}

.season-card {
  display: flex;
  flex-direction: column;
  gap: 12px;
  padding: 14px;
  border: 1px solid rgba(255, 255, 255, 0.12);
  border-radius: 10px;
  background: rgba(255, 255, 255, 0.05);
}

.season-card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.season-card-title {
  color: #ffffff;
  font-size: 15px;
  font-weight: 600;
}

.season-fields-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 12px;
}

.episodes-block {
  display: flex;
  flex-direction: column;
  gap: 10px;
  padding-top: 8px;
  border-top: 1px dashed rgba(255, 255, 255, 0.15);
}

.episodes-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.episodes-title {
  color: rgba(255, 255, 255, 0.85);
  font-size: 14px;
  font-weight: 600;
}

.episode-card {
  display: flex;
  flex-direction: column;
  gap: 10px;
  padding: 10px;
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 8px;
  background: rgba(255, 255, 255, 0.03);
}

.episode-card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.episode-card-title {
  color: rgba(255, 255, 255, 0.85);
  font-size: 13px;
  font-weight: 600;
}

.empty-state-text {
  color: rgba(255, 255, 255, 0.5);
  font-style: italic;
  font-size: 13px;
  padding: 6px 0;
}

.action-bar {
  margin-top: 8px;
  display: flex;
  gap: 12px;
  align-items: center;
}

.btn-action {
  padding: 12px 24px;
  border-radius: 8px;
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  border: none;
  transition: opacity 0.2s, transform 0.1s, background 0.2s;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  text-decoration: none;
}

.btn-action:active {
  transform: scale(0.98);
}

.btn-action:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.btn-small {
  padding: 6px 12px;
  font-size: 13px;
}

.btn-success {
  background-color: #2ec4b6;
  color: white;
  width: max-content;
}

.btn-secondary {
  background-color: rgba(255, 255, 255, 0.15);
  color: #ffffff;
  border: 1px solid rgba(255, 255, 255, 0.3);
}

.btn-secondary:hover {
  background-color: rgba(255, 255, 255, 0.25);
}

.btn-danger {
  background-color: #e71d36;
  color: white;
}

.btn-danger:hover {
  background-color: #c9182d;
}

.error-state {
  color: #ff6b6b;
  padding: 12px 16px;
  border-radius: 8px;
  background: rgba(255, 107, 107, 0.1);
  border: 1px solid rgba(255, 107, 107, 0.3);
  font-size: 14px;
  text-align: center;
}

.loading-state {
  color: #ffffff;
  padding: 20px 0;
  text-align: center;
}
</style>