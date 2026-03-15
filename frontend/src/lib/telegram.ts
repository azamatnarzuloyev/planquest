/**
 * Telegram Mini App SDK Adapter Layer
 * Based on: https://core.telegram.org/bots/webapps
 *
 * Production-grade wrapper around window.Telegram.WebApp.
 * All Telegram interactions go through this module.
 * Safe to call outside Telegram (graceful fallback).
 */

// ============================
// Types
// ============================

export interface TelegramThemeParams {
  bg_color?: string;
  text_color?: string;
  hint_color?: string;
  link_color?: string;
  button_color?: string;
  button_text_color?: string;
  secondary_bg_color?: string;
  header_bg_color?: string;
  accent_text_color?: string;
  section_bg_color?: string;
  section_header_text_color?: string;
  subtitle_text_color?: string;
  destructive_text_color?: string;
  section_separator_color?: string;
  bottom_bar_bg_color?: string;
}

export interface TelegramUser {
  id: number;
  first_name: string;
  last_name?: string;
  username?: string;
  language_code?: string;
  is_premium?: boolean;
  photo_url?: string;
  allows_write_to_pm?: boolean;
}

export type ColorScheme = "light" | "dark";

export interface ViewportInfo {
  height: number;
  stableHeight: number;
  isExpanded: boolean;
}

export interface SafeAreaInsets {
  top: number;
  bottom: number;
  left: number;
  right: number;
}

export interface MainButtonConfig {
  text: string;
  color?: string;
  textColor?: string;
  isActive?: boolean;
  isVisible?: boolean;
  hasShineEffect?: boolean;
}

export interface PopupButton {
  id?: string;
  type?: "default" | "ok" | "close" | "cancel" | "destructive";
  text?: string;
}

export interface PopupParams {
  title?: string;
  message: string;
  buttons?: PopupButton[];
}

// ============================
// Core accessor
// ============================

function wa(): any | null {
  if (typeof window === "undefined") return null;
  return (window as any).Telegram?.WebApp || null;
}

// ============================
// Detection & Version
// ============================

/** Check if running inside Telegram WebApp */
export function isTelegram(): boolean {
  const w = wa();
  return w !== null && !!w.initData;
}

/** Check if user's Telegram supports a given Bot API version */
export function isVersionAtLeast(version: string): boolean {
  return wa()?.isVersionAtLeast(version) ?? false;
}

/** Get current platform: "android", "ios", "web", etc. */
export function getPlatform(): string {
  return wa()?.platform || "unknown";
}

// ============================
// Init Data
// ============================

/** Get raw initData string for backend auth */
export function getInitData(): string {
  return wa()?.initData || "";
}

/** Get parsed Telegram user from initDataUnsafe */
export function getTelegramUser(): TelegramUser | null {
  const user = wa()?.initDataUnsafe?.user;
  if (!user) return null;
  return user as TelegramUser;
}

/** Get start_param from deep link */
export function getStartParam(): string | null {
  return wa()?.initDataUnsafe?.start_param || null;
}

// ============================
// Lifecycle
// ============================

/** Signal that Mini App is ready — hides loading placeholder */
export function ready(): void {
  wa()?.ready();
}

/** Expand to maximum available height */
export function expand(): void {
  wa()?.expand();
}

/** Close Mini App */
export function close(): void {
  wa()?.close();
}

// ============================
// Fullscreen (Bot API 8.0+)
// ============================

export function requestFullscreen(): void {
  try { wa()?.requestFullscreen(); } catch {}
}

export function exitFullscreen(): void {
  try { wa()?.exitFullscreen(); } catch {}
}

export function isFullscreen(): boolean {
  return wa()?.isFullscreen || false;
}

// ============================
// Orientation (Bot API 8.0+)
// ============================

export function lockOrientation(): void {
  try { wa()?.lockOrientation(); } catch {}
}

export function unlockOrientation(): void {
  try { wa()?.unlockOrientation(); } catch {}
}

// ============================
// Theme & Colors
// ============================

export function getColorScheme(): ColorScheme {
  return wa()?.colorScheme || "dark";
}

export function getThemeParams(): TelegramThemeParams {
  return wa()?.themeParams || {};
}

export function setHeaderColor(color: string): void {
  try { wa()?.setHeaderColor(color); } catch {}
}

export function setBackgroundColor(color: string): void {
  try { wa()?.setBackgroundColor(color); } catch {}
}

/** Bot API 7.10+ */
export function setBottomBarColor(color: string): void {
  try { wa()?.setBottomBarColor?.(color); } catch {}
}

// ============================
// Viewport & Safe Area
// ============================

export function getViewport(): ViewportInfo {
  const w = wa();
  return {
    height: w?.viewportHeight || (typeof window !== "undefined" ? window.innerHeight : 0),
    stableHeight: w?.viewportStableHeight || (typeof window !== "undefined" ? window.innerHeight : 0),
    isExpanded: w?.isExpanded || false,
  };
}

export function getSafeAreaInsets(): SafeAreaInsets {
  const inset = wa()?.safeAreaInset || {};
  return {
    top: inset.top || 0,
    bottom: inset.bottom || 0,
    left: inset.left || 0,
    right: inset.right || 0,
  };
}

