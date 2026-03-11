<template>
  <v-card :loading="loading" class="elevation-2">
    <v-card-title class="d-flex align-center pa-4">
      <v-icon :icon="icon" class="mr-2" />
      {{ title }}
      <v-spacer />
      <slot name="actions" />
    </v-card-title>

    <v-divider />

    <v-card-text class="pa-0">
      <v-data-table
        :headers="headers"
        :items="items"
        :loading="loading"
        :items-per-page="itemsPerPage"
        class="elevation-0"
        hover
        @click:row="handleRowClick"
      >
        <template #item.status="{ item }">
          <StatusChip :status="item.status" />
        </template>

        <template #item.claim_amount="{ item }">
          {{ item.claim_amount ? formatCurrency(item.claim_amount) : "-" }}
        </template>

        <template #item.created_at="{ item }">
          {{ formatDate(item.created_at) }}
        </template>

        <template #item.actions="{ item }">
          <v-btn
            icon="mdi-eye"
            variant="text"
            size="small"
            color="primary"
            @click.stop="$emit('view', item)"
          />
        </template>

        <template #bottom>
          <v-pagination
            v-if="(totalPages?? 0) > 1"
            :model-value="page"
            :length="totalPages"
            :total-visible="5"
            class="my-4"
            @update:model-value="$emit('update:page', $event)"
          />
        </template>
      </v-data-table>
    </v-card-text>
  </v-card>
</template>

<script setup lang="ts">
import type { Claim } from "~/shared/types";

defineProps<{
  title: string;
  icon: string;
  headers: any[];
  items: Claim[];
  loading?: boolean;
  page?: number;
  totalPages?: number;
  itemsPerPage?: number;
}>();

const emit = defineEmits(["view", "update:page"]);

const handleRowClick = (_: any, { item }: { item: Claim }) => {
  emit("view", item);
};

const formatCurrency = (amount: number) => {
  return new Intl.NumberFormat("en-US", {
    style: "currency",
    currency: "USD",
  }).format(amount);
};

const formatDate = (dateString: string) => {
  return new Date(dateString).toLocaleDateString("en-US", {
    year: "numeric",
    month: "short",
    day: "numeric",
  });
};
</script>
