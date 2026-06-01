import { jwtDecode } from 'jwt-decode';

const TOKEN_KEY = 'financial_ai_token';

export const setToken = (token) => {
  if (typeof window !== 'undefined') {
    localStorage.setItem(TOKEN_KEY, token);
  }
};

export const getToken = () => {
  if (typeof window !== 'undefined') {
    return localStorage.getItem(TOKEN_KEY);
  }
  return null;
};

export const removeToken = () => {
  if (typeof window !== 'undefined') {
    localStorage.removeItem(TOKEN_KEY);
  }
};

export const isTokenValid = () => {
  const token = getToken();
  if (!token) return false;

  try {
    const decoded = jwtDecode(token);
    const currentTime = Date.now() / 1000;

    // If token doesn't contain exp, treat it as invalid.
    if (!decoded || typeof decoded.exp !== 'number') return false;

    return decoded.exp > currentTime;
  } catch (error) {
    // Helpful during debugging: token might not be a JWT (or is malformed).
    // This prevents silent redirect loops.
    if (typeof window !== 'undefined') {
      // eslint-disable-next-line no-console
      console.warn('Invalid token in localStorage (not a valid JWT or missing exp).');
    }
    return false;
  }
};

export const getUser = () => {
  const token = getToken();
  if (!token) return null;

  try {
    return jwtDecode(token);
  } catch (error) {
    return null;
  }
};

