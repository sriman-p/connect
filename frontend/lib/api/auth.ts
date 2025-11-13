/**
 * Authentication API Service
 * Handles user authentication, registration, and profile management
 */

import apiClient from './client';
import { setTokens, clearTokens } from '../utils/token';
import type {
  LoginRequest,
  LoginResponse,
  RegisterRequest,
  RegisterResponse,
  User,
} from '../types/api';

/**
 * Login user with email and password
 */
export const login = async (
  credentials: LoginRequest
): Promise<LoginResponse> => {
  const response = await apiClient.post<LoginResponse>(
    '/auth/login/',
    credentials
  );

  // Store tokens
  setTokens(response.data.tokens);

  return response.data;
};

/**
 * Register new user
 */
export const register = async (
  data: RegisterRequest
): Promise<RegisterResponse> => {
  const response = await apiClient.post<RegisterResponse>(
    '/auth/register/',
    data
  );

  // Store tokens
  setTokens(response.data.tokens);

  return response.data;
};

/**
 * Logout user (blacklist refresh token)
 */
export const logout = async (refreshToken: string): Promise<void> => {
  try {
    await apiClient.post('/auth/logout/', { refresh: refreshToken });
  } catch (error) {
    console.error('Logout error:', error);
  } finally {
    // Always clear tokens locally
    clearTokens();
  }
};

/**
 * Get current user profile
 */
export const getProfile = async (): Promise<User> => {
  const response = await apiClient.get<User>('/auth/profile/');
  return response.data;
};

/**
 * Update user profile
 */
export const updateProfile = async (data: Partial<User>): Promise<User> => {
  const response = await apiClient.patch<User>('/auth/profile/', data);
  return response.data;
};

/**
 * Change password
 */
export const changePassword = async (data: {
  current_password: string;
  new_password: string;
  new_password_confirm: string;
}): Promise<{ message: string }> => {
  const response = await apiClient.post<{ message: string }>(
    '/auth/password/change/',
    data
  );
  return response.data;
};

/**
 * Request password reset
 */
export const requestPasswordReset = async (email: string): Promise<void> => {
  await apiClient.post('/auth/password/reset/', { email });
};

/**
 * Confirm password reset with token
 */
export const confirmPasswordReset = async (data: {
  token: string;
  new_password: string;
  new_password_confirm: string;
}): Promise<void> => {
  await apiClient.post('/auth/password/reset/confirm/', data);
};

/**
 * Verify email with token
 */
export const verifyEmail = async (token: string): Promise<void> => {
  await apiClient.post('/auth/email/verify/', { token });
};
