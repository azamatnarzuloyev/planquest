"use client";

import { TelegramProvider } from "@/contexts/TelegramContext";
import { AuthProvider, useAuth } from "@/contexts/AuthContext";
import BottomNav from "@/components/BottomNav";
import LoadingScreen from "@/components/LoadingScreen";

function AppContent({ children }: { children: React.ReactNode }) {
  const { isLoading } = useAuth();

  if (isLoading) {
    return <LoadingScreen />;
  }

  return (
    <>
      <main className="pb-20 min-h-screen">{children}</main>
      <BottomNav />
    </>
  );
}

export function AppShell({ children }: { children: React.ReactNode }) {
  return (
    <TelegramProvider>
      <AuthProvider>
        <AppContent>{children}</AppContent>
      </AuthProvider>
    </TelegramProvider>
  );
}
