/**
 * Telegram Theme → CSS Variables mapping.
 * Uses official Telegram CSS variable names from docs.
 * Fallback values for non-Telegram environments.
 */

import { getThemeParams, getColorScheme, type TelegramThemeParams } from "./telegram";

const DARK_DEFAULTS: Required<TelegramThemeParams> = {
  bg_color: "#0a0a0a",
  text_color: "#ffffff",
  hint_color: "#6b7280",
  link_color: "#3b82f6",
  button_color: "#3b82f6",
  button_text_color: "#ffffff",
  secondary_bg_color: "#111827",
  header_bg_color: "#0a0a0a",
  accent_text_color: "#3b82f6",
  section_bg_color: "#111827",
  section_header_text_color: "#9ca3af",
  subtitle_text_color: "#6b7280",
  destructive_text_color: "#ef4444",
  section_separator_color: "#1f2937",
  bottom_bar_bg_color: "#0a0a0a",
};

const LIGHT_DEFAULTS: Required<TelegramThemeParams> = {
  bg_color: "#ffffff",
  text_color: "#000000",
  hint_color: "#6b7280",
  link_color: "#2563eb",
  button_color: "#2563eb",
  button_text_color: "#ffffff",
  secondary_bg_color: "#f3f4f6",
  header_bg_color: "#ffffff",
  accent_text_color: "#2563eb",
  section_bg_color: "#f9fafb",
  section_header_text_color: "#4b5563",
  subtitle_text_color: "#6b7280",
  destructive_text_color: "#dc2626",
  section_separator_color: "#e5e7eb",
  bottom_bar_bg_color: "#ffffff",
};

// Official Telegram CSS variable names
const CSS_VARS: Record<keyof TelegramThemeParams, string> = {
  bg_color: "--tg-theme-bg-color",
  text_color: "--tg-theme-text-color",
  hint_color: "--tg-theme-hint-color",
  link_color: "--tg-theme-link-color",
  button_color: "--tg-theme-button-color",
  button_text_color: "--tg-theme-button-text-color",
  secondary_bg_color: "--tg-theme-secondary-bg-color",
  header_bg_color: "--tg-theme-header-bg-color",
  accent_text_color: "--tg-theme-accent-text-color",
  section_bg_color: "--tg-theme-section-bg-color",
  section_header_text_color: "--tg-theme-section-header-text-color",
  subtitle_text_color: "--tg-theme-subtitle-text-color",
  destructive_text_color: "--tg-theme-destructive-text-color",
  section_separator_color: "--tg-theme-section-separator-color",
  bottom_bar_bg_color: "--tg-theme-bottom-bar-bg-color",
};

/** Apply Telegram theme as CSS variables on <html> */
export function applyTelegramTheme(): void {
  if (typeof document === "undefined") return;

  const scheme = getColorScheme();
  const tgParams = getThemeParams();
  const defaults = scheme === "dark" ? DARK_DEFAULTS : LIGHT_DEFAULTS;
  const merged = { ...defaults, ...tgParams };

  const root = document.documentElement;

  for (const [key, cssVar] of Object.entries(CSS_VARS)) {
    const value = merged[key as keyof TelegramThemeParams];
    if (value) root.style.setProperty(cssVar, value);
  }

  // Also set color scheme
  root.style.setProperty("--tg-color-scheme", scheme);
  root.setAttribute("data-theme", scheme);
}

/** Get resolved theme (Telegram + fallback merged) */
export function getResolvedTheme(): Required<TelegramThemeParams> {
  const scheme = getColorScheme();
  const tgParams = getThemeParams();
  const defaults = scheme === "dark" ? DARK_DEFAULTS : LIGHT_DEFAULTS;
  return { ...defaults, ...tgParams };
}
