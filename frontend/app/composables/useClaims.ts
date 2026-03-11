import type {
  Claim,
  PaginatedClaims,
  CreateClaimInput,
  UpdateClaimInput,
  ReviewClaimInput,
  ApproveClaimInput,
  ClaimStatus,
} from "~/shared/types";
import { useApi } from "./useApi";

export const useClaims = () => {
  const api = useApi();

  const getClaims = async (params?: {
    status?: ClaimStatus | "all";
    page?: number;
    page_size?: number;
  }): Promise<PaginatedClaims> => {
    const response = await api.get<PaginatedClaims>("/claims", { params });
    return response.data;
  };

  const getClaim = async (id: number): Promise<Claim> => {
    const response = await api.get<Claim>(`/claims/${id}`);
    return response.data;
  };

  const createClaim = async (data: CreateClaimInput): Promise<Claim> => {
    const response = await api.post<Claim>("/claims", data);
    return response.data;
  };

  const updateClaim = async (
    id: number,
    data: UpdateClaimInput
  ): Promise<Claim> => {
    const response = await api.patch<Claim>(`/claims/${id}`, data);
    return response.data;
  };

  const submitClaim = async (id: number): Promise<Claim> => {
    const response = await api.post<Claim>(`/claims/${id}/submit`);
    return response.data;
  };

  const reviewClaim = async (
    id: number,
    data: ReviewClaimInput
  ): Promise<Claim> => {
    const response = await api.post<Claim>(`/claims/${id}/review`, data);
    return response.data;
  };

  const approveClaim = async (
    id: number,
    data: ApproveClaimInput
  ): Promise<Claim> => {
    const response = await api.post<Claim>(`/claims/${id}/approve`, data);
    return response.data;
  };

  const deleteClaim = async (id: number): Promise<void> => {
    await api.delete(`/claims/${id}`);
  };

  return {
    getClaims,
    getClaim,
    createClaim,
    updateClaim,
    submitClaim,
    reviewClaim,
    approveClaim,
    deleteClaim,
  };
};
