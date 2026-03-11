export default defineNuxtRouteMiddleware((to) => {
  const authStore = useAuthStore();

  // Check if user is approver
  if (authStore.user?.role !== "APPROVER") {
    // Redirect to appropriate dashboard based on role
    if (authStore.user?.role === "VERIFIER") {
      return navigateTo("/verifier");
    }
    return navigateTo("/user");
  }
});
