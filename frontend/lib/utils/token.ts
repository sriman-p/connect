/**
 * JWT Token Management Utilities
 * Handles token storage, retrieval, and validation
 */

const ACCESS_TOKEN_KEY = 'connect_access_token';
const REFRESH_TOKEN_KEY = 'connect_refresh_token';

export interface TokenPair {
  access: string;
  refresh: string;
}

/**
 * Store tokens in localStorage
 */
export const setTokens = (tokens: TokenPair): void => {
  if (typeof window === 'undefined') return;

  localStorage.setItem(ACCESS_TOKEN_KEY, tokens.access);
  localStorage.setItem(REFRESH_TOKEN_KEY, tokens.refresh);
};

/**
 * Get access token from localStorage
 */
export const getAccessToken = (): string | null => {
  if (typeof window === 'undefined') return null;

  return localStorage.getItem(ACCESS_TOKEN_KEY);
};

/**
 * Get refresh token from localStorage
 */
export const getRefreshToken = (): string | null => {
  if (typeof window === 'undefined') return null;

  return localStorage.getItem(REFRESH_TOKEN_KEY);
};

/**
 * Remove tokens from localStorage
 */
export const clearTokens = (): void => {
  if (typeof window === 'undefined') return;

  localStorage.removeItem(ACCESS_TOKEN_KEY);
  localStorage.removeItem(REFRESH_TOKEN_KEY);
};

/**
 * Check if user is authenticated (has valid access token)
 */
export const isAuthenticated = (): boolean => {
  const token = getAccessToken();

  if (!token) return false;

  // Check if token is expired
  try {
    const payload = JSON.parse(atob(token.split('.')[1]));
    const expiry = payload.exp * 1000; // Convert to milliseconds

    return Date.now() < expiry;
  } catch (error) {
    console.error('Error parsing token:', error);
    return false;
  }
};

/**
 * Get token expiry time in milliseconds
 */
export const getTokenExpiry = (token: string): number | null => {
  try {
    const payload = JSON.parse(atob(token.split('.')[1]));
    return payload.exp * 1000; // Convert to milliseconds
  } catch (error) {
    console.error('Error parsing token expiry:', error);
    return null;
  }
};

/**
 * Get user ID from access token
 */
export const getUserIdFromToken = (): number | null => {
  const token = getAccessToken();

  if (!token) return null;

  try {
    const payload = JSON.parse(atob(token.split('.')[1]));
    return payload.user_id || null;
  } catch (error) {
    console.error('Error parsing user ID from token:', error);
    return null;
  }
};
