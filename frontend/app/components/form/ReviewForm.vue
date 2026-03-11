<template>
  <v-card class="elevation-2">
    <v-card-title class="d-flex align-center pa-4 bg-primary">
      <v-icon icon="mdi-clipboard-text-search" class="mr-2" />
      Submit Review
    </v-card-title>

    <v-card-text class="pa-4">
      <v-form ref="formRef" @submit.prevent="handleSubmit">
        <v-textarea
          v-model="reviewSummary"
          label="Review Summary"
          variant="outlined"
          rows="6"
          :rules="[rules.required, rules.minLength]"
          placeholder="Write a detailed review summary of this claim. Verify the documents, amounts, and provide your assessment..."
          :disabled="disabled"
        />
      </v-form>
    </v-card-text>

    <v-divider />

    <v-card-actions class="pa-4">
      <v-spacer />
      <v-btn
        color="primary"
        variant="elevated"
        :loading="loading"
        :disabled="disabled"
        @click="handleSubmit"
      >
        <v-icon start icon="mdi-check" />
        Submit Review
      </v-btn>
    </v-card-actions>
  </v-card>
</template>

<script setup lang="ts">
const props = defineProps<{
  loading?: boolean;
  disabled?: boolean;
}>();

const emit = defineEmits(["submit"]);

const formRef = ref();
const reviewSummary = ref("");

const rules = {
  required: (v: string) => !!v || "Review summary is required",
  minLength: (v: string) =>
    v.length >= 10 || "Review summary must be at least 10 characters",
};

const handleSubmit = async () => {
  const { valid } = await formRef.value?.validate();
  if (!valid) return;

  emit("submit", { summary: reviewSummary.value });
  reviewSummary.value = "";
};
</script>
