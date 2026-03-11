import type {
  LoginInput,
  RegisterInput,
  TokenResponse,
  User,
} from "~/shared/types";
import { useApi } from "./useApi";
import { useAuthStore } from "./useAuthStore";

export const useAuth = () => {
  const api = useApi();
  const authStore = useAuthStore();

  const login = async (data: LoginInput): Promise<TokenResponse> => {
    const response = await api.post<TokenResponse>("/auth/login", data);
    authStore.setTokens(response.data);
    await fetchCurrentUser();
    return response.data;
  };

  const register = async (data: RegisterInput): Promise<User> => {
    const response = await api.post<User>("/auth/register", data);
    return response.data;
  };

  const fetchCurrentUser = async (): Promise<User | null> => {
    try {
      const response = await api.get<User>("/auth/me");
      authStore.setUser(response.data);
      return response.data;
    } catch (error) {
      return null;
    }
  };

  const logout = () => {
    authStore.logout();
    navigateTo("/");
  };

  const initAuth = async () => {
    authStore.loadFromStorage();
    if (authStore.isAuthenticated) {
      await fetchCurrentUser();
    }
  };

  return {
    login,
    register,
    logout,
    fetchCurrentUser,
    initAuth,
    isAuthenticated: computed(() => authStore.isAuthenticated),
    currentUser: computed(() => authStore.currentUser),
    userRole: computed(() => authStore.userRole),
  };
};
