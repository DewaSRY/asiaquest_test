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
            <h1 class="text-h4 font-weight-bold">Claims for Review</h1>
            <p class="text-body-2 text-grey">
              Review submitted insurance claims
            </p>
          </div>
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
            <v-card color="info" variant="flat" class="rounded-lg">
              <v-card-text class="d-flex align-center">
                <v-avatar color="white" size="48" class="mr-4">
                  <v-icon color="info" icon="mdi-clock-outline" />
                </v-avatar>
                <div>
                  <div class="text-h4 font-weight-bold">{{ stats.pending }}</div>
                  <div class="text-body-2 opacity-80">Pending Review</div>
                </div>
              </v-card-text>
            </v-card>
          </v-col>
          <v-col cols="12" sm="6" md="3">
            <v-card color="warning" variant="flat" class="rounded-lg">
              <v-card-text class="d-flex align-center">
                <v-avatar color="white" size="48" class="mr-4">
                  <v-icon color="warning" icon="mdi-eye-check" />
                </v-avatar>
                <div>
                  <div class="text-h4 font-weight-bold">{{ stats.reviewed }}</div>
                  <div class="text-body-2 opacity-80">Reviewed</div>
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
                  <div class="text-h4 font-weight-bold">{{ stats.completed }}</div>
                  <div class="text-body-2 opacity-80">Completed</div>
                </div>
              </v-card-text>
            </v-card>
          </v-col>
        </v-row>

        <!-- Filter Tabs -->
        <v-tabs v-model="statusFilter" color="primary" class="mb-4">
          <v-tab value="all">All</v-tab>
          <v-tab value="SUBMITTED">Pending Review</v-tab>
          <v-tab value="REVIEWED">Reviewed</v-tab>
          <v-tab value="APPROVED">Approved</v-tab>
          <v-tab value="REJECTED">Rejected</v-tab>
        </v-tabs>

        <!-- Claims Table -->
        <ClaimsTable
          title="Claims"
          icon="mdi-clipboard-text-search"
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

    <!-- Snackbar -->
    <v-snackbar v-model="snackbar.show" :color="snackbar.color" :timeout="3000">
      {{ snackbar.message }}
    </v-snackbar>
  </div>
</template>

<script setup lang="ts">
import type { Claim, ClaimStatus } from "~/shared/types";

definePageMeta({
  middleware: ["auth", "verifier"],
});

const { currentUser, userRole } = useAuth();
const { getClaims } = useClaims();
const router = useRouter();

const drawer = ref(true);
const rail = ref(false);
const loading = ref(false);
const statusFilter = ref<ClaimStatus | "all">("SUBMITTED");
const page = ref(1);
const totalPages = ref(1);
const claims = ref<Claim[]>([]);

const stats = reactive({
  total: 0,
  pending: 0,
  reviewed: 0,
  completed: 0,
});

const snackbar = reactive({
  show: false,
  message: "",
  color: "success",
});

const headers = [
  { title: "Claim Number", key: "claim_number", sortable: true },
  { title: "Status", key: "status", sortable: true },
  { title: "Claimant", key: "first_name", sortable: false },
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

    // Count stats
    const allClaims = await getClaims({ page_size: 100 });
    stats.total = allClaims.total;
    stats.pending = allClaims.items.filter((c) => c.status === "SUBMITTED").length;
    stats.reviewed = allClaims.items.filter((c) => c.status === "REVIEWED").length;
    stats.completed = allClaims.items.filter(
      (c) => c.status === "APPROVED" || c.status === "REJECTED"
    ).length;
  } catch (error) {
    showMessage("Failed to load claims", "error");
  } finally {
    loading.value = false;
  }
};

const handleViewClaim = (claim: Claim) => {
  router.push(`/verifier/claim-insurance/${claim.id}`);
};

// Watch for filter changes
watch([statusFilter, page], () => {
  fetchClaims();
});

onMounted(() => {
  fetchClaims();
});
</script>
