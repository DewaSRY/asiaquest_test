<template>
  <v-card class="elevation-2">
    <v-card-title class="d-flex align-center pa-4 bg-primary">
      <v-icon icon="mdi-gavel" class="mr-2" />
      Make Decision
    </v-card-title>

    <v-card-text class="pa-4">
      <v-form ref="formRef" @submit.prevent>
        <v-radio-group v-model="decision" :disabled="disabled">
          <v-radio
            label="Approve Claim"
            value="APPROVED"
            color="success"
          >
            <template #label>
              <div class="d-flex align-center">
                <v-icon icon="mdi-check-circle" color="success" class="mr-2" />
                <span>Approve Claim</span>
              </div>
            </template>
          </v-radio>
          <v-radio
            label="Reject Claim"
            value="REJECTED"
            color="error"
          >
            <template #label>
              <div class="d-flex align-center">
                <v-icon icon="mdi-close-circle" color="error" class="mr-2" />
                <span>Reject Claim</span>
              </div>
            </template>
          </v-radio>
        </v-radio-group>

        <v-expand-transition>
          <v-textarea
            v-if="decision === 'REJECTED'"
            v-model="reason"
            label="Rejection Reason"
            variant="outlined"
            rows="4"
            :rules="decision === 'REJECTED' ? [rules.required] : []"
            placeholder="Please provide a reason for rejection..."
            class="mt-4"
            :disabled="disabled"
          />
        </v-expand-transition>
      </v-form>
    </v-card-text>

    <v-divider />

    <v-card-actions class="pa-4">
      <v-spacer />
      <v-btn
        v-if="decision === 'APPROVED'"
        color="success"
        variant="elevated"
        :loading="loading"
        :disabled="disabled || !decision"
        @click="handleSubmit"
      >
        <v-icon start icon="mdi-check" />
        Approve
      </v-btn>
      <v-btn
        v-else-if="decision === 'REJECTED'"
        color="error"
        variant="elevated"
        :loading="loading"
        :disabled="disabled || !decision"
        @click="handleSubmit"
      >
        <v-icon start icon="mdi-close" />
        Reject
      </v-btn>
      <v-btn
        v-else
        color="grey"
        variant="elevated"
        disabled
      >
        Select Decision
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
const decision = ref<"APPROVED" | "REJECTED" | null>(null);
const reason = ref("");

const rules = {
  required: (v: string) => !!v || "Rejection reason is required",
};

const handleSubmit = async () => {
  const { valid } = await formRef.value?.validate();
  if (!valid) return;

  emit("submit", {
    decision: decision.value,
    reason: decision.value === "REJECTED" ? reason.value : undefined,
  });

  decision.value = null;
  reason.value = "";
};
</script>
