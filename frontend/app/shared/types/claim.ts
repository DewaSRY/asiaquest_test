import { z } from "zod";

// Claim status enum
export const claimStatusSchema = z.enum([
  "DRAFT",
  "SUBMITTED",
  "REVIEWED",
  "APPROVED",
  "REJECTED",
]);

export type ClaimStatus = z.infer<typeof claimStatusSchema>;

// Create claim input
export const createClaimSchema = z.object({
  insurance_id: z.number().int().positive("Insurance ID is required"),
});

export type CreateClaimInput = z.infer<typeof createClaimSchema>;

// Update claim input
export const updateClaimSchema = z.object({
  first_name: z.string().max(100).optional(),
  last_name: z.string().max(100).optional(),
  email: z.string().email().optional(),
  phone_number: z.string().max(20).optional(),
  user_id_number: z.string().max(50).optional(),
  policy_number: z.string().max(50).optional(),
  policy_holder_number: z.string().max(50).optional(),
  coverage_start_date: z.string().optional(),
  coverage_end_date: z.string().optional(),
  claim_date: z.string().optional(),
  claim_type: z.string().max(100).optional(),
  description: z.string().optional(),
  claim_amount: z.number().min(0).optional(),
});

export type UpdateClaimInput = z.infer<typeof updateClaimSchema>;

// Claim review
export const claimReviewSchema = z.object({
  id: z.number(),
  claim_id: z.number(),
  verifier_id: z.number(),
  review_summary: z.string(),
  reviewed_at: z.string(),
});

export type ClaimReview = z.infer<typeof claimReviewSchema>;

// Claim approval
export const claimApprovalSchema = z.object({
  id: z.number(),
  claim_id: z.number(),
  approver_id: z.number(),
  decision: z.enum(["APPROVED", "REJECTED"]),
  reason: z.string().nullable(),
  decided_at: z.string(),
});

export type ClaimApproval = z.infer<typeof claimApprovalSchema>;

// Full claim response
export const claimSchema = z.object({
  id: z.number(),
  claim_number: z.string(),
  user_id: z.number(),
  insurance_id: z.number(),
  status: claimStatusSchema,
  first_name: z.string().nullable(),
  last_name: z.string().nullable(),
  email: z.string().nullable(),
  phone_number: z.string().nullable(),
  user_id_number: z.string().nullable(),
  policy_number: z.string().nullable(),
  policy_holder_number: z.string().nullable(),
  coverage_start_date: z.string().nullable(),
  coverage_end_date: z.string().nullable(),
  claim_date: z.string().nullable(),
  claim_type: z.string().nullable(),
  description: z.string().nullable(),
  claim_amount: z.number().nullable(),
  created_at: z.string(),
  updated_at: z.string(),
  review: claimReviewSchema.nullable(),
  approval: claimApprovalSchema.nullable(),
});

export type Claim = z.infer<typeof claimSchema>;

// Paginated claims response
export const paginatedClaimsSchema = z.object({
  items: z.array(claimSchema),
  total: z.number(),
  page: z.number(),
  page_size: z.number(),
  total_pages: z.number(),
});

export type PaginatedClaims = z.infer<typeof paginatedClaimsSchema>;

// Review claim input
export const reviewClaimSchema = z.object({
  summary: z.string().min(10, "Review summary must be at least 10 characters"),
});

export type ReviewClaimInput = z.infer<typeof reviewClaimSchema>;

// Approve claim input
export const approveClaimSchema = z.object({
  decision: z.enum(["APPROVED", "REJECTED"]),
  reason: z.string().optional(),
});

export type ApproveClaimInput = z.infer<typeof approveClaimSchema>;
