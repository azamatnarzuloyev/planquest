"use client";

import { createContext, useContext, useEffect, useState, ReactNode } from "react";
import {
  isTelegram,
  ready,
  expand,
  getColorScheme,
  getViewport,
  onThemeChanged,
  onViewportChanged,
  disableVerticalSwipes,
  setHeaderColor,
  setBackgroundColor,
  type ColorScheme,
  type ViewportInfo,
} from "@/lib/telegram";
import { applyTelegramTheme, getResolvedTheme } from "@/lib/theme";

interface TelegramState {
  isTg: boolean;
  colorScheme: ColorScheme;
  viewport: ViewportInfo;
}

const TelegramContext = createContext<TelegramState>({
  isTg: false,
  colorScheme: "dark",
  viewport: {
    height: 0,
    stableHeight: 0,
    isExpanded: false,
    safeAreaTop: 0,
    safeAreaBottom: 0,
    safeAreaLeft: 0,
    safeAreaRight: 0,
    contentSafeAreaTop: 0,
    contentSafeAreaBottom: 0,
  },
});

export function TelegramProvider({ children }: { children: ReactNode }) {
  const [isTg, setIsTg] = useState(false);
  const [colorScheme, setColorScheme] = useState<ColorScheme>("dark");
  const [viewport, setViewport] = useState<ViewportInfo>({
    height: 0, stableHeight: 0, isExpanded: false,
    safeAreaTop: 0, safeAreaBottom: 0, safeAreaLeft: 0, safeAreaRight: 0,
    contentSafeAreaTop: 0, contentSafeAreaBottom: 0,
  });

  useEffect(() => {
    const tg = isTelegram();
    setIsTg(tg);

    // Apply theme
    applyTelegramTheme();
    setColorScheme(getColorScheme());

    if (tg) {
      // Signal ready
      ready();
      // Expand to full height
      expand();
      // Disable swipe-to-close for scrollable content
      disableVerticalSwipes();

      // Set native colors
      const theme = getResolvedTheme();
      setHeaderColor(theme.header_bg_color);
      setBackgroundColor(theme.bg_color);

      // Update viewport
      setViewport(getViewport());
    }

    // Listen for theme changes
    const cleanupTheme = onThemeChanged(() => {
      applyTelegramTheme();
      setColorScheme(getColorScheme());
    });

    // Listen for viewport changes
    const cleanupViewport = onViewportChanged(({ isStateStable }) => {
      if (isStateStable) {
        setViewport(getViewport());
      }
    });

    return () => {
      cleanupTheme();
      cleanupViewport();
    };
  }, []);

  return (
    <TelegramContext.Provider value={{ isTg, colorScheme, viewport }}>
      {children}
    </TelegramContext.Provider>
  );
}

export function useTelegramContext() {
  return useContext(TelegramContext);
}
