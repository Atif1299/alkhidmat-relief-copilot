/** Client-side auth token + role from JWT login. */

import type { DeskRole } from "./roles";

const TOKEN_KEY = "aiddesk_token";
const USER_KEY = "aiddesk_user";

export type AuthUser = {
  email: string;
  role: DeskRole;
  user_id: string;
};

export function getToken(): string | null {
  if (typeof window === "undefined") return null;
  return window.localStorage.getItem(TOKEN_KEY);
}

export function getAuthUser(): AuthUser | null {
  if (typeof window === "undefined") return null;
  const raw = window.localStorage.getItem(USER_KEY);
  if (!raw) return null;
  try {
    return JSON.parse(raw) as AuthUser;
  } catch {
    return null;
  }
}

export function setAuth(token: string, user: AuthUser) {
  window.localStorage.setItem(TOKEN_KEY, token);
  window.localStorage.setItem(USER_KEY, JSON.stringify(user));
  window.localStorage.setItem("aiddesk_role", user.role);
}

export function clearAuth() {
  window.localStorage.removeItem(TOKEN_KEY);
  window.localStorage.removeItem(USER_KEY);
  window.localStorage.removeItem("aiddesk_role");
}

export function authHeaders(extra?: HeadersInit): HeadersInit {
  const token = getToken();
  const base: Record<string, string> = {
    ...(extra as Record<string, string>),
  };
  if (token) base.Authorization = `Bearer ${token}`;
  return base;
}
