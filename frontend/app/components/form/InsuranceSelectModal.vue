<template>
  <v-dialog
    :model-value="modelValue"
    @update:model-value="$emit('update:modelValue', $event)"
    max-width="600"
    persistent
  >
    <v-card>
      <v-card-title class="d-flex align-center pa-4 bg-primary">
        <v-icon icon="mdi-file-plus" class="mr-2" />
        Select Insurance to Claim
      </v-card-title>

      <v-card-text class="pa-4">
        <v-text-field
          v-model="search"
          prepend-inner-icon="mdi-magnify"
          label="Search insurance..."
          variant="outlined"
          density="comfortable"
          hide-details
          clearable
          class="mb-4"
        />

        <v-list v-if="!loading" lines="three" class="insurance-list">
          <v-list-item
            v-for="insurance in filteredInsurances"
            :key="insurance.id"
            :value="insurance.id"
            :class="{ 'v-list-item--active': selected?.id === insurance.id }"
            rounded="lg"
            class="mb-2"
            @click="selected = insurance"
          >
            <template #prepend>
              <v-avatar color="primary" variant="tonal">
                <v-icon icon="mdi-shield-outline" />
              </v-avatar>
            </template>

            <v-list-item-title class="font-weight-bold">
              {{ insurance.title }}
            </v-list-item-title>
            <v-list-item-subtitle>
              {{ insurance.number }}
            </v-list-item-subtitle>
            <v-list-item-subtitle class="text-body-2">
              {{ insurance.description }}
            </v-list-item-subtitle>

            <template #append>
              <div class="text-right">
                <div class="text-h6 text-primary font-weight-bold">
                  {{ formatCurrency(insurance.amount) }}
                </div>
                <v-chip
                  size="x-small"
                  :color="getPriorityColor(insurance.priority)"
                >
                  Priority {{ insurance.priority }}
                </v-chip>
              </div>
            </template>
          </v-list-item>

          <v-list-item v-if="filteredInsurances.length === 0">
            <v-list-item-title class="text-center text-grey">
              No insurances found
            </v-list-item-title>
          </v-list-item>
        </v-list>

        <div v-else class="d-flex justify-center py-8">
          <v-progress-circular indeterminate color="primary" />
        </div>
      </v-card-text>

      <v-divider />

      <v-card-actions class="pa-4">
        <v-btn
          variant="text"
          @click="handleClose"
        >
          Cancel
        </v-btn>
        <v-spacer />
        <v-btn
          color="primary"
          variant="elevated"
          :disabled="!selected"
          :loading="submitting"
          @click="handleSubmit"
        >
          Create Claim
        </v-btn>
      </v-card-actions>
    </v-card>
  </v-dialog>
</template>

<script setup lang="ts">
import type { Insurance } from "~/shared/types";

const props = defineProps<{
  modelValue: boolean;
  insurances: Insurance[];
  loading?: boolean;
}>();

const emit = defineEmits(["update:modelValue", "submit"]);

const search = ref("");
const selected = ref<Insurance | null>(null);
const submitting = ref(false);

const filteredInsurances = computed(() => {
  if (!search.value) return props.insurances;
  const query = search.value.toLowerCase();
  return props.insurances.filter(
    (ins) =>
      ins.title.toLowerCase().includes(query) ||
      ins.number.toLowerCase().includes(query) ||
      ins.description.toLowerCase().includes(query)
  );
});

const formatCurrency = (amount: number) => {
  return new Intl.NumberFormat("en-US", {
    style: "currency",
    currency: "USD",
  }).format(amount);
};

const getPriorityColor = (priority: number) => {
  if (priority <= 2) return "error";
  if (priority <= 3) return "warning";
  return "success";
};

const handleClose = () => {
  selected.value = null;
  search.value = "";
  emit("update:modelValue", false);
};

const handleSubmit = async () => {
  if (!selected.value) return;
  submitting.value = true;
  emit("submit", selected.value);
  submitting.value = false;
};

watch(
  () => props.modelValue,
  (val) => {
    if (!val) {
      selected.value = null;
      search.value = "";
    }
  }
);
</script>

<style scoped>
.insurance-list {
  max-height: 400px;
  overflow-y: auto;
}

.v-list-item--active {
  background-color: rgb(var(--v-theme-primary), 0.1);
  border: 2px solid rgb(var(--v-theme-primary));
}
</style>
