import type { PaginatedInsurance, Insurance } from "~/shared/types";
import { useApi } from "./useApi";

export const useInsurance = () => {
  const api = useApi();

  const getInsurances = async (params?: {
    page?: number;
    page_size?: number;
  }): Promise<PaginatedInsurance> => {
    const response = await api.get<PaginatedInsurance>("/insurances", {
      params,
    });
    return response.data;
  };

  const getInsurance = async (id: number): Promise<Insurance> => {
    const response = await api.get<Insurance>(`/insurances/${id}`);
    return response.data;
  };

  return {
    getInsurances,
    getInsurance,
  };
};
