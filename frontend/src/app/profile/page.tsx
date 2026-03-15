"use client";

import { useAuth } from "@/contexts/AuthContext";
import { useEffect, useState } from "react";
import { getMySettings, updateMySettings, updateMe, getWallet, buyStreakFreeze } from "@/lib/api";
import type { UserSettingsResponse, WalletResponse } from "@/types";
import { Settings, Crown, Share2, Smartphone, ChevronRight, Clock, Moon, Globe, Bell, Shield, ShoppingCart } from "lucide-react";
import { addToHomeScreen, checkHomeScreenStatus, isTelegram, haptic, showAlert } from "@/lib/telegram";

const LEVEL_TITLES: Record<number, string> = {
  1: "Yangi boshlovchi", 5: "Beginner Planner", 10: "Rising Star",
  15: "Consistent Worker", 20: "Productivity Pro", 25: "Goal Crusher",
  30: "Deep Worker", 40: "Legendary Planner", 50: "Master of Productivity",
};

function getLevelTitle(level: number): string {
  const keys = Object.keys(LEVEL_TITLES).map(Number).sort((a, b) => b - a);
  for (const k of keys) if (level >= k) return LEVEL_TITLES[k];
  return "Yangi boshlovchi";
}

const TIME_OPTIONS = [
  "06:00", "06:30", "07:00", "07:30", "08:00", "08:30",
  "09:00", "09:30", "10:00", "10:30", "11:00",
  "18:00", "18:30", "19:00", "19:30", "20:00", "20:30",
  "21:00", "21:30", "22:00", "22:30", "23:00",
];

const TIMEZONES = [
  "UTC", "Asia/Tashkent", "Asia/Almaty", "Asia/Dubai",
  "Europe/Moscow", "Europe/London", "America/New_York",
];

