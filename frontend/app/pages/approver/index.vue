<template>
  <v-container fluid class="pa-6">
        <div class="d-flex justify-space-between align-center mb-6">
          <div>
            <h1 class="text-h4 font-weight-bold">Claims for Approval</h1>
            <p class="text-body-2 text-grey">
              Approve or reject reviewed insurance claims
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
            <v-card color="warning" variant="flat" class="rounded-lg">
              <v-card-text class="d-flex align-center">
                <v-avatar color="white" size="48" class="mr-4">
                  <v-icon color="warning" icon="mdi-clock-outline" />
                </v-avatar>
                <div>
                  <div class="text-h4 font-weight-bold">{{ stats.pending }}</div>
                  <div class="text-body-2 opacity-80">Pending Approval</div>
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
          <v-col cols="12" sm="6" md="3">
            <v-card color="error" variant="flat" class="rounded-lg">
              <v-card-text class="d-flex align-center">
                <v-avatar color="white" size="48" class="mr-4">
                  <v-icon color="error" icon="mdi-close-circle" />
                </v-avatar>
                <div>
                  <div class="text-h4 font-weight-bold">{{ stats.rejected }}</div>
                  <div class="text-body-2 opacity-80">Rejected</div>
                </div>
              </v-card-text>
            </v-card>
          </v-col>
        </v-row>

        <!-- Filter Tabs -->
        <v-tabs v-model="statusFilter" color="primary" class="mb-4">
          <v-tab value="all">All</v-tab>
          <v-tab value="REVIEWED">Pending Approval</v-tab>
          <v-tab value="APPROVED">Approved</v-tab>
          <v-tab value="REJECTED">Rejected</v-tab>
        </v-tabs>

        <!-- Claims Table -->
        <ClaimsTable
          title="Claims"
          icon="mdi-check-decagram"
          :headers="headers"
          :items="claims"
          :loading="loading"
          :page="page"
          :total-pages="totalPages"
          @view="handleViewClaim"
          @update:page="page = $event"
        />
    <!-- Snackbar -->
    <v-snackbar v-model="snackbar.show" :color="snackbar.color" :timeout="3000">
      {{ snackbar.message }}
    </v-snackbar>
  </v-container>
</template>

<script setup lang="ts">
import type { Claim, ClaimStatus } from "~/shared/types";
import ClaimsTable from "~/components/tabledata/ClaimsTable.vue";
import { useClaims } from "~/composables/useClaims";
import { useRouter } from "vue-router";

definePageMeta({
   layout: "dashboard",
  middleware: ["auth", "approver"],
});

const { getClaims } = useClaims();
const router = useRouter();

const loading = ref(false);
const statusFilter = ref<ClaimStatus | "all">("REVIEWED");
const page = ref(1);
const totalPages = ref(1);
const claims = ref<Claim[]>([]);

const stats = reactive({
  total: 0,
  pending: 0,
  approved: 0,
  rejected: 0,
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
    stats.pending = allClaims.items.filter((c) => c.status === "REVIEWED").length;
    stats.approved = allClaims.items.filter((c) => c.status === "APPROVED").length;
    stats.rejected = allClaims.items.filter((c) => c.status === "REJECTED").length;
  } catch (error) {
    showMessage("Failed to load claims", "error");
  } finally {
    loading.value = false;
  }
};

const handleViewClaim = (claim: Claim) => {
  router.push(`/approver/claim-insurance/${claim.id}`);
};

// Watch for filter changes
watch([statusFilter, page], () => {
  fetchClaims();
});

onMounted(() => {
  fetchClaims();
});
</script>
