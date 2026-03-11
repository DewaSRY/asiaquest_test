<template>
  <v-app-bar color="primary" density="comfortable" elevation="2">
    <v-app-bar-nav-icon
      v-if="showMenu"
      @click="$emit('toggle-drawer')"
    />

    <v-app-bar-title>
      <v-icon icon="mdi-shield-check" class="mr-2" />
      Insurance Claims System
    </v-app-bar-title>

    <v-spacer />

    <template v-if="user">
      <v-chip
        class="mr-4"
        :color="roleColor"
        variant="elevated"
      >
        <v-icon start :icon="roleIcon" />
        {{ user.role.toUpperCase() }}
      </v-chip>

      <v-menu>
        <template #activator="{ props }">
          <v-btn
            v-bind="props"
            icon
            variant="text"
          >
            <v-avatar color="surface-variant" size="36">
              <span class="text-body-2">{{ userInitials }}</span>
            </v-avatar>
          </v-btn>
        </template>

        <v-list density="compact">
          <v-list-item>
            <v-list-item-title class="font-weight-bold">
              {{ user.username }}
            </v-list-item-title>
            <v-list-item-subtitle>{{ user.email }}</v-list-item-subtitle>
          </v-list-item>

          <v-divider class="my-2" />

          <v-list-item
            prepend-icon="mdi-logout"
            title="Logout"
            @click="handleLogout"
          />
        </v-list>
      </v-menu>
    </template>
  </v-app-bar>
</template>

<script setup lang="ts">
import type { User } from "~/shared/types";

const props = defineProps<{
  user?: User | null;
  showMenu?: boolean;
}>();

defineEmits(["toggle-drawer"]);

const { logout } = useAuth();

const userInitials = computed(() => {
  if (!props.user) return "?";
  return props.user.username.slice(0, 2).toUpperCase();
});

const roleColor = computed(() => {
  if (!props.user) return "grey";
  switch (props.user.role) {
    case "APPROVER":
      return "success";
    case "VERIFIER":
      return "info";
    default:
      return "secondary";
  }
});

const roleIcon = computed(() => {
  if (!props.user) return "mdi-account";
  switch (props.user.role) {
    case "APPROVER":
      return "mdi-check-decagram";
    case "VERIFIER":
      return "mdi-clipboard-check";
    default:
      return "mdi-account";
  }
});

const handleLogout = () => {
  logout();
};
</script>
