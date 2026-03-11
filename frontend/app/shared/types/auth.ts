import { z } from "zod";

// Login schema
export const loginSchema = z.object({
  email: z.string().email("Invalid email address"),
  password: z.string().min(8, "Password must be at least 8 characters"),
});

export type LoginInput = z.infer<typeof loginSchema>;

// Register schema
export const registerSchema = z.object({
  email: z.string().email("Invalid email address"),
  username: z.string().min(3, "Username must be at least 3 characters").max(100),
  password: z.string().min(8, "Password must be at least 8 characters").max(100),
});

export type RegisterInput = z.infer<typeof registerSchema>;

// Token response
export const tokenResponseSchema = z.object({
  access_token: z.string(),
  refresh_token: z.string(),
  token_type: z.string(),
});

export type TokenResponse = z.infer<typeof tokenResponseSchema>;

// User response
export const userSchema = z.object({
  id: z.number(),
  email: z.string().email(),
  username: z.string(),
  role: z.enum(["USER", "VERIFIER", "APPROVER"]),
  created_at: z.string(),
  updated_at: z.string(),
});

export type User = z.infer<typeof userSchema>;

// Refresh token schema
export const refreshTokenSchema = z.object({
  refresh_token: z.string(),
});

export type RefreshTokenInput = z.infer<typeof refreshTokenSchema>;
