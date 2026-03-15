"use client";

import { useEffect, useCallback, useRef } from "react";
import {
  showMainButton,
  hideMainButton,
  setMainButtonLoading,
  showSecondaryButton,
  hideSecondaryButton,
  showBackButton,
  hideBackButton,
  showSettingsButton,
  hideSettingsButton,
  haptic,
  showPopup,
  showAlert,
  showConfirm,
  isTelegram,
  openLink,
  openTelegramLink,
  showScanQrPopup,
  readClipboard,
  type MainButtonConfig,
  type PopupParams,
} from "@/lib/telegram";

// ============================
// useMainButton
// ============================

/** Show Telegram MainButton while mounted. Auto-hides on unmount. */
export function useMainButton(
  config: MainButtonConfig | null,
  onClick: () => void,
) {
  const callbackRef = useRef(onClick);
  callbackRef.current = onClick;

  useEffect(() => {
    if (!config) { hideMainButton(); return; }
    return showMainButton(config, () => callbackRef.current());
  }, [config?.text, config?.isActive, config?.color, config?.hasShineEffect]);
}

// ============================
// useSecondaryButton (Bot API 7.10+)
// ============================

export function useSecondaryButton(
  config: (MainButtonConfig & { position?: "left" | "right" | "top" | "bottom" }) | null,
  onClick: () => void,
) {
  const callbackRef = useRef(onClick);
  callbackRef.current = onClick;

  useEffect(() => {
    if (!config) { hideSecondaryButton(); return; }
    return showSecondaryButton(config, () => callbackRef.current());
  }, [config?.text, config?.isActive, config?.color]);
}

// ============================
// useBackButton
// ============================

/** Show Telegram BackButton while mounted. Auto-hides on unmount. */
export function useBackButton(onClick: () => void) {
  const callbackRef = useRef(onClick);
  callbackRef.current = onClick;

  useEffect(() => {
    return showBackButton(() => callbackRef.current());
  }, []);
}

// ============================
// useSettingsButton (Bot API 7.0+)
// ============================

export function useSettingsButton(onClick: () => void) {
  const callbackRef = useRef(onClick);
  callbackRef.current = onClick;

  useEffect(() => {
    return showSettingsButton(() => callbackRef.current());
  }, []);
}

// ============================
// useMainButtonLoading
// ============================

export function useMainButtonLoading(loading: boolean) {
  useEffect(() => {
    setMainButtonLoading(loading);
  }, [loading]);
}

// ============================
// useHaptic
// ============================

export function useHaptic() {
  return haptic;
}

// ============================
// useTelegramPopup
// ============================

export function useTelegramPopup() {
  return {
    popup: useCallback((params: PopupParams) => showPopup(params), []),
    alert: useCallback((msg: string) => showAlert(msg), []),
    confirm: useCallback((msg: string) => showConfirm(msg), []),
  };
}

// ============================
// useIsTelegram
// ============================

export function useIsTelegram(): boolean {
  return isTelegram();
}

// ============================
// Utility hooks
// ============================

export function useTelegramLinks() {
  return {
    openLink: useCallback((url: string, instantView?: boolean) => openLink(url, instantView), []),
    openTelegramLink: useCallback((url: string) => openTelegramLink(url), []),
  };
}

export function useScanQr() {
  return useCallback((text?: string) => showScanQrPopup(text), []);
}

export function useClipboard() {
  return useCallback(() => readClipboard(), []);
}
