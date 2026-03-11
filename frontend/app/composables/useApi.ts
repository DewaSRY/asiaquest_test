import axios, { type AxiosInstance, type AxiosError } from "axios";
import { useAuthStore } from "./useAuthStore";

let apiClient: AxiosInstance | null = null;

export const useApi = () => {
  if (!apiClient) {
    apiClient = axios.create({
      baseURL: "/api",
      headers: {
        "Content-Type": "application/json",
      },
    });

    // Request interceptor to add auth token
    apiClient.interceptors.request.use(
      (config) => {
        const authStore = useAuthStore();
        if (authStore.token) {
          config.headers.Authorization = `Bearer ${authStore.token}`;
        }
        return config;
      },
      (error) => Promise.reject(error)
    );

    // Response interceptor to handle token refresh
    apiClient.interceptors.response.use(
      (response) => response,
      async (error: AxiosError) => {
        const originalRequest = error.config;

        // If 401 and we have a refresh token, try to refresh
        if (
          error.response?.status === 401 &&
          originalRequest &&
          !originalRequest.url?.includes("/auth/refresh") &&
          !originalRequest.url?.includes("/auth/login")
        ) {
          const authStore = useAuthStore();
          const refreshed = await authStore.refreshTokens();

          if (refreshed) {
            // Retry the original request
            originalRequest.headers.Authorization = `Bearer ${authStore.token}`;
            return apiClient!.request(originalRequest);
          }

          // Redirect to login
          if (import.meta.client) {
            navigateTo("/");
          }
        }

        return Promise.reject(error);
      }
    );
  }

  return apiClient;
};
