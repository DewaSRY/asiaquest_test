<template>
  <v-card class="elevation-2">
    <v-card-title class="d-flex align-center pa-4">
      <v-icon icon="mdi-file-document-outline" class="mr-2" />
      Claim Information
      <v-spacer />
      <StatusChip :status="claim.status" variant="elevated" />
    </v-card-title>

    <v-divider />

    <v-card-text class="pa-4">
      <v-row>
        <v-col cols="12" md="6">
          <div class="text-caption text-grey">Claim Number</div>
          <div class="text-body-1 font-weight-bold">{{ claim.claim_number }}</div>
        </v-col>
        <v-col cols="12" md="6">
          <div class="text-caption text-grey">Created At</div>
          <div class="text-body-1">{{ formatDate(claim.created_at) }}</div>
        </v-col>
      </v-row>

      <v-divider class="my-4" />

      <h4 class="text-subtitle-1 font-weight-bold mb-3">
        <v-icon icon="mdi-account" size="small" class="mr-1" />
        Personal Information
      </h4>
      <v-row>
        <v-col cols="12" md="6">
          <div class="text-caption text-grey">Full Name</div>
          <div class="text-body-1">
            {{ claim.first_name || "-" }} {{ claim.last_name || "" }}
          </div>
        </v-col>
        <v-col cols="12" md="6">
          <div class="text-caption text-grey">Email</div>
          <div class="text-body-1">{{ claim.email || "-" }}</div>
        </v-col>
        <v-col cols="12" md="6">
          <div class="text-caption text-grey">Phone Number</div>
          <div class="text-body-1">{{ claim.phone_number || "-" }}</div>
        </v-col>
        <v-col cols="12" md="6">
          <div class="text-caption text-grey">ID Number</div>
          <div class="text-body-1">{{ claim.user_id_number || "-" }}</div>
        </v-col>
      </v-row>

      <v-divider class="my-4" />

      <h4 class="text-subtitle-1 font-weight-bold mb-3">
        <v-icon icon="mdi-shield-outline" size="small" class="mr-1" />
        Policy Information
      </h4>
      <v-row>
        <v-col cols="12" md="6">
          <div class="text-caption text-grey">Policy Number</div>
          <div class="text-body-1">{{ claim.policy_number || "-" }}</div>
        </v-col>
        <v-col cols="12" md="6">
          <div class="text-caption text-grey">Policy Holder Number</div>
          <div class="text-body-1">{{ claim.policy_holder_number || "-" }}</div>
        </v-col>
        <v-col cols="12" md="6">
          <div class="text-caption text-grey">Coverage Start Date</div>
          <div class="text-body-1">
            {{ claim.coverage_start_date ? formatDate(claim.coverage_start_date) : "-" }}
          </div>
        </v-col>
        <v-col cols="12" md="6">
          <div class="text-caption text-grey">Coverage End Date</div>
          <div class="text-body-1">
            {{ claim.coverage_end_date ? formatDate(claim.coverage_end_date) : "-" }}
          </div>
        </v-col>
      </v-row>

      <v-divider class="my-4" />

      <h4 class="text-subtitle-1 font-weight-bold mb-3">
        <v-icon icon="mdi-file-document" size="small" class="mr-1" />
        Claim Details
      </h4>
      <v-row>
        <v-col cols="12" md="6">
          <div class="text-caption text-grey">Claim Date</div>
          <div class="text-body-1">
            {{ claim.claim_date ? formatDate(claim.claim_date) : "-" }}
          </div>
        </v-col>
        <v-col cols="12" md="6">
          <div class="text-caption text-grey">Claim Type</div>
          <div class="text-body-1">{{ claim.claim_type || "-" }}</div>
        </v-col>
        <v-col cols="12" md="6">
          <div class="text-caption text-grey">Claim Amount</div>
          <div class="text-h6 text-primary font-weight-bold">
            {{ claim.claim_amount ? formatCurrency(claim.claim_amount) : "-" }}
          </div>
        </v-col>
        <v-col cols="12">
          <div class="text-caption text-grey">Description</div>
          <div class="text-body-1">{{ claim.description || "-" }}</div>
        </v-col>
      </v-row>

      <!-- Review Section -->
      <template v-if="claim.review">
        <v-divider class="my-4" />
        <h4 class="text-subtitle-1 font-weight-bold mb-3">
          <v-icon icon="mdi-clipboard-check" size="small" class="mr-1" />
          Review Information
        </h4>
        <v-alert type="info" variant="tonal" class="mb-3">
          <div class="text-caption">Reviewed At</div>
          <div class="text-body-2">{{ formatDate(claim.review.reviewed_at) }}</div>
          <v-divider class="my-2" />
          <div class="text-caption">Review Summary</div>
          <div class="text-body-1">{{ claim.review.review_summary }}</div>
        </v-alert>
      </template>

      <!-- Approval Section -->
      <template v-if="claim.approval">
        <v-divider class="my-4" />
        <h4 class="text-subtitle-1 font-weight-bold mb-3">
          <v-icon icon="mdi-gavel" size="small" class="mr-1" />
          Decision Information
        </h4>
        <v-alert
          :type="claim.approval.decision === 'APPROVED' ? 'success' : 'error'"
          variant="tonal"
        >
          <div class="text-caption">Decision</div>
          <div class="text-body-1 font-weight-bold text-uppercase">
            {{ claim.approval.decision }}
          </div>
          <v-divider class="my-2" />
          <div class="text-caption">Decided At</div>
          <div class="text-body-2">{{ formatDate(claim.approval.decided_at) }}</div>
          <template v-if="claim.approval.reason">
            <v-divider class="my-2" />
            <div class="text-caption">Reason</div>
            <div class="text-body-1">{{ claim.approval.reason }}</div>
          </template>
        </v-alert>
      </template>
    </v-card-text>
  </v-card>
</template>

<script setup lang="ts">
import type { Claim } from "~/shared/types";

defineProps<{
  claim: Claim;
}>();

const formatCurrency = (amount: number) => {
  return new Intl.NumberFormat("en-US", {
    style: "currency",
    currency: "USD",
  }).format(amount);
};

const formatDate = (dateString: string) => {
  return new Date(dateString).toLocaleDateString("en-US", {
    year: "numeric",
    month: "long",
    day: "numeric",
    hour: "2-digit",
    minute: "2-digit",
  });
};
</script>
