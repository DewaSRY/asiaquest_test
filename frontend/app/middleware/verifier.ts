export default defineNuxtRouteMiddleware((to) => {
  const authStore = useAuthStore();

  // Check if user is verifier or approver
  if (
    authStore.user?.role !== "VERIFIER" &&
    authStore.user?.role !== "APPROVER"
  ) {
    // Redirect to appropriate dashboard based on role
    if (authStore.user?.role === "APPROVER") {
      return navigateTo("/approver");
    }
    return navigateTo("/user");
  }
});
