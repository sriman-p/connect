/**
 * Authentication Store (Zustand)
 * Global state management for user authentication
 */

import { create } from 'zustand';
import { devtools, persist } from 'zustand/middleware';
import type { User } from '../types/api';
import {
  login as apiLogin,
  register as apiRegister,
  logout as apiLogout,
  getProfile,
} from '../api/auth';
import { clearTokens, getRefreshToken, isAuthenticated } from '../utils/token';

interface AuthState {
  // State
  user: User | null;
  isLoading: boolean;
  isAuthenticated: boolean;
  error: string | null;

  // Actions
  login: (email: string, password: string) => Promise<void>;
  register: (data: {
    email: string;
    full_name: string;
    password: string;
    password_confirm: string;
    timezone?: string;
  }) => Promise<void>;
  logout: () => Promise<void>;
  fetchProfile: () => Promise<void>;
  updateUser: (user: User) => void;
  clearError: () => void;
  checkAuth: () => void;
}

export const useAuthStore = create<AuthState>()(
  devtools(
    persist(
      (set, get) => ({
        // Initial state
        user: null,
        isLoading: false,
        isAuthenticated: false,
        error: null,

        // Login action
        login: async (email: string, password: string) => {
          set({ isLoading: true, error: null });

          try {
            const response = await apiLogin({ email, password });

            set({
              user: response.user,
              isAuthenticated: true,
              isLoading: false,
              error: null,
            });
          } catch (error: any) {
            const errorMessage =
              error.response?.data?.detail ||
              error.response?.data?.error ||
              'Login failed. Please check your credentials.';

            set({
              user: null,
              isAuthenticated: false,
              isLoading: false,
              error: errorMessage,
            });

            throw error;
          }
        },

        // Register action
        register: async (data) => {
          set({ isLoading: true, error: null });

          try {
            const response = await apiRegister(data);

            set({
              user: response.user,
              isAuthenticated: true,
              isLoading: false,
              error: null,
            });
          } catch (error: any) {
            let errorMessage = 'Registration failed. Please try again.';

            // Extract error messages from response
            if (error.response?.data) {
              const errors = error.response.data;

              if (typeof errors === 'object') {
                // Combine all error messages
                errorMessage = Object.values(errors)
                  .flat()
                  .join(' ');
              } else if (typeof errors === 'string') {
                errorMessage = errors;
              }
            }

            set({
              user: null,
              isAuthenticated: false,
              isLoading: false,
              error: errorMessage,
            });

            throw error;
          }
        },

        // Logout action
        logout: async () => {
          set({ isLoading: true });

          try {
            const refreshToken = getRefreshToken();

            if (refreshToken) {
              await apiLogout(refreshToken);
            }
          } catch (error) {
            console.error('Logout error:', error);
          } finally {
            clearTokens();

            set({
              user: null,
              isAuthenticated: false,
              isLoading: false,
              error: null,
            });

            // Redirect to login
            if (typeof window !== 'undefined') {
              window.location.href = '/login';
            }
          }
        },

        // Fetch user profile
        fetchProfile: async () => {
          if (!isAuthenticated()) {
            set({ user: null, isAuthenticated: false });
            return;
          }

          set({ isLoading: true });

          try {
            const user = await getProfile();

            set({
              user,
              isAuthenticated: true,
              isLoading: false,
              error: null,
            });
          } catch (error: any) {
            console.error('Failed to fetch profile:', error);

            // If 401, clear auth state
            if (error.response?.status === 401) {
              clearTokens();

              set({
                user: null,
                isAuthenticated: false,
                isLoading: false,
                error: null,
              });
            } else {
              set({ isLoading: false });
            }
          }
        },

        // Update user in state (after profile update)
        updateUser: (user: User) => {
          set({ user });
        },

        // Clear error
        clearError: () => {
          set({ error: null });
        },

        // Check authentication status
        checkAuth: () => {
          const authenticated = isAuthenticated();

          if (!authenticated) {
            clearTokens();

            set({
              user: null,
              isAuthenticated: false,
            });
          } else {
            set({ isAuthenticated: true });

            // Fetch profile if authenticated but no user data
            if (!get().user) {
              get().fetchProfile();
            }
          }
        },
      }),
      {
        name: 'auth-storage',
        partialize: (state) => ({
          user: state.user,
          isAuthenticated: state.isAuthenticated,
        }),
      }
    ),
    { name: 'AuthStore' }
  )
);
