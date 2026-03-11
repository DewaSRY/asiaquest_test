<template>
  <v-form ref="formRef" @submit.prevent="handleSubmit">
    <v-row>
      <v-col cols="12">
        <h3 class="text-h6 mb-4">
          <v-icon icon="mdi-account" class="mr-2" />
          Personal Information
        </h3>
      </v-col>

      <v-col cols="12" md="6">
        <v-text-field
          v-model="form.first_name"
          label="First Name"
          variant="outlined"
          :rules="[rules.required]"
          :disabled="disabled"
        />
      </v-col>

      <v-col cols="12" md="6">
        <v-text-field
          v-model="form.last_name"
          label="Last Name"
          variant="outlined"
          :rules="[rules.required]"
          :disabled="disabled"
        />
      </v-col>

      <v-col cols="12" md="6">
        <v-text-field
          v-model="form.email"
          label="Email"
          type="email"
          variant="outlined"
          :rules="[rules.required, rules.email]"
          :disabled="disabled"
        />
      </v-col>

      <v-col cols="12" md="6">
        <v-text-field
          v-model="form.phone_number"
          label="Phone Number"
          variant="outlined"
          :disabled="disabled"
        />
      </v-col>

      <v-col cols="12" md="6">
        <v-text-field
          v-model="form.user_id_number"
          label="ID Number"
          variant="outlined"
          :disabled="disabled"
        />
      </v-col>

      <v-col cols="12">
        <v-divider class="my-4" />
        <h3 class="text-h6 mb-4">
          <v-icon icon="mdi-shield-outline" class="mr-2" />
          Policy Information
        </h3>
      </v-col>

      <v-col cols="12" md="6">
        <v-text-field
          v-model="form.policy_number"
          label="Policy Number"
          variant="outlined"
          :rules="[rules.required]"
          :disabled="disabled"
        />
      </v-col>

      <v-col cols="12" md="6">
        <v-text-field
          v-model="form.policy_holder_number"
          label="Policy Holder Number"
          variant="outlined"
          :disabled="disabled"
        />
      </v-col>

      <v-col cols="12" md="6">
        <v-text-field
          v-model="form.coverage_start_date"
          label="Coverage Start Date"
          type="date"
          variant="outlined"
          :disabled="disabled"
        />
      </v-col>

      <v-col cols="12" md="6">
        <v-text-field
          v-model="form.coverage_end_date"
          label="Coverage End Date"
          type="date"
          variant="outlined"
          :disabled="disabled"
        />
      </v-col>

      <v-col cols="12">
        <v-divider class="my-4" />
        <h3 class="text-h6 mb-4">
          <v-icon icon="mdi-file-document" class="mr-2" />
          Claim Details
        </h3>
      </v-col>

      <v-col cols="12" md="6">
        <v-text-field
          v-model="form.claim_date"
          label="Claim Date"
          type="date"
          variant="outlined"
          :disabled="disabled"
        />
      </v-col>

      <v-col cols="12" md="6">
        <v-text-field
          v-model="form.claim_type"
          label="Claim Type"
          variant="outlined"
          :disabled="disabled"
        />
      </v-col>

      <v-col cols="12">
        <v-textarea
          v-model="form.description"
          label="Description"
          variant="outlined"
          rows="4"
          :disabled="disabled"
        />
      </v-col>

      <v-col cols="12" md="6">
        <v-text-field
          v-model.number="form.claim_amount"
          label="Claim Amount"
          type="number"
          variant="outlined"
          prefix="$"
          :rules="[rules.required, rules.positiveNumber]"
          :disabled="disabled"
        />
      </v-col>
    </v-row>

    <v-divider class="my-6" />

    <div v-if="!disabled" class="d-flex justify-end gap-2">
      <v-btn
        variant="outlined"
        @click="$emit('cancel')"
      >
        Cancel
      </v-btn>
      <v-btn
        color="secondary"
        variant="elevated"
        :loading="saving"
        @click="handleSave"
      >
        <v-icon start icon="mdi-content-save" />
        Save Draft
      </v-btn>
      <v-btn
        color="primary"
        variant="elevated"
        :loading="submitting"
        @click="handleSubmit"
      >
        <v-icon start icon="mdi-send" />
        Submit Claim
      </v-btn>
    </div>
  </v-form>
</template>

<script setup lang="ts">
import type { Claim, UpdateClaimInput } from "~/shared/types";

const props = defineProps<{
  claim: Claim;
  disabled?: boolean;
  saving?: boolean;
  submitting?: boolean;
}>();

const emit = defineEmits(["save", "submit", "cancel"]);

const formRef = ref();

const form = reactive<UpdateClaimInput>({
  first_name: props.claim.first_name || "",
  last_name: props.claim.last_name || "",
  email: props.claim.email || "",
  phone_number: props.claim.phone_number || "",
  user_id_number: props.claim.user_id_number || "",
  policy_number: props.claim.policy_number || "",
  policy_holder_number: props.claim.policy_holder_number || "",
  coverage_start_date: props.claim.coverage_start_date || "",
  coverage_end_date: props.claim.coverage_end_date || "",
  claim_date: props.claim.claim_date || "",
  claim_type: props.claim.claim_type || "",
  description: props.claim.description || "",
  claim_amount: props.claim.claim_amount || 0,
});

const rules = {
  required: (v: any) => !!v || "This field is required",
  email: (v: string) => /.+@.+\..+/.test(v) || "Invalid email address",
  positiveNumber: (v: number) => v >= 0 || "Must be a positive number",
};

const handleSave = async () => {
  const { valid } = await formRef.value?.validate();
  emit("save", form);
};

const handleSubmit = async () => {
  const { valid } = await formRef.value?.validate();
  if (!valid) return;
  emit("submit", form);
};

// Watch for claim changes and update form
watch(
  () => props.claim,
  (newClaim) => {
    Object.assign(form, {
      first_name: newClaim.first_name || "",
      last_name: newClaim.last_name || "",
      email: newClaim.email || "",
      phone_number: newClaim.phone_number || "",
      user_id_number: newClaim.user_id_number || "",
      policy_number: newClaim.policy_number || "",
      policy_holder_number: newClaim.policy_holder_number || "",
      coverage_start_date: newClaim.coverage_start_date || "",
      coverage_end_date: newClaim.coverage_end_date || "",
      claim_date: newClaim.claim_date || "",
      claim_type: newClaim.claim_type || "",
      description: newClaim.description || "",
      claim_amount: newClaim.claim_amount || 0,
    });
  },
  { immediate: true }
);
</script>
