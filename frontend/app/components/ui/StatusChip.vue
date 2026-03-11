<template>
  <v-chip
    :color="statusColor"
    :variant="variant"
    size="small"
  >
    <v-icon start :icon="statusIcon" size="x-small" />
    {{ statusLabel }}
  </v-chip>
</template>

<script setup lang="ts">
import type { ClaimStatus } from "~/shared/types";

const props = defineProps<{
  status: ClaimStatus;
  variant?: "flat" | "elevated" | "tonal" | "outlined" | "text" | "plain";
}>();

const statusColor = computed(() => {
  switch (props.status) {
    case "DRAFT":
      return "grey";
    case "SUBMITTED":
      return "info";
    case "REVIEWED":
      return "warning";
    case "APPROVED":
      return "success";
    case "REJECTED":
      return "error";
    default:
      return "grey";
  }
});

const statusIcon = computed(() => {
  switch (props.status) {
    case "DRAFT":
      return "mdi-pencil";
    case "SUBMITTED":
      return "mdi-send";
    case "REVIEWED":
      return "mdi-eye-check";
    case "APPROVED":
      return "mdi-check-circle";
    case "REJECTED":
      return "mdi-close-circle";
    default:
      return "mdi-help-circle";
  }
});

const statusLabel = computed(() => {
  return props.status.charAt(0).toUpperCase() + props.status.slice(1).toLowerCase();
});
</script>