export default function ProfilePage() {
  const { user, progress, refreshUser } = useAuth();
  const [settings, setSettings] = useState<UserSettingsResponse | null>(null);
  const [homeScreenStatus, setHomeScreenStatus] = useState<string>("unknown");
  const [wallet, setWallet] = useState<WalletResponse | null>(null);
  const [editField, setEditField] = useState<string | null>(null);
  const [buyingFreeze, setBuyingFreeze] = useState(false);

  useEffect(() => {
    getMySettings().then(setSettings).catch(() => {});
    getWallet().then(setWallet).catch(() => {});
    if (isTelegram()) {
      checkHomeScreenStatus().then(setHomeScreenStatus);
    }
  }, []);

  // Lock body when picker open
  useEffect(() => {
    if (editField) {
      document.body.style.overflow = "hidden";
    } else {
      document.body.style.overflow = "";
    }
    return () => { document.body.style.overflow = ""; };
  }, [editField]);

  async function handleAddToHome() {
    haptic.medium();
    addToHomeScreen();
    setTimeout(() => checkHomeScreenStatus().then(setHomeScreenStatus), 3000);
  }

  async function handleUpdateSetting(key: string, value: string) {
    haptic.light();
    try {
      const updated = await updateMySettings({ [key]: value });
      setSettings(updated);
      setEditField(null);
    } catch {
      haptic.error();
    }
  }

  async function handleUpdateTimezone(tz: string) {
    haptic.light();
    try {
      await updateMe({ timezone: tz });
      await refreshUser();
      setEditField(null);
    } catch {
      haptic.error();
    }
  }

  async function handleCopyReferral() {
    if (!user?.referral_code) return;
    haptic.light();
    const link = `https://t.me/planAIbot?start=ref_${user.referral_code}`;
    try {
      await navigator.clipboard.writeText(link);
      await showAlert("Referral link nusxalandi!");
    } catch {
      await showAlert(link);
    }
  }

  async function handleBuyFreeze() {
    setBuyingFreeze(true);
    haptic.medium();
    try {
      const result = await buyStreakFreeze();
      if (result.ok) {
        haptic.success();
        await showAlert(`Streak freeze olindi! (${result.freeze_tokens} ta mavjud)`);
        setWallet((prev) => prev ? { ...prev, balance: result.balance, freeze_tokens: result.freeze_tokens } : prev);
        await refreshUser();
      } else {
        haptic.error();
        await showAlert(result.error || "Xatolik");
      }
    } catch {
      haptic.error();
    } finally {
      setBuyingFreeze(false);
    }
  }

  const segmentLabels: Record<string, string> = {
    student: "🎓 Talaba", freelancer: "💻 Freelancer",
    entrepreneur: "🚀 Tadbirkor", developer: "👨‍💻 Dasturchi", other: "👤 Foydalanuvchi",
  };

  const level = progress?.current_level || 1;

  return (
    <div className="p-4 space-y-4">
      {/* Profile header */}
      <div className="bg-gray-900 rounded-xl p-5 text-center">
        <div className="w-20 h-20 bg-gradient-to-br from-blue-500 to-purple-600 rounded-full mx-auto mb-3 flex items-center justify-center">
          <span className="text-3xl font-bold">{user?.first_name?.[0] || "?"}</span>
        </div>
        <h1 className="text-lg font-bold">{user?.first_name} {user?.last_name || ""}</h1>
        {user?.username && (
          <p className="text-sm text-gray-400">@{user.username}</p>
        )}
        <p className="text-xs text-blue-400 mt-1">{getLevelTitle(level)}</p>
        <p className="text-xs text-gray-500">
          {segmentLabels[user?.segment || "other"]}
        </p>

        <div className="flex items-center justify-center gap-4 mt-4">
          <div className="text-center">
            <p className="text-lg font-bold text-blue-400">{level}</p>
            <p className="text-[10px] text-gray-500">Level</p>
          </div>
          <div className="w-px h-8 bg-gray-700" />
          <div className="text-center">
            <p className="text-lg font-bold text-yellow-400">{progress?.coins_balance || 0}</p>
            <p className="text-[10px] text-gray-500">Coinlar</p>
          </div>
          <div className="w-px h-8 bg-gray-700" />
          <div className="text-center">
            <p className="text-lg font-bold text-purple-400">{progress?.total_xp || 0}</p>
            <p className="text-[10px] text-gray-500">XP</p>
          </div>
        </div>
      </div>

      {/* Referral */}
      <button
        onClick={handleCopyReferral}
        className="w-full bg-gray-900 rounded-xl p-4 flex items-center gap-3 active:bg-gray-800 transition-colors"
      >
        <Share2 size={20} className="text-green-400 shrink-0" />
        <div className="flex-1 text-left">
          <p className="text-sm font-medium">Referral link</p>
          <p className="text-xs text-gray-500">Bosib nusxalash</p>
        </div>
        <p className="text-xs text-gray-400 font-mono">{user?.referral_code || "—"}</p>
      </button>

      {/* Streak Freeze Shop */}
      <div className="bg-gray-900 rounded-xl p-4">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-3">
            <Shield size={20} className="text-cyan-400" />
            <div>
              <p className="text-sm font-medium">Streak Freeze</p>
              <p className="text-xs text-gray-500">
                {wallet?.freeze_tokens || 0} ta mavjud
              </p>
            </div>
          </div>
          <button
            onClick={handleBuyFreeze}
            disabled={buyingFreeze || (progress?.coins_balance || 0) < 50}
            className="flex items-center gap-1.5 bg-yellow-600 px-3 py-1.5 rounded-lg text-xs font-medium hover:bg-yellow-500 active:scale-95 transition-all disabled:opacity-40 disabled:pointer-events-none"
          >
            <ShoppingCart size={12} />
            50 🪙
          </button>
        </div>
        <p className="text-[10px] text-gray-600 mt-2">
          Streak uzilganda 1 kun himoya qiladi
        </p>
      </div>

      {/* Settings */}
      <div className="bg-gray-900 rounded-xl overflow-hidden">
        <div className="p-4 pb-2">
          <h2 className="font-semibold flex items-center gap-2 text-sm">
            <Settings size={16} className="text-gray-400" />
            Sozlamalar
          </h2>
        </div>

        {/* Morning reminder */}
        <button
          onClick={() => setEditField("morning")}
          className="w-full flex items-center justify-between px-4 py-3 hover:bg-gray-800/50 transition-colors"
        >
          <div className="flex items-center gap-3">
            <Bell size={16} className="text-orange-400" />
            <span className="text-sm">Ertalabki eslatma</span>
          </div>
          <div className="flex items-center gap-1">
            <span className="text-sm text-gray-400">{settings?.morning_reminder_time?.slice(0, 5) || "08:00"}</span>
            <ChevronRight size={14} className="text-gray-600" />
          </div>
        </button>

        {/* Evening summary */}
        <button
          onClick={() => setEditField("evening")}
          className="w-full flex items-center justify-between px-4 py-3 hover:bg-gray-800/50 transition-colors"
        >
          <div className="flex items-center gap-3">
            <Moon size={16} className="text-blue-400" />
            <span className="text-sm">Kechki xulosa</span>
          </div>
          <div className="flex items-center gap-1">
            <span className="text-sm text-gray-400">{settings?.evening_reminder_time?.slice(0, 5) || "21:00"}</span>
            <ChevronRight size={14} className="text-gray-600" />
          </div>
        </button>

        {/* Theme */}
        <button
          onClick={() => setEditField("theme")}
          className="w-full flex items-center justify-between px-4 py-3 hover:bg-gray-800/50 transition-colors"
        >
          <div className="flex items-center gap-3">
            <Clock size={16} className="text-purple-400" />
            <span className="text-sm">Mavzu</span>
          </div>
          <div className="flex items-center gap-1">
            <span className="text-sm text-gray-400">{settings?.theme || "system"}</span>
            <ChevronRight size={14} className="text-gray-600" />
          </div>
        </button>

        {/* Timezone */}
        <button
          onClick={() => setEditField("timezone")}
          className="w-full flex items-center justify-between px-4 py-3 hover:bg-gray-800/50 transition-colors"
        >
          <div className="flex items-center gap-3">
            <Globe size={16} className="text-green-400" />
            <span className="text-sm">Timezone</span>
          </div>
          <div className="flex items-center gap-1">
            <span className="text-sm text-gray-400">{user?.timezone || "UTC"}</span>
            <ChevronRight size={14} className="text-gray-600" />
          </div>
        </button>
      </div>

      {/* Add to Home Screen */}
      {isTelegram() && homeScreenStatus !== "added" && (
        <button
          onClick={handleAddToHome}
          className="w-full bg-gradient-to-r from-blue-600 to-indigo-600 rounded-xl p-4 flex items-center gap-3 hover:opacity-90 active:opacity-80 transition-opacity"
        >
          <Smartphone size={24} />
          <div className="text-left flex-1">
            <p className="font-semibold text-sm">Asosiy ekranga qo'shish</p>
            <p className="text-xs text-blue-200">Ilova sifatida tez ochish</p>
          </div>
        </button>
      )}

      {isTelegram() && homeScreenStatus === "added" && (
        <div className="bg-gray-900 rounded-xl p-4 flex items-center gap-3">
          <Smartphone size={20} className="text-green-400" />
          <p className="text-sm text-gray-400">Asosiy ekranga qo'shilgan ✓</p>
        </div>
      )}

      {/* Premium */}
      <div className="bg-gradient-to-r from-yellow-900/30 to-orange-900/30 rounded-xl p-4 border border-yellow-800/30">
        <div className="flex items-center gap-3">
          <Crown size={24} className="text-yellow-400" />
          <div>
            <p className="font-semibold text-yellow-400">Premium</p>
            <p className="text-xs text-gray-400">Tez kunda...</p>
          </div>
        </div>
      </div>

      {/* Picker Modal */}
      {editField && (
        <div
          className="fixed inset-0 bg-black/60 z-[60] flex items-end"
          onClick={() => setEditField(null)}
        >
          <div
            className="w-full bg-gray-900 rounded-t-2xl p-5 animate-slide-up"
            onClick={(e) => e.stopPropagation()}
          >
            <h3 className="font-bold text-center mb-4">
              {editField === "morning" && "Ertalabki eslatma vaqti"}
              {editField === "evening" && "Kechki xulosa vaqti"}
              {editField === "theme" && "Mavzu tanlash"}
              {editField === "timezone" && "Timezone tanlash"}
            </h3>

            <div className="max-h-[50vh] overflow-y-auto overscroll-contain space-y-1">
              {editField === "morning" && TIME_OPTIONS.filter(t => t < "12:00").map((t) => (
                <button
                  key={t}
                  onClick={() => handleUpdateSetting("morning_reminder_time", t + ":00")}
                  className={`w-full p-3 rounded-xl text-sm text-left transition-colors ${
                    settings?.morning_reminder_time?.startsWith(t) ? "bg-blue-600" : "bg-gray-800 hover:bg-gray-700"
                  }`}
                >
                  {t}
                </button>
              ))}

              {editField === "evening" && TIME_OPTIONS.filter(t => t >= "18:00").map((t) => (
                <button
                  key={t}
                  onClick={() => handleUpdateSetting("evening_reminder_time", t + ":00")}
                  className={`w-full p-3 rounded-xl text-sm text-left transition-colors ${
                    settings?.evening_reminder_time?.startsWith(t) ? "bg-blue-600" : "bg-gray-800 hover:bg-gray-700"
                  }`}
                >
                  {t}
                </button>
              ))}

              {editField === "theme" && ["system", "dark", "light"].map((t) => (
                <button
                  key={t}
                  onClick={() => handleUpdateSetting("theme", t)}
                  className={`w-full p-3 rounded-xl text-sm text-left transition-colors ${
                    settings?.theme === t ? "bg-blue-600" : "bg-gray-800 hover:bg-gray-700"
                  }`}
                >
                  {t === "system" ? "🔄 Tizim" : t === "dark" ? "🌙 Qorong'i" : "☀️ Yorug'"}
                </button>
              ))}

              {editField === "timezone" && TIMEZONES.map((tz) => (
                <button
                  key={tz}
                  onClick={() => handleUpdateTimezone(tz)}
                  className={`w-full p-3 rounded-xl text-sm text-left transition-colors ${
                    user?.timezone === tz ? "bg-blue-600" : "bg-gray-800 hover:bg-gray-700"
                  }`}
                >
                  {tz}
                </button>
              ))}
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