export function getContentSafeAreaInsets(): SafeAreaInsets {
  const inset = wa()?.contentSafeAreaInset || {};
  return {
    top: inset.top || 0,
    bottom: inset.bottom || 0,
    left: inset.left || 0,
    right: inset.right || 0,
  };
}

// ============================
// Swipe control
// ============================

export function disableVerticalSwipes(): void {
  try { wa()?.disableVerticalSwipes(); } catch {}
}

export function enableVerticalSwipes(): void {
  try { wa()?.enableVerticalSwipes(); } catch {}
}

// ============================
// Closing confirmation
// ============================

export function enableClosingConfirmation(): void {
  try { wa()?.enableClosingConfirmation(); } catch {}
}

export function disableClosingConfirmation(): void {
  try { wa()?.disableClosingConfirmation(); } catch {}
}

// ============================
// Main Button (BottomButton)
// ============================

export function showMainButton(config: MainButtonConfig, onClick: () => void): () => void {
  const w = wa();
  if (!w?.MainButton) return () => {};

  const mb = w.MainButton;
  mb.setParams({
    text: config.text,
    color: config.color,
    text_color: config.textColor,
    is_active: config.isActive ?? true,
    is_visible: true,
    has_shine_effect: config.hasShineEffect ?? false,
  });
  mb.onClick(onClick);
  mb.show();

  return () => {
    mb.offClick(onClick);
    mb.hide();
  };
}

export function hideMainButton(): void {
  wa()?.MainButton?.hide();
}

export function setMainButtonLoading(loading: boolean): void {
  const mb = wa()?.MainButton;
  if (!mb) return;
  loading ? mb.showProgress(false) : mb.hideProgress();
}

export function setMainButtonText(text: string): void {
  wa()?.MainButton?.setText(text);
}

// ============================
// Secondary Button (Bot API 7.10+)
// ============================

export function showSecondaryButton(config: MainButtonConfig & { position?: "left" | "right" | "top" | "bottom" }, onClick: () => void): () => void {
  const w = wa();
  if (!w?.SecondaryButton) return () => {};

  const sb = w.SecondaryButton;
  sb.setParams({
    text: config.text,
    color: config.color,
    text_color: config.textColor,
    is_active: config.isActive ?? true,
    is_visible: true,
    position: config.position ?? "left",
  });
  sb.onClick(onClick);
  sb.show();

  return () => {
    sb.offClick(onClick);
    sb.hide();
  };
}

export function hideSecondaryButton(): void {
  wa()?.SecondaryButton?.hide();
}

// ============================
// Back Button
// ============================

export function showBackButton(onClick: () => void): () => void {
  const w = wa();
  if (!w?.BackButton) return () => {};

  w.BackButton.onClick(onClick);
  w.BackButton.show();

  return () => {
    w.BackButton.offClick(onClick);
    w.BackButton.hide();
  };
}

export function hideBackButton(): void {
  wa()?.BackButton?.hide();
}

// ============================
// Settings Button (Bot API 7.0+)
// ============================

export function showSettingsButton(onClick: () => void): () => void {
  const w = wa();
  if (!w?.SettingsButton) return () => {};

  w.SettingsButton.onClick(onClick);
  w.SettingsButton.show();

  return () => {
    w.SettingsButton.offClick(onClick);
    w.SettingsButton.hide();
  };
}

export function hideSettingsButton(): void {
  wa()?.SettingsButton?.hide();
}

// ============================
// Haptic Feedback
// ============================

export const haptic = {
  /** Light impact — button tap, toggle */
  light() { try { wa()?.HapticFeedback?.impactOccurred("light"); } catch {} },
  /** Medium impact — task complete, habit log */
  medium() { try { wa()?.HapticFeedback?.impactOccurred("medium"); } catch {} },
  /** Heavy impact — level up, achievement */
  heavy() { try { wa()?.HapticFeedback?.impactOccurred("heavy"); } catch {} },
  /** Rigid impact */
  rigid() { try { wa()?.HapticFeedback?.impactOccurred("rigid"); } catch {} },
  /** Soft impact */
  soft() { try { wa()?.HapticFeedback?.impactOccurred("soft"); } catch {} },
  /** Success notification */
  success() { try { wa()?.HapticFeedback?.notificationOccurred("success"); } catch {} },
  /** Warning notification */
  warning() { try { wa()?.HapticFeedback?.notificationOccurred("warning"); } catch {} },
  /** Error notification */
  error() { try { wa()?.HapticFeedback?.notificationOccurred("error"); } catch {} },
  /** Selection changed — scroll, pick */
  selectionChanged() { try { wa()?.HapticFeedback?.selectionChanged(); } catch {} },
};

// ============================
// Popups & Alerts
// ============================

export function showPopup(params: PopupParams): Promise<string | null> {
  return new Promise((resolve) => {
    const w = wa();
    if (!w?.showPopup) {
      resolve(window.confirm(params.message) ? "ok" : null);
      return;
    }
    w.showPopup(params, (id: string) => resolve(id || null));
  });
}

