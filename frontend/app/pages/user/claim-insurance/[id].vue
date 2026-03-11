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
      <v-container fluid class="pa-6">
        <!-- Header with Back Button -->
        <div class="d-flex align-center mb-6">
          <v-btn
            icon="mdi-arrow-left"
            variant="text"
            @click="router.push('/user')"
          />
          <div class="ml-2">
            <h1 class="text-h4 font-weight-bold">
              {{ claim?.claim_number || "Loading..." }}
            </h1>
            <p class="text-body-2 text-grey">
              {{ isDraft ? "Edit your claim details" : "View claim details" }}
            </p>
          </div>
          <v-spacer />
          <StatusChip v-if="claim" :status="claim.status" variant="elevated" />
        </div>

        <v-row v-if="loading" justify="center" class="py-12">
          <v-progress-circular indeterminate size="64" color="primary" />
        </v-row>

        <template v-else-if="claim">
          <!-- Draft: Show editable form -->
          <v-card v-if="isDraft" class="elevation-2">
            <v-card-title class="pa-4 bg-primary">
              <v-icon icon="mdi-pencil" class="mr-2" />
              Edit Claim
            </v-card-title>
            <v-card-text class="pa-6">
              <ClaimForm
                :claim="claim"
                :disabled="false"
                :saving="saving"
                :submitting="submitting"
                @save="handleSave"
                @submit="handleSubmit"
                @cancel="router.push('/user')"
              />
            </v-card-text>
          </v-card>

          <!-- Submitted: Show read-only view -->
          <ClaimDetailView v-else :claim="claim" />
        </template>

        <v-alert v-else type="error" variant="tonal">
          Claim not found
        </v-alert>
      </v-container>
    </v-main>

    <!-- Snackbar -->
    <v-snackbar v-model="snackbar.show" :color="snackbar.color" :timeout="3000">
      {{ snackbar.message }}
    </v-snackbar>

    <!-- Confirmation Dialog -->
    <v-dialog v-model="confirmDialog" max-width="400">
      <v-card>
        <v-card-title>Confirm Submission</v-card-title>
        <v-card-text>
          Are you sure you want to submit this claim? Once submitted, you won't
          be able to make changes.
        </v-card-text>
        <v-card-actions>
          <v-spacer />
          <v-btn variant="text" @click="confirmDialog = false">Cancel</v-btn>
          <v-btn
            color="primary"
            variant="elevated"
            :loading="submitting"
            @click="confirmSubmit"
          >
            Submit
          </v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>
  </div>
</template>

<script setup lang="ts">
import type { Claim, UpdateClaimInput } from "~/shared/types";
import AppBar from "~/components/ui/AppBar.vue";
import SideNav from "~/components/ui/SideNav.vue";
import StatusChip from "~/components/ui/StatusChip.vue";
import ClaimForm from "~/components/form/ClaimForm.vue";
import ClaimDetailView from "~/components/pages/ClaimDetailView.vue";
import { useAuth } from "~/composables/useAuth";
import { useClaims } from "~/composables/useClaims";
import { useRouter, useRoute } from "vue-router";

definePageMeta({
  middleware: ["auth"],
});

const route = useRoute();
const router = useRouter();
const { currentUser, userRole } = useAuth();
const { getClaim, updateClaim, submitClaim } = useClaims();

const drawer = ref(true);
const rail = ref(false);
const loading = ref(false);
const saving = ref(false);
const submitting = ref(false);
const confirmDialog = ref(false);
const claim = ref<Claim | null>(null);
const pendingFormData = ref<UpdateClaimInput | null>(null);

const snackbar = reactive({
  show: false,
  message: "",
  color: "success",
});

const claimId = computed(() => Number(route.params.id));
const isDraft = computed(() => claim.value?.status === "DRAFT");

const showMessage = (message: string, color: string = "success") => {
  snackbar.message = message;
  snackbar.color = color;
  snackbar.show = true;
};

const fetchClaim = async () => {
  loading.value = true;
  try {
    claim.value = await getClaim(claimId.value);
  } catch (error) {
    showMessage("Failed to load claim", "error");
  } finally {
    loading.value = false;
  }
};

const handleSave = async (formData: UpdateClaimInput) => {
  saving.value = true;
  try {
    claim.value = await updateClaim(claimId.value, formData);
    showMessage("Claim saved successfully!");
  } catch (error: any) {
    const message = error.response?.data?.detail || "Failed to save claim";
    showMessage(message, "error");
  } finally {
    saving.value = false;
  }
};

const handleSubmit = async (formData: UpdateClaimInput) => {
  pendingFormData.value = formData;
  confirmDialog.value = true;
};

const confirmSubmit = async () => {
  if (!pendingFormData.value) return;

  submitting.value = true;
  try {
    // First save the form data
    await updateClaim(claimId.value, pendingFormData.value);
    // Then submit
    claim.value = await submitClaim(claimId.value);
    showMessage("Claim submitted successfully!");
    confirmDialog.value = false;
  } catch (error: any) {
    const message = error.response?.data?.detail || "Failed to submit claim";
    showMessage(message, "error");
  } finally {
    submitting.value = false;
  }
};

onMounted(() => {
  fetchClaim();
});
</script>
