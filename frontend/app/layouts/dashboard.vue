<template>
  <div>
    <AppBar :user="currentUser" :show-menu="true" @toggle-drawer="drawer = !drawer" />

    <SideNav
      v-model="drawer"
      :rail="rail"
      :user-role="userRole"
      @update:rail="rail = $event"
    />

    <v-main>
      <slot />
    </v-main>
  </div>
</template>

<script setup lang="ts">
import AppBar from "~/components/ui/AppBar.vue";
import SideNav from "~/components/ui/SideNav.vue";

const { currentUser, userRole } = useAuth();

const drawer = ref(true);
const rail = ref(false);
</script>
