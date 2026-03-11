import { defineStore } from "pinia";
import type { User, TokenResponse } from "~/shared/types";

interface AuthState {
  user: User | null;
  accessToken: string | null;
  refreshToken: string | null;
  isAuthenticated: boolean;
}

export const useAuthStore = defineStore("auth", {
  state: (): AuthState => ({
    user: null,
    accessToken: null,
    refreshToken: null,
    isAuthenticated: false,
  }),

  getters: {
    currentUser: (state) => state.user,
    userRole: (state) => state.user?.role || null,
    isUser: (state) => state.user?.role === "USER",
    isVerifier: (state) => state.user?.role === "VERIFIER",
    isApprover: (state) => state.user?.role === "APPROVER",
    token: (state) => state.accessToken,
  },

  actions: {
    setTokens(tokens: TokenResponse) {
      this.accessToken = tokens.access_token;
      this.refreshToken = tokens.refresh_token;
      this.isAuthenticated = true;

      // Persist to localStorage
      if (import.meta.client) {
        localStorage.setItem("access_token", tokens.access_token);
        localStorage.setItem("refresh_token", tokens.refresh_token);
      }
    },

    setUser(user: User) {
      this.user = user;
    },

    loadFromStorage() {
      if (import.meta.client) {
        const accessToken = localStorage.getItem("access_token");
        const refreshToken = localStorage.getItem("refresh_token");

        if (accessToken && refreshToken) {
          this.accessToken = accessToken;
          this.refreshToken = refreshToken;
          this.isAuthenticated = true;
        }
      }
    },

    logout() {
      this.user = null;
      this.accessToken = null;
      this.refreshToken = null;
      this.isAuthenticated = false;

      if (import.meta.client) {
        localStorage.removeItem("access_token");
        localStorage.removeItem("refresh_token");
      }
    },

    async refreshTokens() {
      if (!this.refreshToken) {
        this.logout();
        return false;
      }

      try {
        const response = await $fetch<TokenResponse>("/api/auth/refresh", {
          method: "POST",
          body: { refresh_token: this.refreshToken },
        });

        this.setTokens(response);
        return true;
      } catch (error) {
        this.logout();
        return false;
      }
    },
  },
});
