import { MediaService } from '~/services/MediaService'

export const useMedia = () => {
  const { $api } = useNuxtApp()
  const { getAccessToken } = useAuth()

  return new MediaService($api, getAccessToken)
}