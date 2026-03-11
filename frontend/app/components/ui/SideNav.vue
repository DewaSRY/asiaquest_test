<template>
  <v-navigation-drawer
    :model-value="modelValue"
    @update:model-value="$emit('update:modelValue', $event)"
    :rail="rail"
    permanent
  >
    <v-list density="comfortable" nav>
      <v-list-item
        v-for="item in filteredItems"
        :key="item.to"
        :to="item.to"
        :prepend-icon="item.icon"
        :title="item.title"
        :value="item.to"
        color="primary"
        rounded="xl"
      />
    </v-list>

    <template #append>
      <v-divider />
      <v-list density="compact" nav>
        <v-list-item
          prepend-icon="mdi-chevron-left"
          title="Collapse Menu"
          @click="$emit('update:rail', !rail)"
        />
      </v-list>
    </template>
  </v-navigation-drawer>
</template>

<script setup lang="ts">
const props = defineProps<{
  modelValue: boolean;
  rail: boolean;
  userRole?: string | null;
}>();

defineEmits(["update:modelValue", "update:rail"]);

interface NavItem {
  title: string;
  icon: string;
  to: string;
  roles: string[];
}

const navItems: NavItem[] = [
  {
    title: "Dashboard",
    icon: "mdi-view-dashboard",
    to: "/user",
    roles: ["user"],
  },
  {
    title: "My Claims",
    icon: "mdi-file-document-multiple",
    to: "/user",
    roles: ["user"],
  },
  {
    title: "Dashboard",
    icon: "mdi-view-dashboard",
    to: "/verifier",
    roles: ["verifier"],
  },
  {
    title: "Review Claims",
    icon: "mdi-clipboard-text-search",
    to: "/verifier",
    roles: ["verifier"],
  },
  {
    title: "Dashboard",
    icon: "mdi-view-dashboard",
    to: "/approver",
    roles: ["approver"],
  },
  {
    title: "Approve Claims",
    icon: "mdi-check-decagram",
    to: "/approver",
    roles: ["approver"],
  },
];

const filteredItems = computed(() => {
  if (!props.userRole) return [];
  return navItems.filter((item) => item.roles.includes(props.userRole!));
});
</script>