export function showAlert(message: string): Promise<void> {
  return new Promise((resolve) => {
    const w = wa();
    if (!w?.showAlert) { window.alert(message); resolve(); return; }
    w.showAlert(message, () => resolve());
  });
}

export function showConfirm(message: string): Promise<boolean> {
  return new Promise((resolve) => {
    const w = wa();
    if (!w?.showConfirm) { resolve(window.confirm(message)); return; }
    w.showConfirm(message, (ok: boolean) => resolve(ok));
  });
}

// ============================
// QR Scanner (Bot API 6.4+)
// ============================

export function showScanQrPopup(text?: string): Promise<string | null> {
  return new Promise((resolve) => {
    const w = wa();
    if (!w?.showScanQrPopup) { resolve(null); return; }
    w.showScanQrPopup({ text }, (data: string) => {
      w.closeScanQrPopup();
      resolve(data || null);
      return true; // close scanner
    });
  });
}

// ============================
// Links & Navigation
// ============================

/** Open URL in external browser */
export function openLink(url: string, tryInstantView = false): void {
  const w = wa();
  if (w?.openLink) {
    w.openLink(url, { try_instant_view: tryInstantView });
  } else {
    window.open(url, "_blank");
  }
}

/** Open Telegram deep link */
export function openTelegramLink(url: string): void {
  const w = wa();
  if (w?.openTelegramLink) {
    w.openTelegramLink(url);
  } else {
    window.open(url, "_blank");
  }
}

// ============================
// Payments (Bot API 6.1+)
// ============================

export function openInvoice(url: string): Promise<string> {
  return new Promise((resolve) => {
    const w = wa();
    if (!w?.openInvoice) { resolve("failed"); return; }
    w.openInvoice(url, (status: string) => resolve(status));
  });
}

// ============================
// Story sharing (Bot API 7.8+)
// ============================

export function shareToStory(mediaUrl: string, params?: { text?: string }): void {
  try { wa()?.shareToStory(mediaUrl, params); } catch {}
}

// ============================
// Data transmission
// ============================

/** Send data to bot — closes Mini App (keyboard button only) */
export function sendData(data: string): void {
  wa()?.sendData(data);
}

/** Switch inline query */
export function switchInlineQuery(query: string, chooseChatTypes?: string[]): void {
  try { wa()?.switchInlineQuery(query, chooseChatTypes); } catch {}
}

// ============================
// Clipboard (Bot API 6.4+)
// ============================

export function readClipboard(): Promise<string | null> {
  return new Promise((resolve) => {
    const w = wa();
    if (!w?.readTextFromClipboard) { resolve(null); return; }
    w.readTextFromClipboard((text: string | null) => resolve(text));
  });
}

// ============================
// Permissions
// ============================

export function requestWriteAccess(): Promise<boolean> {
  return new Promise((resolve) => {
    const w = wa();
    if (!w?.requestWriteAccess) { resolve(false); return; }
    w.requestWriteAccess((granted: boolean) => resolve(granted));
  });
}

export function requestContact(): Promise<boolean> {
  return new Promise((resolve) => {
    const w = wa();
    if (!w?.requestContact) { resolve(false); return; }
    w.requestContact((sent: boolean) => resolve(sent));
  });
}

// ============================
// Home Screen (Bot API 8.0+)
// ============================

export function addToHomeScreen(): void {
  try { wa()?.addToHomeScreen(); } catch {}
}

export function checkHomeScreenStatus(): Promise<string> {
  return new Promise((resolve) => {
    const w = wa();
    if (!w?.checkHomeScreenStatus) { resolve("unsupported"); return; }
    w.checkHomeScreenStatus((status: string) => resolve(status));
  });
}

// ============================
// Events
// ============================

type EventCallback = (...args: any[]) => void;

export function onEvent(event: string, callback: EventCallback): () => void {
  const w = wa();
  if (!w) return () => {};
  w.onEvent(event, callback);
  return () => w.offEvent(event, callback);
}

/** Shorthand event listeners */
export function onThemeChanged(cb: () => void) { return onEvent("themeChanged", cb); }
export function onViewportChanged(cb: (e: { isStateStable: boolean }) => void) { return onEvent("viewportChanged", cb); }
export function onMainButtonClicked(cb: () => void) { return onEvent("mainButtonClicked", cb); }
export function onBackButtonClicked(cb: () => void) { return onEvent("backButtonClicked", cb); }
export function onSettingsButtonClicked(cb: () => void) { return onEvent("settingsButtonClicked", cb); }
export function onInvoiceClosed(cb: (e: { url: string; status: string }) => void) { return onEvent("invoiceClosed", cb); }
export function onPopupClosed(cb: (e: { button_id: string | null }) => void) { return onEvent("popupClosed", cb); }
export function onFullscreenChanged(cb: () => void) { return onEvent("fullscreenChanged", cb); }
export function onSafeAreaChanged(cb: () => void) { return onEvent("safeAreaChanged", cb); }
export function onActivated(cb: () => void) { return onEvent("activated", cb); }
export function onDeactivated(cb: () => void) { return onEvent("deactivated", cb); }
