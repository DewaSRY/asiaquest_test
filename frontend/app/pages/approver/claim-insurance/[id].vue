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
            @click="router.push('/approver')"
          />
          <div class="ml-2">
            <h1 class="text-h4 font-weight-bold">
              {{ claim?.claim_number || "Loading..." }}
            </h1>
            <p class="text-body-2 text-grey">Make approval decision</p>
          </div>
          <v-spacer />
          <StatusChip v-if="claim" :status="claim.status" variant="elevated" />
        </div>

        <v-row v-if="loading" justify="center" class="py-12">
          <v-progress-circular indeterminate size="64" color="primary" />
        </v-row>

        <template v-else-if="claim">
          <v-row>
            <!-- Claim Details -->
            <v-col cols="12" lg="8">
              <ClaimDetailView :claim="claim" />
            </v-col>

            <!-- Approval Form -->
            <v-col cols="12" lg="4">
              <ApprovalForm
                v-if="canApprove"
                :loading="submitting"
                @submit="handleApproval"
              />

              <v-alert
                v-else-if="claim.status === 'APPROVED'"
                type="success"
                variant="tonal"
                class="mb-4"
              >
                <v-alert-title>Approved</v-alert-title>
                This claim has been approved.
              </v-alert>

              <v-alert
                v-else-if="claim.status === 'REJECTED'"
                type="error"
                variant="tonal"
                class="mb-4"
              >
                <v-alert-title>Rejected</v-alert-title>
                This claim has been rejected.
              </v-alert>

              <v-alert
                v-else
                type="info"
                variant="tonal"
                class="mb-4"
              >
                <v-alert-title>Status: {{ claim.status }}</v-alert-title>
                This claim cannot be approved/rejected in its current state.
              </v-alert>
            </v-col>
          </v-row>
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
  </div>
</template>

<script setup lang="ts">
import type { Claim, ApproveClaimInput } from "~/shared/types";

definePageMeta({
  middleware: ["auth", "approver"],
});

const route = useRoute();
const router = useRouter();
const { currentUser, userRole } = useAuth();
const { getClaim, approveClaim } = useClaims();

const drawer = ref(true);
const rail = ref(false);
const loading = ref(false);
const submitting = ref(false);
const claim = ref<Claim | null>(null);

const snackbar = reactive({
  show: false,
  message: "",
  color: "success",
});

const claimId = computed(() => Number(route.params.id));
const canApprove = computed(() => claim.value?.status === "REVIEWED");

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

const handleApproval = async (data: ApproveClaimInput) => {
  submitting.value = true;
  try {
    claim.value = await approveClaim(claimId.value, data);
    const action = data.decision === "APPROVED" ? "approved" : "rejected";
    showMessage(`Claim ${action} successfully!`);
  } catch (error: any) {
    const message = error.response?.data?.detail || "Failed to process decision";
    showMessage(message, "error");
  } finally {
    submitting.value = false;
  }
};

onMounted(() => {
  fetchClaim();
});
</script>
