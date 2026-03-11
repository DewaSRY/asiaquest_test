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
        <div class="d-flex justify-space-between align-center mb-6">
          <div>
            <h1 class="text-h4 font-weight-bold">My Claims</h1>
            <p class="text-body-2 text-grey">
              Manage your insurance claims
            </p>
          </div>

          <v-btn
            color="primary"
            size="large"
            @click="showInsuranceModal = true"
          >
            <v-icon start icon="mdi-plus" />
            New Claim
          </v-btn>
        </div>

        <!-- Stats Cards -->
        <v-row class="mb-6">
          <v-col cols="12" sm="6" md="3">
            <v-card color="primary" variant="flat" class="rounded-lg">
              <v-card-text class="d-flex align-center">
                <v-avatar color="white" size="48" class="mr-4">
                  <v-icon color="primary" icon="mdi-file-document-multiple" />
                </v-avatar>
                <div>
                  <div class="text-h4 font-weight-bold">{{ stats.total }}</div>
                  <div class="text-body-2 opacity-80">Total Claims</div>
                </div>
              </v-card-text>
            </v-card>
          </v-col>
          <v-col cols="12" sm="6" md="3">
            <v-card color="grey" variant="flat" class="rounded-lg">
              <v-card-text class="d-flex align-center">
                <v-avatar color="white" size="48" class="mr-4">
                  <v-icon color="grey" icon="mdi-pencil" />
                </v-avatar>
                <div>
                  <div class="text-h4 font-weight-bold">{{ stats.draft }}</div>
                  <div class="text-body-2 opacity-80">Draft</div>
                </div>
              </v-card-text>
            </v-card>
          </v-col>
          <v-col cols="12" sm="6" md="3">
            <v-card color="info" variant="flat" class="rounded-lg">
              <v-card-text class="d-flex align-center">
                <v-avatar color="white" size="48" class="mr-4">
                  <v-icon color="info" icon="mdi-send" />
                </v-avatar>
                <div>
                  <div class="text-h4 font-weight-bold">{{ stats.submitted }}</div>
                  <div class="text-body-2 opacity-80">Submitted</div>
                </div>
              </v-card-text>
            </v-card>
          </v-col>
          <v-col cols="12" sm="6" md="3">
            <v-card color="success" variant="flat" class="rounded-lg">
              <v-card-text class="d-flex align-center">
                <v-avatar color="white" size="48" class="mr-4">
                  <v-icon color="success" icon="mdi-check-circle" />
                </v-avatar>
                <div>
                  <div class="text-h4 font-weight-bold">{{ stats.approved }}</div>
                  <div class="text-body-2 opacity-80">Approved</div>
                </div>
              </v-card-text>
            </v-card>
          </v-col>
        </v-row>

        <!-- Filter Tabs -->
        <v-tabs v-model="statusFilter" color="primary" class="mb-4">
          <v-tab value="all">All</v-tab>
          <v-tab value="DRAFT">Draft</v-tab>
          <v-tab value="SUBMITTED">Submitted</v-tab>
          <v-tab value="REVIEWED">Under Review</v-tab>
          <v-tab value="APPROVED">Approved</v-tab>
          <v-tab value="REJECTED">Rejected</v-tab>
        </v-tabs>

        <!-- Claims Table -->
        <ClaimsTable
          title="Claims"
          icon="mdi-file-document-multiple"
          :headers="headers"
          :items="claims"
          :loading="loading"
          :page="page"
          :total-pages="totalPages"
          @view="handleViewClaim"
          @update:page="page = $event"
        />
      </v-container>
    </v-main>

    <!-- Insurance Select Modal -->
    <InsuranceSelectModal
      v-model="showInsuranceModal"
      :insurances="insurances"
      :loading="loadingInsurances"
      @submit="handleCreateClaim"
    />

    <!-- Snackbar -->
    <v-snackbar v-model="snackbar.show" :color="snackbar.color" :timeout="3000">
      {{ snackbar.message }}
    </v-snackbar>
  </div>
</template>

<script setup lang="ts">
import type { Claim, Insurance, ClaimStatus } from "~/shared/types";

definePageMeta({
  middleware: ["auth"],
});

const { currentUser, userRole } = useAuth();
const { getClaims, createClaim } = useClaims();
const { getInsurances } = useInsurance();
const router = useRouter();

const drawer = ref(true);
const rail = ref(false);
const loading = ref(false);
const loadingInsurances = ref(false);
const showInsuranceModal = ref(false);
const statusFilter = ref<ClaimStatus | "all">("all");
const page = ref(1);
const totalPages = ref(1);
const claims = ref<Claim[]>([]);
const insurances = ref<Insurance[]>([]);

const stats = reactive({
  total: 0,
  draft: 0,
  submitted: 0,
  approved: 0,
});

const snackbar = reactive({
  show: false,
  message: "",
  color: "success",
});

const headers = [
  { title: "Claim Number", key: "claim_number", sortable: true },
  { title: "Status", key: "status", sortable: true },
  { title: "Claim Type", key: "claim_type", sortable: false },
  { title: "Amount", key: "claim_amount", sortable: true },
  { title: "Created", key: "created_at", sortable: true },
  { title: "Actions", key: "actions", sortable: false, align: "center" },
];

const showMessage = (message: string, color: string = "success") => {
  snackbar.message = message;
  snackbar.color = color;
  snackbar.show = true;
};

const fetchClaims = async () => {
  loading.value = true;
  try {
    const data = await getClaims({
      status: statusFilter.value,
      page: page.value,
      page_size: 10,
    });
    claims.value = data.items;
    totalPages.value = data.total_pages;
    stats.total = data.total;

    // Count stats
    const allClaims = await getClaims({ page_size: 100 });
    stats.draft = allClaims.items.filter((c) => c.status === "DRAFT").length;
    stats.submitted = allClaims.items.filter((c) => c.status === "SUBMITTED").length;
    stats.approved = allClaims.items.filter((c) => c.status === "APPROVED").length;
  } catch (error) {
    showMessage("Failed to load claims", "error");
  } finally {
    loading.value = false;
  }
};

const fetchInsurances = async () => {
  loadingInsurances.value = true;
  try {
    const data = await getInsurances({ page_size: 100 });
    insurances.value = data.items;
  } catch (error) {
    showMessage("Failed to load insurances", "error");
  } finally {
    loadingInsurances.value = false;
  }
};

const handleViewClaim = (claim: Claim) => {
  router.push(`/user/claim-insurance/${claim.id}`);
};

const handleCreateClaim = async (insurance: Insurance) => {
  try {
    const claim = await createClaim({ insurance_id: insurance.id });
    showMessage("Claim created successfully!");
    showInsuranceModal.value = false;
    router.push(`/user/claim-insurance/${claim.id}`);
  } catch (error: any) {
    const message = error.response?.data?.detail || "Failed to create claim";
    showMessage(message, "error");
  }
};

// Watch for filter changes
watch([statusFilter, page], () => {
  fetchClaims();
});

onMounted(() => {
  fetchClaims();
  fetchInsurances();
});
</script>
