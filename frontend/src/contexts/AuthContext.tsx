"use client";

import { createContext, useContext, useEffect, useState, useCallback, ReactNode } from "react";
import { authTelegram, getMe, getMyProgress } from "@/lib/api";
import { getInitData, isTelegram } from "@/lib/telegram";
import type { UserResponse, UserProgressResponse } from "@/types";

interface AuthState {
  user: UserResponse | null;
  progress: UserProgressResponse | null;
  isLoading: boolean;
  isAuthenticated: boolean;
  refreshProgress: () => Promise<void>;
  refreshUser: () => Promise<void>;
}

const AuthContext = createContext<AuthState>({
  user: null,
  progress: null,
  isLoading: true,
  isAuthenticated: false,
  refreshProgress: async () => {},
  refreshUser: async () => {},
});

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<UserResponse | null>(null);
  const [progress, setProgress] = useState<UserProgressResponse | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  const refreshProgress = useCallback(async () => {
    try {
      const p = await getMyProgress();
      setProgress(p);
    } catch {}
  }, []);

  const refreshUser = useCallback(async () => {
    try {
      const u = await getMe();
      setUser(u);
    } catch {}
  }, []);

  useEffect(() => {
    async function init() {
      try {
        // 1. Check existing token
        const token = localStorage.getItem("token");
        if (token) {
          try {
            const [userData, prog] = await Promise.all([getMe(), getMyProgress()]);
            setUser(userData);
            setProgress(prog);
            setIsLoading(false);
            return;
          } catch {
            localStorage.removeItem("token");
          }
        }

        // 2. Telegram auth flow
        if (isTelegram()) {
          const initData = getInitData();
          if (initData) {
            const authResult = await authTelegram(initData);
            localStorage.setItem("token", authResult.access_token);
            setUser(authResult.user);
            const prog = await getMyProgress();
            setProgress(prog);
          }
        }
      } catch (err) {
        console.error("Auth init failed:", err);
      } finally {
        setIsLoading(false);
      }
    }

    init();
  }, []);

  return (
    <AuthContext.Provider
      value={{
        user,
        progress,
        isLoading,
        isAuthenticated: !!user,
        refreshProgress,
        refreshUser,
      }}
    >
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  return useContext(AuthContext);
}
