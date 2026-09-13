// plugins/auth-init.client.ts
export default defineNuxtPlugin(() => {
  const { initializeAuth } = useAuth()
  console.log("auth")
  initializeAuth()
})
