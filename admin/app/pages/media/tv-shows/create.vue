<template>
  <GalssPanel>
    <BaseBackLink to="/media/tv-shows" label="← Назад к списку" />

    <BaseForm class="user-form-container">
      <div class="form-content">
        <div class="form-header">
          <h1 class="page-title">Создание нового сериала</h1>
        </div>

        <form @submit.prevent="handleSubmit" class="form-section">
          <BaseInput
            v-model="createForm.title"
            label="Название сериала"
            placeholder="Введите название сериала"
            :disabled="isProcessing"
            required
          />

          <BaseTextarea
            v-model="createForm.description"
            label="Описание"
            placeholder="Введите описание"
            :disabled="isProcessing"
            :rows="4"
            required
          />

          <BaseFormField label="Категории">
            <div class="checkbox-grid">
              <BaseCheckbox
                v-for="category in categories"
                :key="category.id"
                v-model="createForm.category_ids"
                :value="category.id"
                :label="category.name"
                :disabled="isProcessing"
              />
            </div>
          </BaseFormField>

          <div class="seasons-block">
            <div class="seasons-header">
              <h2 class="section-title">Сезоны</h2>
              <BaseButton
                variant="secondary"
                size="sm"
                :disabled="isProcessing"
                @click="addSeason"
              >
                + Добавить сезон
              </BaseButton>
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
                <BaseButton
                  variant="danger"
                  size="sm"
                  :disabled="isProcessing"
                  @click="removeSeason(seasonIndex)"
                >
                  Удалить сезон
                </BaseButton>
              </div>

              <div class="season-fields-grid">
                <BaseInput
                  v-model="season.season_number"
                  type="number"
                  label="Номер сезона"
                  :min="1"
                  :disabled="isProcessing"
                />
                <BaseInput
                  v-model="season.title"
                  label="Название"
                  placeholder="Название сезона"
                  :disabled="isProcessing"
                />
                <BaseInput
                  v-model="season.poster_url"
                  label="Poster URL"
                  placeholder="https://..."
                  :disabled="isProcessing"
                />
                <div class="input-field-group--full">
                  <BaseTextarea
                    v-model="season.description"
                    label="Описание"
                    placeholder="Описание сезона"
                    :disabled="isProcessing"
                    :rows="3"
                  />
                </div>
              </div>

              <div class="episodes-block">
                <div class="episodes-header">
                  <span class="episodes-title">Эпизоды</span>
                  <BaseButton
                    variant="secondary"
                    size="sm"
                    :disabled="isProcessing"
                    @click="addEpisode(seasonIndex)"
                  >
                    + Добавить эпизод
                  </BaseButton>
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
                    <BaseButton
                      variant="danger"
                      size="sm"
                      :disabled="isProcessing"
                      @click="removeEpisode(seasonIndex, episodeIndex)"
                    >
                      Удалить
                    </BaseButton>
                  </div>

                  <div class="season-fields-grid">
                    <BaseInput
                      v-model="episode.title"
                      label="Название"
                      placeholder="Название эпизода"
                      :disabled="isProcessing"
                    />
                    <BaseInput
                      v-model="episode.duration"
                      type="number"
                      label="Длительность (мин)"
                      :min="0"
                      :disabled="isProcessing"
                    />
                    <BaseInput
                      v-model="episode.hls_link"
                      label="HLS ссылка"
                      placeholder="https://..."
                      :disabled="isProcessing"
                    />
                    <BaseInput
                      v-model="episode.poster_url"
                      label="Poster URL"
                      placeholder="https://..."
                      :disabled="isProcessing"
                    />
                  </div>
                </div>
              </div>
            </div>
          </div>

          <div class="action-bar">
            <BaseButton
              native-type="submit"
              variant="success"
              :loading="isProcessing"
              loading-text="Создание..."
            >
              Создать сериал
            </BaseButton>
            <BaseLink to="/media/tv-shows" variant="secondary">
              Отмена
            </BaseLink>
          </div>
        </form>

        <div v-if="validationError" class="error-state">
          {{ validationError }}
        </div>
        <div v-else-if="error" class="error-state">
          {{ error }}
        </div>
      </div>
    </BaseForm>
  </GalssPanel>
</template>

<script setup lang="ts">
import { reactive, ref } from 'vue'
import type { Category } from '~/types/CategoryTypes'
import type { CreateEpisodeDto } from '~/types/MediaTypes'

definePageMeta({
  middleware: 'auth',
  layout: 'default'
})

const router = useRouter()
const mediaService = useMedia()
const categoryService = useCategory()

const categories = ref<Category[]>([])
const validationError = ref<string | null>(null)

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

const addSeason = () => seasons.value.push(createEmptySeason())

const removeSeason = (index: number) => seasons.value.splice(index, 1)

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

const { isProcessing, error, execute } = useAsyncAction(
  async () => {
    const createdMedia = await mediaService.create({
      title: createForm.title,
      description: createForm.description,
      type: 'tv_show',
      category_ids: createForm.category_ids
    })

    for (const season of seasons.value) {
      await mediaService.addSeasonWithEpisodes(
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
    }

    return createdMedia
  },
  {
    toast: {
      successMessage: () => `Сериал «${createForm.title}» создан`,
      errorMessage: (e) => e?.data?.detail || `Ошибка ${e?.status || ''}`,
    },
    onSuccess: () => router.push('/media/tv-shows'),
  }
)

const handleSubmit = () => {
  validationError.value = null
  if (!createForm.title || !createForm.description) {
    validationError.value = 'Заполните название и описание сериала'
    return
  }
  execute().catch(() => {})
}

onMounted(fetchCategories)
</script>

<style scoped>
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

.input-field-group--full {
  grid-column: 1 / -1;
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

.action-bar {
  margin-top: 8px;
  display: flex;
  gap: 12px;
  align-items: center;
}
</style>