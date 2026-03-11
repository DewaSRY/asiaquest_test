export default defineNuxtRouteMiddleware(async (to) => {
  // Skip middleware on server
  if (import.meta.server) return;

  const authStore = useAuthStore();

  // Load tokens from storage
  authStore.loadFromStorage();

  // If not authenticated, redirect to login
  if (!authStore.isAuthenticated) {
    return navigateTo("/");
  }

  // If authenticated but no user data, try to fetch it
  if (!authStore.user) {
    const { fetchCurrentUser } = useAuth();
    const user = await fetchCurrentUser();

    if (!user) {
      authStore.logout();
      return navigateTo("/");
    }
  }
});
