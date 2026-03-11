export * from "./auth";
export * from "./claim";
export * from "./insurance";

// Common API response wrapper
export interface ApiResponse<T> {
  data: T;
  message?: string;
}

// API Error
export interface ApiError {
  detail: string;
  status_code?: number;
}
