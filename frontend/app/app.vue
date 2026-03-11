<template>
  <v-app>
    <NuxtPage />
  </v-app>
</template>

<script setup lang="ts">
// Initialize auth on app mount
const { initAuth } = useAuth();

onMounted(async () => {
  await initAuth();
});
</script>

<style>
html,
body {
  margin: 0;
  padding: 0;
  font-family: "Roboto", sans-serif;
}
</style>
